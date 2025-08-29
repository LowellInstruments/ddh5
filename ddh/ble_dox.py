import json
import os
import toml
from ble.ble import *
from ddh.lef import lef_create_file
from ddh.notifications_v2 import (
    LoggerNotification, notify_logger_error_low_battery,
    notify_logger_error_sensor_pressure, notify_logger_error_sensor_oxygen
)
from mat.utils import linux_is_rpi
from utils.ddh_common import (
    ddh_config_get_logger_sn_from_mac,
    create_path_to_folder_dl_files_from_mac,
    ddh_ble_logger_needs_a_reset,
    ddh_get_template_of_path_of_hbw_flag_file,
    ddh_get_path_to_folder_scripts, EV_BLE_LOW_BATTERY,
    STR_EV_BLE_LOW_BATTERY, app_state_set, t_str,
    ddh_does_do_not_rerun_file_flag_exist, EV_BLE_DL_ERROR,
    TESTMODE_FILENAME_PREFIX,
    calculate_path_to_folder_within_dl_files_from_mac_address,
    ddh_config_does_flag_file_download_test_mode_exist, exp_get_conf_dox,
)
from ddh_log import lg_ble as lg



MC_FILE = "MAT.cfg"
g_debug_not_delete_files = False
BAT_FACTOR_DOT = 0.4545
MIN_VERSION_HBW_CMD = "4.2.21"



class BLEAppException(Exception):
    pass



def _rae(rv, s):
    if rv:
        raise BLEAppException("TDO interact " + s)



def _une(rv, d, e, ce=0):
    # ude: update dictionary error
    if rv:
        d["error"] = "error " + str(e)
        d["crit_error"] = int(ce)




