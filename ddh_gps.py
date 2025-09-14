import signal
import sys

import setproctitle
from tzlocal import get_localzone
from gps.gps_adafruit import gps_adafruit_init
from gps.gps_puck import gps_puck_detect_usb_port
from gps.gps_quectel import gps_hat_get_firmware_version, gps_hat_init
from rd_ctt.ddh import *
from gps.gps import (
    gps_find_any_usb_port,
    gps_hardware_read,
    gps_parse_sentence_type_rmc, gps_parse_sentence_type_gga
)
from gpiozero import LED
from ddh.notifications_v2 import (
    notify_ddh_number_of_gps_satellites, notify_ddh_error_hw_gps,
)
from rd_ctt.ddh import RD_DDH_GPS_HAT_GFV, RD_DDH_GPS_FIX_POSITION, RD_DDH_GPS_FIX_SPEED
from utils.ddh_common import (
    NAME_EXE_GPS, ddh_config_is_gps_error_forced_enabled, LI_PATH_GPS_DUMMY,
    LI_PATH_CELL_FW, EV_GPS_WAITING_BOOT, app_state_set, t_str,
    EV_GPS_IN_PORT,
    STR_EV_GPS_IN_PORT, STR_EV_BLE_SCAN_2, EV_BLE_SCAN, ddh_this_process_needs_to_quit, TMP_PATH_GPS_LAST_JSON
)
import datetime
import json
from ddh.timecache import is_it_time_to
from mat.utils import linux_is_rpi, linux_set_datetime
from ddh_log import lg_gps as lg
import os
import redis
import time
from ddh.in_ports_geo import ddh_ask_in_port_to_ddn
from utils.ddh_common import (
    ddh_get_path_to_app_override_flag_file,
    ddh_config_get_gear_type, \
    ddh_config_get_speed_considered_as_trawling,
    ddh_config_get_list_of_monitored_macs, \
)
from ddh_log import lg_ble as lg



# ============================================
# ddh_gps
# writes to redis GPS FIX, SPEED and NUM. SAT
# and type of GPS antenna
# ============================================





r = redis.Redis('localhost', port=6379)
PERIOD_GPS_AT_BOOT_SECS = 600 if linux_is_rpi() else 10
PERIOD_GPS_NOTI_NUM_GPS_SAT = 1800
p_name = NAME_EXE_GPS
_skip_satellite_notification = 1
using_dummy_gps = os.path.exists(LI_PATH_GPS_DUMMY)
app_gear_type = ddh_config_get_gear_type()
s_lo, s_hi = ddh_config_get_speed_considered_as_trawling()
s_lo = float(s_lo)
s_hi = float(s_hi)
g_ls_macs_mon = ddh_config_get_list_of_monitored_macs()
g_killed = False



def _cb_kill(n, _):
    print(f'{p_name}: captured signal kill', flush=True)
    global g_killed
    g_killed = True



def _cb_ctrl_c(n, _):
    print(f'{p_name}: captured signal ctrl + c', flush=True)
    global g_killed
    g_killed = True



def ddh_gps_know_we_are_using_dummy():
    return using_dummy_gps



def ddh_gps_know_we_have_external_puck_connected():
    return gps_puck_detect_usb_port()



def ddh_gps_hat_power_cycle():
    # # _u(STATE_DDH_GPS_POWER_CYCLE)
    t = 75
    lg.a(f"=== warning, power-cycling hat, wait ~{t} seconds ===")

    # GPIO26 controls the sixfab hat power rail
    # on() means high-level, shutdowns power to hat
    # off() means low-level, restores power to hat
    _pin = LED(26)
    _pin.on()
    time.sleep(5)
    _pin.off()
    time.sleep(t)
    lg.a("=== warning, power-cycling done, hat should be ON by now ===")




def ddh_app_check_operational_conditions(gps_pos):

    if not gps_pos:
        return False


    # -----------------------------------------------------
    # we can download when:
    # GPS
    #       + speed conditions
    #       + mac not in black list
    #       + mac not in orange list
    #       + mac not in smart lock-out
    # or GPS
    #       + forced flag, which clears all the previous
    # -----------------------------------------------------


    # forced flag, when user presses button '2' for example
    forced_flag = ddh_get_path_to_app_override_flag_file()
    if os.path.exists(forced_flag):
        lg.a('debug, detected application override flag')
        os.unlink(forced_flag)
        ls_slo_keys = r.keys(RD_DDH_SLO_LS + '*')
        for k in ls_slo_keys:
            r.delete(k.decode())
            return True


    # are we in port
    are_we_in_port = ddh_ask_in_port_to_ddn(gps_pos)
    if are_we_in_port:
        app_state_set(EV_GPS_IN_PORT, t_str(STR_EV_GPS_IN_PORT))
        r.setex(RD_DDH_GUI_STATE_EVENT_ICON_LOCK, 10, 1)
        return False


    # check type of DDH application is mobile and we out of speed range
    lat, lon, tg, speed_knots = gps_pos
    speed_knots = float(speed_knots)
    if app_gear_type == 1 and not (s_lo <= speed_knots <= s_hi):
        app_state_set(EV_BLE_SCAN, t_str(STR_EV_BLE_SCAN_2))
        return False

    return True




