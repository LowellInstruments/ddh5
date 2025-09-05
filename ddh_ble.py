import datetime
import os
import pathlib
import shutil
import sys

from tzlocal import get_localzone
from uuid import uuid4
import json
import time
import signal
import setproctitle
import redis
from ble.ble import ble_scan_slow, disconnect
from ble.ble_linux import (
    ble_linux_get_bluez_version,
    ble_linux_is_antenna_up_n_running,
    ble_linux_detect_devices_left_connected_ll,
    ble_linux_disconnect_all, ble_linux_find_best_interface,
    ble_linux_get_type_of_interface, ble_linux_reset_antenna,
    ble_linux_disconnect_by_mac, ble_linux_is_mac_already_connected
)
from ddh.ble_dox import ble_download_dox
from ddh_gps import (
    ddh_gps_get_fix_upon_cold_boot,
    ddh_gps_know_we_are_using_dummy,
    ddh_gps_get_clock_sync_if_so, ddh_gps_get,
    ddh_app_check_operational_conditions
)
from ddh.ble_tdo import ble_download_tdo
from ddh.macs import (
    macs_color_show_at_boot, macs_black, macs_orange,
    add_mac_black, rm_mac_orange, add_mac_orange,
    rm_mac_black
)
from ddh.notifications_v2 import (
    notify_error_gps_clock_sync,
    notify_boot, notify_ddh_error_hw_ble, LoggerNotification,
    notify_logger_download, notify_logger_error_retries
)
from ddh.slo import slo_get_all, slo_add, slo_delete
from ddh.timecache import is_it_time_to
from ddh.tracking import ddh_log_tracking_add, get_path_current_track_file
from main_ddh import gui_add_to_history_database
from mat.utils import linux_is_rpi
from rd_ctt.ddh import *
from utils.ddh_common import (
    NAME_EXE_BLE,
    ddh_create_needed_folders,
    ddh_config_does_flag_file_download_test_mode_exist,
    ddh_config_get_list_of_monitored_macs,
    TMP_PATH_BLE_IFACE, app_state_set, EV_BLE_SCAN, STR_EV_BLE_SCAN, t_str, ael,
    ddh_config_get_logger_sn_from_mac, EV_BLE_DL_ERROR, EV_BLE_DL_RETRY,
    ddh_does_do_not_rerun_file_flag_exist, EV_BLE_DL_OK_NO_RERUN, EV_BLE_DL_OK,
    STR_EV_BLE_DL_OK, STR_EV_BLE_DL_OK_NO_RERUN, STR_EV_BLE_DL_NO_NEED,
    EV_BLE_DL_NO_NEED, EV_BLE_CONNECTING, STR_EV_BLE_CONNECTING,
    EV_GPS_SYNC_CLOCK, STR_EV_GPS_SYNC_CLOCK,
    EV_BLE_DL_PROGRESS, STR_EV_BLE_DL_PROGRESS,
    STR_EV_BLE_DL_RETRY, EV_GPS_HW_ERROR, STR_EV_GPS_HW_ERROR,
    EV_NO_ASSIGNED_LOGGERS,
    STR_NO_ASSIGNED_LOGGERS, ddh_this_process_needs_to_quit
)
from ddh_log import lg_ble as lg




# =====================================================
# ddh_ble
# downloads loggers
# updates redis with BLE antenna, last_dl and history
# =====================================================



r = redis.Redis('localhost', port=6379)
p_name = NAME_EXE_BLE
skip_1st_gps_notif = 1
using_dummy_gps = ddh_gps_know_we_are_using_dummy()
g_prev_ble = 0
g_ls_macs_mon = [i.upper() for i in ddh_config_get_list_of_monitored_macs()]
_g_logger_errors = {}
g_killed = False



def _cb_kill(n, _):
    print(f'{p_name}: captured signal kill', flush=True)
    global g_killed
    g_killed = True



def _cb_ctrl_c(n, _):
    print(f'{p_name}: captured signal ctrl + c', flush=True)
    global g_killed
    g_killed = True



def _check_bluez_version():
    v = ble_linux_get_bluez_version()
    if v != '5.66':
        lg.a(f"warning, bluez version {v} != 5.66")




def _ddh_ble_hardware_error_notify_via_email(g, antenna_idx, rv_error_ble_hw):

    if g and rv_error_ble_hw:
        e = f"error, ble_check_antenna_up_n_running #{antenna_idx}"
        if is_it_time_to(e, 600):
            lg.a(e)
            notify_ddh_error_hw_ble(g)




