import asyncio
import os
import toml
from ble.ble_oop import LoggerBle
from ddh.lef import lef_create_file
from ddh.notifications_v2 import (
    LoggerNotification,
    notify_logger_error_low_battery,
    notify_logger_error_sensor_pressure
)
from lix.lix import ph16temp_to_float, ph16acid_to_float
from utils.ddh_common import (
    ddh_config_get_logger_sn_from_mac,
    create_path_to_folder_dl_files_from_mac,
    ddh_ble_logger_needs_a_reset,
    ddh_get_template_of_path_of_hbw_flag_file,
    ddh_get_path_to_folder_scripts,
    EV_BLE_LOW_BATTERY,
    STR_EV_BLE_LOW_BATTERY,
    app_state_set,
    t_str,
    ddh_does_do_not_rerun_file_flag_exist,
    TESTMODE_FILENAME_PREFIX,
    calculate_path_to_folder_within_dl_files_from_mac_address,
    ddh_config_does_flag_file_download_test_mode_exist,
    exp_get_skip_hbw, linux_is_rpi,
)
from ddh_log import lg_ble as lg
from utils.redis import RD_DDH_BLE_PREVENT_FULL_QUERY



lc = LoggerBle()
g_debug_not_delete_files = False
BAT_FACTOR_PH = 0.4545
MIN_VERSION_HBW_CMD = "4.2.21"



class BLEAppException(Exception):
    pass



def _rae(rv, s):
    if rv:
        raise BLEAppException("PH interact " + s)



def _une(rv, d, e, ce=0):
    # ude: update dictionary error
    if rv:
        d["error"] = "error " + str(e)
        d["crit_error"] = int(ce)