# ========================
# GPS CONSUMER section
# ========================



# gets from redis as a dict and returns as a tuple
def _ddh_gps_get():

    # hooks
    if ddh_config_is_gps_error_forced_enabled():
        lg.a("debug, HOOK_GPS_ERROR_MEASUREMENT_FORCED")
        time.sleep(1)
        return None


    # get from redis the number of satellites notification
    ns = r.get(RD_DDH_GPS_FIX_NUMBER_OF_SATELLITES)
    ns = int(ns.decode()) if ns else 0
    global _skip_satellite_notification
    if 0 < ns <= 6 and is_it_time_to('SQS_gps_num_satellites', PERIOD_GPS_NOTI_NUM_GPS_SAT):
        if _skip_satellite_notification:
            _skip_satellite_notification = 0
        else:
            notify_ddh_number_of_gps_satellites(ns)


    # get from redis the GPS fix
    g = r.get(RD_DDH_GPS_FIX_POSITION)
    if g:
        d = json.loads(g)
        # dt: "2025-07-31T18:16:10Z"
        dt = datetime.datetime.strptime(
            d['dt'],
            '%Y-%m-%dT%H:%M:%SZ')
        speed = '0'
        if r.exists(RD_DDH_GPS_FIX_SPEED):
            speed = r.get(RD_DDH_GPS_FIX_SPEED).decode()
        lat = "{:+.6f}".format(float(d['lat']))
        lon = "{:+.6f}".format(float(d['lon']))


        # this is extra for API
        try:
            d = {
                "lat": lat,
                "lon": lon,
                "gps_time": str(d['dt']),
                "speed": speed
            }
            with open(TMP_PATH_GPS_LAST_JSON, "w") as f:
                json.dump(d, f)
        except (Exception,) as ex:
            lg.a(f'error: saving {TMP_PATH_GPS_LAST_JSON} -> {ex}')
        return lat, lon, dt, speed


    return None




def ddh_gps_get():
    try:
        return _ddh_gps_get()
    except (Exception,) as ex:
        lg.a(f"error, ddh_gps_get() -> {ex}")



def ddh_gps_get_clock_sync_if_so():

    g = ddh_gps_get()
    if not g:
        return None


    # sync local clock with GPS frame
    z_utc = datetime.timezone.utc
    dt_gps_utc = g[2].replace(tzinfo=z_utc)
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    diff_secs = abs((dt_gps_utc - utc_now).total_seconds())
    if diff_secs < 60:
        return g
    lg.a(f"warning, the difference between UTC and local time was = {diff_secs} seconds")
    z_my = get_localzone()
    dt_my = dt_gps_utc.astimezone(tz=z_my)
    t = str(dt_my)[:-6]


    # don't GPS clock sync when developing
    if not linux_is_rpi():
        return g


    if linux_set_datetime(t):
        return g

    return None



def ddh_gps_get_hat_firmware_version():
    if using_dummy_gps:
        return 'dummy_gps'
    gfv = r.get(RD_DDH_GPS_HAT_GFV)
    with open(LI_PATH_CELL_FW, 'w') as f:
        # gfv: EG25GGBR07A08M2GMay 18 2022 20:48:14Authors: QCT
        f.write(gfv)
    return gfv




def ddh_gps_get_fix_upon_cold_boot():

    # Wikipedia: GPS-Time-To-First-Fix for cold start is typ.
    # 2 to 5 minutes, warm <= 45 secs, hot <= 22 secs

    r.set(RD_DDH_GPS_COUNTDOWN_FOR_FIX_AT_BOOT, 1)
    r.expire(RD_DDH_GPS_COUNTDOWN_FOR_FIX_AT_BOOT, PERIOD_GPS_AT_BOOT_SECS)
    app_state_set(EV_GPS_WAITING_BOOT, 'GPS boot')
    lg.a(f"boot, wait up to {PERIOD_GPS_AT_BOOT_SECS} seconds")
    till = time.perf_counter() + PERIOD_GPS_AT_BOOT_SECS

    while time.perf_counter() < till:
        t_left = int(till - time.perf_counter())
        g = ddh_gps_get()
        if g:
            lg.a(f"OK, cold boot, got first gps fix")
            return
        lg.a(f"{t_left} seconds remaining GPS at boot")
        time.sleep(1)

    lg.a("warning, cold boot, did NOT get GPS lock")





# =====================
# GPS PRODUCER section
# =====================

def _set_redis_gps_number_of_satellites(d):
    if d and 'ns' in d.keys():
        r.set(RD_DDH_GPS_FIX_NUMBER_OF_SATELLITES, d['ns'])
        r.expire(RD_DDH_GPS_FIX_NUMBER_OF_SATELLITES, 60)