def _ddh_ble_hardware_describe_antenna_type():

    antenna_idx = ble_linux_find_best_interface()
    if antenna_idx != -1:
        antenna_desc = ble_linux_get_type_of_interface(antenna_idx)
    else:
        antenna_desc = 'error'

    # save to file which BLE interface we use, API needs it
    try:
        with open(TMP_PATH_BLE_IFACE, "w") as f:
            json.dump({"ble_iface_used": antenna_desc}, f)
    except (Exception, ) as ex:
        lg.a(f'error, saving {TMP_PATH_BLE_IFACE} -> {ex}')
    return antenna_idx, antenna_desc




def _ddh_ble_hardware_health_check(antenna_idx, rv_previous_run):

    brr = r.get(RD_DDH_BLE_RESET_REQ)
    aur = ble_linux_is_antenna_up_n_running(antenna_idx)
    nlc = ble_linux_detect_devices_left_connected_ll()
    need_hw_reset = brr or aur
    rv = 0

    if rv_previous_run or brr or nlc or aur:
        if rv_previous_run:
            lg.a("warning, last interaction had BLE error")
        if brr:
            # on scan errors + required by some BLE dongles
            lg.a("warning, detected ble_reset_req flag")
            r.delete(RD_DDH_BLE_RESET_REQ)
        if aur:
            lg.a(f"warning, hci{antenna_idx} is NOT up and running")
        if nlc:
            lg.a(f"warning, detected {nlc} devices left connected")
            rv = ble_linux_disconnect_all()
            if rv == 0:
                lg.a('OK, disconnected devices left connected gracefully')
            else:
                lg.a('error, could not disconnect devices left connected')
                need_hw_reset = 1


        if linux_is_rpi() and need_hw_reset:
            lg.a("warning, starting hci0 reset")
            ble_linux_reset_antenna(0)
            time.sleep(1)
            lg.a("warning, starting hci1 reset")
            ble_linux_reset_antenna(1)
            time.sleep(1)


        # linux BLE system health check: again
        aur = ble_linux_is_antenna_up_n_running(antenna_idx)
        if aur:
            lg.a('error, cannot get a good BLE antenna')
            rv = 1
            r.set(RD_DDH_BLE_ANTENNA, 'error')
        else:
            antenna_idx, antenna_description = _ddh_ble_hardware_describe_antenna_type()
            r.set(RD_DDH_BLE_ANTENNA, antenna_description)

    return rv



# def _ble_detect_hypoxia_after_download(f_lid, bat, g, u=''):
#     try:
#         if not f_lid.endswith('.lid') or not is_a_do2_file(f_lid):
#             return
#         f_csv = f_lid.replace('.lid', '_DissolvedOxygen.csv')
#         if not os.path.exists(f_csv):
#             return
#
#         # f_csv: 2404725_lab_20240407_230609.csv
#         sn = os.path.basename(f_csv).split('_')[0]
#         mac = ddh_get_cfg_logger_mac_from_sn(sn)
#         ln = LoggerNotification(mac, sn, 'DOX', bat)
#         ln.uuid_interaction = u
#         with open(f_csv, 'r') as f:
#             ll = f.readlines()
#             # headers: 'ISO 8601 Time,elapsed time (s),agg. time(s),Dissolved Oxygen (mg/l)...'
#             for i in ll[1:]:
#                 do_mg_l = float(i.split(',')[3])
#                 if do_mg_l <= 0.0:
#                     notify_logger_dox_hypoxia(g, ln)
#                     break
#     except (Exception, ) as ex:
#         lg.a(f'error: testing _ble_detect_hypoxia -> {ex}')






def _ble_logger_is_do1_or_do2(info: str):
    return "DO-" in info or info.startswith('DO2')




def _ble_logger_is_tdo(info: str):
    return "TDO" in info




def _ble_logger_is_moana(info: str):
    return "MOANA" in info




def _ble_logger_is_rn4020(mac, info):
    a = "00:1E:C0"
    if mac.startswith(a) or mac.startswith(a.lower()):
        return True
    if "MATP-2W" in info:
        return True