async def ble_download_ph(d, full_query=False):

    # d: {'battery_level': 65535,
    #     'error': 'error comm.',
    #     'crit_error': 0,
    #     'dl_files': [],
    #     'rerun': False,
    #     'gfv': '',
    #     'dev': BLEDevice(D0:2E:AB:D9:29:48, PH_AAA),
    #     'gps_pos': ('+41.610100', '-70.609300', datetime.datetime(2025, 8, 8, 15, 12, 29), '0'),
    #     'antenna_idx': 0,
    #     'antenna_desc': 'internal',
    #     'uuid': '9d8f50cd-0b08-467e-ab98-c62bae39fc96'}

    dev = d['dev']
    mac = dev.address
    g = d['gps_pos']
    sn = ddh_config_get_logger_sn_from_mac(mac)
    create_path_to_folder_dl_files_from_mac(mac)


    rv = await lc.ble_connect_by_dev(dev)
    _une(not rv, d, "comm.")
    _rae(not rv, "connecting")
    lg.a(f"connected to {mac}")

    if full_query:
        lg.a(f'OK, PH download full query ON')
    else:
        lg.a(f'note, PH download full query OFF')



    if ddh_ble_logger_needs_a_reset(mac):
        lg.a(f"warning, logger reset file {mac} found, deleting it")
        await lc.cmd_rst()
        # out of here for sure
        raise BLEAppException("PH interact logger reset file")



    rv, gci_ms = await lc.cmd_gci()
    if rv == 0:
        lg.a(f"GCI | {gci_ms} ms")



    rv, v = await lc.cmd_gfv()
    _rae(rv, "gfv")
    lg.a(f"GFV | {v}")
    d['gfv'] = v
    

    rv, state = await lc.cmd_sts()
    _rae(rv, "sts")
    lg.a(f"STS | logger was {state}")



    # feature has-logger-been-in-water
    flag_ignore_hbw = ddh_get_template_of_path_of_hbw_flag_file().format(mac)
    if exp_get_skip_hbw() != 1:
        if state == 'running':
            if v >= MIN_VERSION_HBW_CMD:
                if os.path.exists(flag_ignore_hbw):
                    os.unlink(flag_ignore_hbw)
                    lg.a('file flag to override HBW exists, FORCE download it')
                else:
                    # normal HBW command
                    lg.a('sending command Has-Been-in-Water')
                    rv, v = await lc.cmd_hbw()
                    if rv:
                        lg.a('note, command Has-Been-in-Water failed, consider it has')
                        v = 1
                    lg.a(f"HBW | {v}")
                    if v == 0:
                        lg.a('logger has NOT been in water, no need to download it')
                        await lc.ble_disconnect()
                        return 2
                    lg.a("logger has been in water, we download it")
        else:
            lg.a('logger NOT running, not sending HBW command')
    else:
        lg.a("warning, not sending HBW command, disabled in configuration file")



    rv = await lc.cmd_sws(g)
    _rae(rv, "sws")
    lg.a("SWS | OK")



    if full_query:
        rv, t = await lc.cmd_utm()
        _rae(rv, "utm")
        lg.a(f"UTM | {t}")


    rv, b = await lc.cmd_bat()
    _rae(rv, "bat")
    adc_b = b
    b /= BAT_FACTOR_PH
    lg.a(f"BAT | ADC {adc_b} mV -> battery {int(b)} mV")
    d["battery_level"] = b
    if adc_b < 982:
        ln = LoggerNotification(mac, sn, 'PH1', adc_b)
        notify_logger_error_low_battery(g, ln)
        app_state_set(EV_BLE_LOW_BATTERY, t_str(STR_EV_BLE_LOW_BATTERY))
        d['error'] = 'low battery'
        rv_bad_bat = 1
        _une(rv_bad_bat, d, "BAT_low_error", ce=1)
        lg.a(f'BAT | error {rv_bad_bat}')
        _rae(rv_bad_bat, "bat")


    rv, v = await lc.cmd_gtm()
    _rae(rv, "gtm")
    lg.a(f"GTM | {v}")


    rv = await lc.cmd_stm()
    _rae(rv, "stm")
    lg.a("STM | OK")


    # disable log for lower power consumption
    if full_query:
        rv, v = await lc.cmd_log()
        _rae(rv, "log")
        if linux_is_rpi():
            if v != 0:
                rv, v = await lc.cmd_log()
                _rae(rv, "log")
        else:
            # we WANT logs ON while developing
            if v != 1:
                rv, v = await lc.cmd_log()
                _rae(rv, "log")



    rv, ls = await lc.cmd_dir()
    _rae(rv, "dir error " + str(rv))
    lg.a(f"DIR | {ls}")



    # iterate files present in logger
    for name, size in ls.items():

        # delete zero-bytes files
        if size == 0:
            rv = await lc.cmd_del(name)
            _rae(rv, "del")
            continue


        # target file to download
        lg.a(f"downloading file {name}")
        rv = await lc.cmd_dwg(name)
        _rae(rv, "dwg")


        # download file
        rv, file_data = await lc.cmd_dwl(int(size))
        _rae(rv, "dwl")
        lg.a(f"OK downloaded file {name}")


        # save file in our local disk
        del_name = name
        if ddh_config_does_flag_file_download_test_mode_exist():
            name = TESTMODE_FILENAME_PREFIX + name
        path = str(calculate_path_to_folder_within_dl_files_from_mac_address(mac) / name)
        with open(path, "wb") as f:
            f.write(file_data)


        # add to the output list
        d['dl_files'].append(path)

        # delete file in logger
        rv = await lc.cmd_del(del_name)
        _rae(rv, "del")
        lg.a(f"deleted file {del_name}")


        # create LEF file with download info
        lg.a(f"creating file LEF for {name}")
        if name.endswith('.lid'):
            lef_create_file(g, name)



    # format file-system
    await asyncio.sleep(.5)
    rv = await lc.cmd_frm()
    _rae(rv, "frm")
    lg.a("FRM | OK")



    # check sensor pH
    rv = await lc.cmd_gph()
    bad_rv = (not rv or (rv[0] == 1 or b'0000' in rv[1] or b'9999' in rv[1]))
    if bad_rv:
        lg.a(f'GPH | error {rv}')
        d['error'] = 'sensor PH'
        _une(bad_rv, d, "PH_sensor_error", ce=1)
    _rae(bad_rv, "gph")


    # b'12' to 0x12
    hex_temp = int(rv[1][:2], 16) << 8
    hex_temp += int(rv[1][2:4], 16) << 0
    hex_ph = int(rv[1][4:6], 16) << 8
    hex_ph += int(rv[1][6:8], 16) << 0
    temp = ph16temp_to_float(hex_temp)
    ph = ph16acid_to_float(hex_ph)


    # only two decimals
    temp = '{:.2f}'.format(temp)
    ph = '{:.2f}'.format(ph)
    lg.a(f'measurements pH = {ph}, temperature = {temp} °')


    # wake mode
    rerun_flag = not ddh_does_do_not_rerun_file_flag_exist()
    w = "on" if rerun_flag else "off"
    rv = await lc.cmd_wak(w)
    _rae(rv, "wak")
    lg.a(f"WAK | {w} OK")


    # re-run the logger or not
    d['rerun'] = rerun_flag
    if rerun_flag:
        rv = await lc.cmd_rws(g)
        if rv:
            d['error'] = 'running'
        _rae(rv, "rws")
        lg.a("RWS | OK")


    await lc.ble_disconnect()
    return 0