def _set_redis_gps_fix_dict(d: dict):
    if d and d['lat'] and d['lon'] and d['dt']:
        # {
        #     "ok": false,
        #     "type": "$GPGGA",
        #     "lat": "0.0000",
        #     "lon": "0.0000",
        #     "dt": "2025-07-29T18:40:28Z",
        #     "sentence": "$GPGGA,184028.163,,,,,0,00,,,M,0.0,M,,0000*55"
        # }
        j = json.dumps(d)
        r.set(RD_DDH_GPS_FIX_POSITION, j)
        r.expire(RD_DDH_GPS_FIX_POSITION, 5)
    else:
        lg.a(f"warning, _send_dict_to_redis discarded sentence {d['sentence']}")



def _set_redis_gps_speed(d: dict):
    if d and 'speed' in d.keys():
        s = d['speed']
        r.set(RD_DDH_GPS_FIX_SPEED, s)
        r.expire(RD_DDH_GPS_FIX_SPEED, 2)



def _ddh_gps(ignore_gui):

    # prepare GPS process
    r.delete(RD_DDH_GPS_ANTENNA)
    setproctitle.setproctitle(p_name)


    # find USB ports for GPS
    port_nmea, port_ctrl, port_type = gps_find_any_usb_port()
    ant_type = 'external' if port_type in ('puck', 'adafruit') else 'internal'
    baud_rate = 115200 if port_type in ('hat', 'adafruit') else 4800


    # set to redis the type of GPS antenna
    if using_dummy_gps:
        lg.a(f'using dummy')
        r.set(RD_DDH_GPS_ANTENNA, 'dummy')
    elif port_type:
        lg.a(f'using type {port_type.upper()} on NMEA port {port_nmea}')
        r.set(RD_DDH_GPS_ANTENNA, ant_type)
    else:
        # None
        lg.a(f'error, we have no GPS at all, not even dummy')
        r.delete(RD_DDH_GPS_ANTENNA)
        time.sleep(5)


    # additional initialization of GPS
    if port_ctrl:
        gfv, gfm = gps_hat_get_firmware_version(port_ctrl)
        gfv = gfv.replace(b'AT+CVERSION\r', b'').decode()
        lg.a(f'hat firmware version is {gfv}')
        r.set(RD_DDH_GPS_HAT_GFV, gfv)

        lg.a(f'activating hat\'s NMEA on {port_nmea} by write to ctrl port {port_ctrl}')
        rv = gps_hat_init(port_ctrl)
        if rv:
            lg.a('OK activate hat NMEA stream')
            r.set(RD_DDH_GPS_ANTENNA, 'internal')
        else:
            lg.a('error activate hat NMEA stream ')

    else:
        # not hat, can still be puck or adafruit
        if port_type == 'adafruit':
            gps_adafruit_init(port_nmea)


    # GPS infinite loop
    while 1:

        if ddh_this_process_needs_to_quit(ignore_gui, p_name, g_killed):
            sys.exit(0)


        # get bytes from hardware USB port
        d = dict()
        if using_dummy_gps:
            time.sleep(1)
            bb_g = b'$GPGGA,134658.00,5106.9792,N,11402.3003,W,2,09,1.0,1048.47,M,-16.27,M,08,AAAA*60'
        else:
            gps_hardware_read(port_nmea, baud_rate, d, debug=False)
            bb_g = d['bb']

        if not bb_g:
            # todo: test this
            # see if GPS is doing OK
            rv = 'error_gps' in d.keys()
            k = RD_DDH_GPS_ERROR_NUMBER
            if rv:
                r.setex(f'{k}_{int(time.time())}', 60, 1)
            _it = r.scan_iter(f'{k}_*', count=20)
            ls = list(_it)
            if len(ls) >= 10:
                notify_ddh_error_hw_gps()
            if rv == 0 or len(ls) >= 10:
                for i in ls:
                    r.delete(i)
            continue


        # record number of satellites
        _set_redis_gps_number_of_satellites(d)


        # try to build friendly GPS dictionary
        d_rmc = gps_parse_sentence_type_rmc(bb_g)
        d_gga = gps_parse_sentence_type_gga(bb_g)
        if d_rmc:
            _set_redis_gps_fix_dict(d_rmc)
            _set_redis_gps_speed(d_rmc)
        else:
            if d_gga:
                _set_redis_gps_fix_dict(d_gga)



def main_ddh_gps(ignore_gui=False):
    signal.signal(signal.SIGINT, _cb_ctrl_c)
    signal.signal(signal.SIGTERM, _cb_kill)

    while 1:
        try:
            _ddh_gps(ignore_gui)
        except (Exception, ) as ex:
            lg.a(f'error, process {p_name} restarting after crash -> {ex}')




if __name__ == '__main__':

    # normal run
    main_ddh_gps(ignore_gui=False)

    # for debug on pycharm
    # main_ddh_gps(ignore_gui=True)