async def _ble_logger_id_and_download(d):

    # d: mutable dictionary to summarize interaction with logger
    mac = d['dev'].address
    name = d['dev'].name
    sn = ddh_config_get_logger_sn_from_mac(mac)
    rv = 0


    # first IDENTIFY, then DOWNLOAD
    try:
        if _ble_logger_is_tdo(name):
            lg.a(f'processing TDO logger SN {sn}')
            rv = await ble_download_tdo(d)

        elif _ble_logger_is_do1_or_do2(name):
            rv = await ble_download_dox(d)

        elif _ble_logger_is_moana(name):
            print('will do this someday, I am not in a hurry')
            #     fol = calculate_path_to_folder_within_dl_files_from_mac_address(mac)
            #     rv = await ble_interact_moana(fol, mac, hs, g)
            #     if rv == 2:
            #         # _u(STATE_DDH_BLE_ERROR_MOANA_PLUGIN)
            #         if is_it_time_to(f'tell_error_moana_plugin', 900):
            #             lg.a('error: no Moana plugin installed')
            #         time.sleep(5)
            #         # 0 because this is not a BLE interaction error
            #         return 0

        else:
            lg.a(f'error, cannot download UNKNOWN logger {name}, mac {mac}')

    except (Exception, ) as ex:
        lg.a(f'error, ble_id_and_download_logger -> {ex}')
        rv = 1
        await disconnect()
        ble_linux_disconnect_by_mac(mac)


    return rv




def _ddh_ble_boot_gps_clock_sync():

    if using_dummy_gps:
        lg.a("warning, dummy GPS, not syncing clock via GPS at boot")
        return

    if not linux_is_rpi():
        lg.a("upon boot, when developing, not syncing clock via GPS")
        return


    ddh_gps_get_fix_upon_cold_boot()
    app_state_set(EV_GPS_SYNC_CLOCK, t_str(STR_EV_GPS_SYNC_CLOCK))

    while 1:
        g = ddh_gps_get_clock_sync_if_so()
        if g:
            # e-mail notification got GPS fix at boot
            notify_boot(g)
            break

        # e-mail notification NOT get GPS fix at boot
        if is_it_time_to('report_gps_sync_boot_error', 3600 * 2):
            global skip_1st_gps_notif
            if skip_1st_gps_notif == 0:
                lg.a('error, cannot GPS sync at boot, sending notification')
                notify_error_gps_clock_sync()
            skip_1st_gps_notif = 0

        # now we are very fast checking GPS :)
        time.sleep(.1)




def _ddh_ble_scan_loggers(antenna_idx):

    adapter = f'hci{antenna_idx}'
    ls_devs_all = ael.run_until_complete(ble_scan_slow(adapter, timeout=5))


    # get all devices around (mac, name) and intersect with 'monitored' list
    ls_devs = [d for d in ls_devs_all if d.address in g_ls_macs_mon]
    if not ls_devs:
        return []
    ls_macs = [d.address for d in ls_devs]


    # prevent ignoring loggers that failed
    ls_macs_orange = [i.upper().replace('-', ':') for i in macs_orange()]
    for m in ls_macs_orange:
        slo_delete(m)


    # also get blacklisted macs
    ls_macs_black = [i.upper().replace('-', ':') for i in macs_black()]


    # first obtain the smart lock-out list, then update for next runs
    ls_macs_slo = slo_get_all()
    for m in ls_macs:
        if m in ls_macs_slo:
            slo_add(m)


    # proceed with macs not present in bad lists
    ls_macs_nope = list(set(ls_macs_black + ls_macs_orange + ls_macs_slo))
    ls_devs = [d for d in ls_devs if d.address not in ls_macs_nope]
    return ls_devs