async def ble_download_tdo(d):

    # d: {'battery_level': 65535,
    #     'error': 'error comm.',
    #     'crit_error': 0,
    #     'dl_files': [],
    #     'rerun': False,
    #     'gfv': '',
    #     'dev': BLEDevice(D0:2E:AB:D9:29:48, DO2_AAA),
    #     'gps_pos': ('+41.610100', '-70.609300', datetime.datetime(2025, 8, 8, 15, 12, 29), '0'),
    #     'antenna_idx': 0,
    #     'antenna_desc': 'internal',
    #     'uuid': '9d8f50cd-0b08-467e-ab98-c62bae39fc96'}

    _is_a_lid_v2_logger = False
    dev = d['dev']
    mac = dev.address
    g = d['gps_pos']
    sn = ddh_config_get_logger_sn_from_mac(mac)
    create_path_to_folder_dl_files_from_mac(mac)


    rv = await connect(dev)
    _une(not rv, d, "comm.")
    _rae(not rv, "connecting")
    lg.a(f"connected to {mac}")


    if ddh_ble_logger_needs_a_reset(mac):
        lg.a(f"debug, logger reset file {mac} found, deleting it")
        await cmd_rst()
        # out of here for sure
        raise BLEAppException("TDO interact logger reset file")


    rv, v = await cmd_gfv()
    _rae(rv, "gfv")
    lg.a(f"GFV | {v}")
    d['gfv'] = v
    

    rv, state = await cmd_sts()
    _rae(rv, "sts")
    lg.a(f"STS | logger was {state}")


    # feature has-logger-been-in-water
    flag_ignore_hbw = ddh_get_template_of_path_of_hbw_flag_file().format(mac)
    if state == 'running':
        # todo: try this
        if v >= MIN_VERSION_HBW_CMD:
            lg.a('sending command Has-Been-in-Water')
            rv, v = await cmd_hbw()
            _rae(rv, "hbw")
            lg.a(f"HBW | {v}")
            if os.path.exists(flag_ignore_hbw):
                os.unlink(flag_ignore_hbw)
                lg.a('file flag to ignore HBW exists, force download it')
            else:
                if v == 0:
                    lg.a('logger has NOT been in water, no need to download it')
                    await disconnect()
                    return 2
                lg.a("logger has been in water, we will download it")
    else:
        lg.a('logger NOT running, not considering HBW command')


    # to know if this DO-X logger uses LID or LIX files
    rv = await lc.cmd_xod()
    _is_a_lid_v2_logger = rv == 0
    lg.a(f"XOD | LIX {_is_a_lid_v2_logger}")


    rv = await cmd_sws(g)
    _rae(rv, "sws")
    lg.a("SWS | OK")


    rv, t = await cmd_utm()
    _rae(rv, "utm")
    lg.a(f"UTM | {t}")


    rv, b = await cmd_bat()
    _rae(rv, "bat")
    adc_b = b
    b /= BAT_FACTOR_DOT
    lg.a(f"BAT | ADC {adc_b} mV -> battery {int(b)} mV")
    d["battery_level"] = b
    if adc_b < 1500:
        ln = LoggerNotification(mac, sn, 'TDO', adc_b)
        notify_logger_error_low_battery(g, ln)
        app_state_set(EV_BLE_LOW_BATTERY, t_str(STR_EV_BLE_LOW_BATTERY))
        d['error'] = 'low battery'
        rv_bad_bat = 1
        _une(rv_bad_bat, d, "BAT_low_error", ce=1)
        lg.a(f'BAT | error {rv_bad_bat}')
        _rae(rv_bad_bat, "bat")


    rv, v = await cmd_gtm()
    _rae(rv, "gtm")
    lg.a(f"GTM | {v}")


    rv = await cmd_stm()
    _rae(rv, "stm")
    lg.a("STM | OK")


    # disable log for lower power consumption
    rv, v = await cmd_log()
    _rae(rv, "log")
    if linux_is_rpi():
        if v != 0:
            rv, v = await cmd_log()
            _rae(rv, "log")
    else:
        # we want logs while developing
        if v != 1:
            rv, v = await cmd_log()
            _rae(rv, "log")



    rv, ls = await cmd_dir()
    _rae(rv, "dir error " + str(rv))
    lg.a(f"DIR | {ls}")
    if MC_FILE not in ls.keys():
        _rae(1, "error, no configuration file in logger")



    # iterate files present in logger
    for name, size in ls.items():

        # delete zero-bytes files
        if size == 0:
            rv = await cmd_del(name)
            _rae(rv, "del")
            continue


        # target file to download
        lg.a(f"downloading file {name}")
        rv = await cmd_dwg(name)
        _rae(rv, "dwg")


        # download file
        rv, file_data = await cmd_dwl(int(size))
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


        # no-deleting the logger configuration file
        if name == MC_FILE:
            continue

        # delete file in logger
        rv = await cmd_del(del_name)
        _rae(rv, "del")
        lg.a(f"deleted file {del_name}")


        # create LEF file with download info
        lg.a(f"creating file LEF for {name}")
        lef_create_file(g, name)



    # format file-system
    await asyncio.sleep(.1)
    rv = await cmd_frm()
    _rae(rv, "frm")
    lg.a("FRM | OK")


    # read the local logger configuration file
    path = str(calculate_path_to_folder_within_dl_files_from_mac_address(mac) / MC_FILE)
    with open(path) as f:
        j = json.load(f)



    # check need to modify the DO interval in the logger config file
    lg.a('debug, analyzing need for DOX interval reconfiguration')
    i_dro = exp_get_conf_dox()
    if i_dro:
        # yes, we were asked to
        if i_dro == int(j["DRI"]):
            lg.a('not changing DRI because it\'s the same')
        else:
            lg.a(f'changing DRI for DOX logger from {j["DRI"]} to {i_dro}')
            j["DRI"] = i_dro
    else:
        lg.a('no experimental conf_dox, keep DRI in DOX logger')



    # all cases, modified or not, send configuration command
    rv = await lc.cmd_cfg(j)
    _rae(rv, "cfg")
    lg.a("CFG | OK")



    # see if the DO sensor works
    for i_do in range(3):
        rv = await lc.cmd_gdo()
        bad_rv = not rv or (rv and rv[0] == "0000")
        if not bad_rv:
            # good!
            lg.a(f"GDO | {rv}")
            break
        # GDO went south, check number of retries remaining
        lg.a(f"GDO | error {rv}")
        if i_do == 2:
            # todo: re-do this
            # notify this
            lat, lon, _, __ = g
            ln = LoggerNotification(mac, sn, 'DOX', b)
            ln.uuid_interaction = u
            notify_logger_error_sensor_oxygen(g, ln)
            _une(bad_rv, notes, "ox_sensor_error", ce=1)
            _rae(bad_rv, "gdo")
        else:
            # todo: send this to GUI in a redis manner
            # _u(STATE_DDH_BLE_DOWNLOAD_ERROR_GDO)
            _une(bad_rv, notes, "ox_sensor_error", ce=0)
        await asyncio.sleep(5)



    # wake mode
    rerun_flag = not ddh_does_do_not_rerun_file_flag_exist()
    w = "on" if rerun_flag else "off"
    rv = await cmd_wak(w)
    _rae(rv, "wak")
    lg.a(f"WAK | {w} OK")
    await asyncio.sleep(1)



    # re-run the logger or not
    d['rerun'] = rerun_flag
    if rerun_flag:
        rv = await cmd_rws(g)
        if rv:
            d['error'] = 'running'
        _rae(rv, "rws")
        lg.a("RWS | OK")


    await disconnect()
    return 0