def _ddh_ble_analyze_logger_download_result(d, rv):

    # small patch for our dashboard, ex: DO2_1234
    mac = d['dev'].address
    name = d['dev'].name
    name = 'DO-2' if name.split('_')[0] == 'DO2' else name


    # case no need to download because HBW command
    if rv == 2:
        app_state_set(EV_BLE_DL_NO_NEED, t_str(STR_EV_BLE_DL_NO_NEED))
        r.setex(RD_DDH_GUI_STATE_EVENT_ICON_LOCK, 5, 1)
        lg.a(f'OK, adding mac {mac} to black list')
        rm_mac_black(mac)
        rm_mac_orange(mac)
        add_mac_black(mac)
        lg.a(f'OK, adding mac {mac} to smart lock-out list')
        slo_add(mac)
        return


    # prepare e-mail notification
    sn = ddh_config_get_logger_sn_from_mac(mac)
    bat = d['battery_level']
    ln = LoggerNotification(mac, sn, name, bat)
    ln.uuid_interaction = d['uuid']
    ln.dl_files = d['dl_files']
    ln.gfv = d['gfv']


    # analyze success or failure
    gps_pos = d['gps_pos']
    if rv == 0:
        lg.a(f'OK, adding mac {mac} to black list')
        rm_mac_black(mac)
        rm_mac_orange(mac)
        add_mac_black(mac)
        lg.a(f'OK, adding mac {mac} to smart lock-out list')
        slo_add(mac)
        if mac in _g_logger_errors.keys():
            del _g_logger_errors[mac]
        lg.a(f"all done for logger {mac}/{sn}")
        notify_logger_download(gps_pos, ln)

        if ddh_does_do_not_rerun_file_flag_exist():
            lg.a("warning, telling this logger is not set for auto-re-run")
            app_state_set(EV_BLE_DL_OK_NO_RERUN, t_str(STR_EV_BLE_DL_OK_NO_RERUN) + f' {sn}')
        else:
            app_state_set(EV_BLE_DL_OK, t_str(STR_EV_BLE_DL_OK) + f' {sn}')
        r.setex(RD_DDH_GUI_STATE_EVENT_ICON_LOCK, 60, 1)


    # failure
    else:
        # not success, mild
        if mac not in _g_logger_errors:
            _g_logger_errors[mac] = 1
        else:
            _g_logger_errors[mac] += 1

        # not success, and the thing is serious
        if d['crit_error']:
            _g_logger_errors[mac] = 5

        rm_mac_black(mac)
        if _g_logger_errors[mac] >= 5:
            rm_mac_orange(mac)
            add_mac_black(mac)
            slo_add(mac)
            lg.a(f"error, logger {mac}/{sn} totally failed, critical")
            app_state_set(EV_BLE_DL_ERROR, d['error'])
            r.setex(RD_DDH_GUI_STATE_EVENT_ICON_LOCK, 60, 1)
            notify_logger_error_retries(gps_pos, ln)
            _g_logger_errors[mac] = 0

        else:
            lg.a(f"warning, logger {mac}/{sn} NOT done, adding to orange list")
            rm_mac_orange(mac)
            add_mac_orange(mac)
            slo_delete(mac)
            app_state_set(EV_BLE_DL_RETRY, t_str(STR_EV_BLE_DL_RETRY))
            r.setex(RD_DDH_GUI_STATE_EVENT_ICON_LOCK, 10, 1)



    # -------------------------------
    # GUI update HISTORY tab's table
    # -------------------------------
    lat, lon, dt, _ = gps_pos
    rerun = d['rerun']
    u = d['uuid']
    tz_ddh = get_localzone()
    tz_utc = datetime.timezone.utc
    dt_local = dt.replace(tzinfo=tz_utc).astimezone(tz=tz_ddh)
    ep_loc = int(dt_local.timestamp())
    ep_utc = int(dt.timestamp())
    e = 'ok' if not rv else f"error {d['error']}"
    gui_add_to_history_database(mac, e, lat, lon, ep_loc, ep_utc, rerun, u, name)
    r.set(RD_DDH_GUI_REFRESH_HISTORY_TABLE, 1)




def _ddh_ble_logger_id_and_download(gps_pos, dev, antenna_idx, antenna_desc):

    # know logger we work with
    mac = dev.address
    sn = ddh_config_get_logger_sn_from_mac(mac)


    # useful to get a summary to send notifications
    d_interaction = {
        'battery_level': 0xFFFF,
        'error': 'error comm.',
        'crit_error': 0,
        'dl_files': [],
        'rerun': False,
        'gfv':  '',
        'dev': dev,
        'gps_pos': gps_pos,
        'antenna_idx': antenna_idx,
        'antenna_desc': antenna_desc,
        'uuid': str(uuid4()),
    }


    # tell what we are doing to GUI
    app_state_set(EV_BLE_CONNECTING, t_str(STR_EV_BLE_CONNECTING) + f' to {sn}')
    lg.a(f'debug, connecting to {sn}')



    # --------------------------------------------
    # discover the type of logger and download it
    # --------------------------------------------
    try:
        r.setex(RD_DDH_BLE_SEMAPHORE, 120, 1)
        app_state_set(EV_BLE_DL_PROGRESS, t_str(STR_EV_BLE_DL_PROGRESS))
        r.setex(RD_DDH_GUI_STATE_EVENT_ICON_LOCK, 1, 1)
        rv = ael.run_until_complete(_ble_logger_id_and_download(d_interaction))
    except (Exception, ) as ex:
        lg.a(f"error, _ddh_ble_download_logger {mac} -> {ex}")
        rv = 1
    finally:
        r.delete(RD_DDH_BLE_SEMAPHORE)



    # some BLE dongles need a reset after download
    if antenna_desc == 'external' and linux_is_rpi():
        lg.a('warning, set planned BLE reset request on redis')
        r.set(RD_DDH_BLE_RESET_REQ, 1)



    # ----------------------
    # parse download result
    # ----------------------
    _ddh_ble_analyze_logger_download_result(d_interaction, rv)



    # ------------------------------------------------
    # enqueue binary data files by converted by CNV
    # ------------------------------------------------
    for p_dl in d_interaction['dl_files']:
        if p_dl.endswith('.lid'):
            bn = os.path.basename(p_dl)
            lg.a(f'post download push of {bn} to CNV queue')
            r.rpush(RD_DDH_CNV_QUEUE, p_dl)



    # ------------------------------------------------
    # enqueue files to AWS to it can upload-copy them
    # ------------------------------------------------
    ptf = get_path_current_track_file()
    bn = os.path.basename(ptf)
    lg.a(f'post download push of track file {bn} to AWS COPY queue')
    r.rpush(RD_DDH_AWS_COPY_QUEUE, ptf)
    for p_dl in d_interaction['dl_files']:
        bn = os.path.basename(p_dl)
        lg.a(f'post download push of file {bn} to AWS COPY queue')
        r.rpush(RD_DDH_AWS_COPY_QUEUE, p_dl)

    return rv




def _ddh_ble(ignore_gui):

    setproctitle.setproctitle(p_name)
    print(f"BLE: process '{p_name}' is running")
    _check_bluez_version()
    ddh_create_needed_folders()
    macs_color_show_at_boot()
    if ddh_config_does_flag_file_download_test_mode_exist():
        lg.a('detected DDH download test mode')


    # know your BLE antenna
    antenna_idx, antenna_s = _ddh_ble_hardware_describe_antenna_type()
    lg.a(f"using BLE antenna hci{antenna_idx}, type {antenna_s}")
    r.set(RD_DDH_BLE_ANTENNA, antenna_s)


    # know your GPS antenna

    _ddh_ble_boot_gps_clock_sync()



    # forever loop downloading loggers
    rv_prev_run = 0
    while 1:

        if ddh_this_process_needs_to_quit(ignore_gui, p_name, g_killed):
            sys.exit(0)


        # not hag cpu
        time.sleep(1)


        # case: forgot to assign loggers
        if not g_ls_macs_mon:
            app_state_set(EV_NO_ASSIGNED_LOGGERS, t_str(STR_NO_ASSIGNED_LOGGERS))
            continue


        # get a gps fix from redis
        g = ddh_gps_get()
        # lg.a(f'debug: g = {g}')
        if not g:
            app_state_set(EV_GPS_HW_ERROR, t_str(STR_EV_GPS_HW_ERROR))
            r.setex(RD_DDH_GUI_STATE_EVENT_ICON_LOCK, 3, 1)
            continue


        # populate your tracking file
        lat, lon, tg, speed_knots = g
        ddh_log_tracking_add(lat, lon, tg)



        # GPS clock sync from time to time
        if is_it_time_to('ble_gps_periodic_clock_sync', 86400):
            if not ignore_gui:
                ddh_gps_get_clock_sync_if_so()



        # see the rest non-GPSy APP conditions are OK
        if not ddh_app_check_operational_conditions(g):
            continue


        # see BLE system OK
        rv_ble_hw = _ddh_ble_hardware_health_check(antenna_idx, rv_prev_run)
        _ddh_ble_hardware_error_notify_via_email(g, antenna_idx, rv_ble_hw)
        if rv_ble_hw:
            continue


        # -------------
        # find loggers
        # -------------
        try:
            app_state_set(EV_BLE_SCAN, t_str(STR_EV_BLE_SCAN))
            ls = _ddh_ble_scan_loggers(antenna_idx)
            if not ls:
                continue
            lg.a(f'list of loggers to download')
            lg.a(f'\t{ls}')
        except (Exception, ) as ex:
            lg.a(f'error during _scan_loggers() -> {ex}')
            continue


        # ----------------------
        # download such loggers
        # ----------------------

        dev = ls[0]
        rv_prev_run = _ddh_ble_logger_id_and_download(g, dev, antenna_idx, antenna_s)




def main_ddh_ble(ignore_gui=False):

    signal.signal(signal.SIGINT, _cb_ctrl_c)
    signal.signal(signal.SIGTERM, _cb_kill)

    while 1:
        try:
            _ddh_ble(ignore_gui)
        except (Exception, ) as ex:
            lg.a(f"BLE: error, process '{p_name}' restarting after crash -> {ex}")




if __name__ == '__main__':

    # normal run
    main_ddh_ble(ignore_gui=False)

    # for debug on pycharm
    # main_ddh_ble(ignore_gui=True)
