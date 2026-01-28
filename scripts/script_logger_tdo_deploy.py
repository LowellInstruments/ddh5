#!/usr/bin/env python3


import asyncio
import sys
import subprocess as sp
import os
import toml

from ble.ble_linux import ble_linux_logger_disconnect_all
from mat.utils import PrintColors as _Pc
from script_logger_tdo_deploy_utils import (
    deploy_logger_tdo,
    ble_scan_for_tdo_loggers,
)
from utils.ddh_common import linux_is_rpi

# don't move this from here
FILE_ALL_MACS_TOML = f'../settings/all_macs.toml'


# ---------------------------------
# issues RUN command or not at end
# ---------------------------------
g_cfg = {
    "RUN": False,
    "DFN": 'TST',
    "PRF": 'script_logger_tdo_deploy_cfg_slow.json',
}



ael = asyncio.new_event_loop()
asyncio.set_event_loop(ael)



def get_ddh_toml_all_macs_content():
    try:
        with open(FILE_ALL_MACS_TOML, 'r') as f:
            # d: {'11:22:33:44:55:66': 'sn1234567'}
            return toml.load(f)
    except (Exception,) as ex:
        print('error, get_ddh_toml_all_macs_content: ', ex)
        os._exit(1)



def _screen_clear():
    sp.run("clear", shell=True)
    print('\n')



def _screen_separation():
    print("\n\n")



def _list_all_macs_file_content():
    ls_macs = get_ddh_toml_all_macs_content()
    if not ls_macs:
        return

    print("\nmonitored macs\n--------------\n")
    for i, (k, v) in enumerate(ls_macs.items()):
        if k.startswith("#") or len(k) < 5:
            continue
        print(f'{i}) {k} SN{v}')



def _menu_display_for_tdo_loggers(d: dict):
    print("\nchoose an option:")
    print("\ts) scan for TDO loggers nearby")
    print("\tl) list monitored macs in config.toml file")
    print(f"\tr) toggle RUN flag, current value '{g_cfg['RUN']}'")
    print(f"\td) set DEPLOYMENT name, current value '{g_cfg['DFN']}'")
    current_profile_file = g_cfg['PRF'].split('_cfg_')[1].split('.')[0]
    print(f"\tp) toggle PROFILING file, current value '{current_profile_file}'")
    print("\tq) quit")

    # print found macs with number
    for k, v in d.items():
        mac, sn, rssi = v
        print(f'\t{k}) deploy {mac} -> SN {sn}, rssi {rssi}')
    return input("\t-> ")




def _menu_execute(_m, _c):
    # _c: user choice
    if _c == "q":
        print("bye!")
        sys.exit(0)

    if _c == "s":
        # re-scan
        return

    if _c == "l":
        _list_all_macs_file_content()
        return

    if _c == "r":
        g_cfg['RUN'] = not g_cfg['RUN']
        return

    if _c == "p":
        _p = g_cfg["PRF"]
        if 'slow' in _p:
            _p = 'script_logger_tdo_deploy_cfg_mid.json'
        elif 'mid' in _p:
            _p = 'script_logger_tdo_deploy_cfg_fast.json'
        elif 'fast' in _p:
            _p = 'script_logger_tdo_deploy_cfg_slow.json'
        g_cfg["PRF"] = _p
        return



    if _c == "d":
        # ------------------------
        # set new deployment name
        # ------------------------
        i = str(input("\t\t enter new deployment -> "))
        if len(i) != 3:
            print("invalid input: must be 3 letters long")
            return
        g_cfg["DFN"] = i
        return


    # --------------------------------------------
    # safety check, logger menu keys are integers
    # --------------------------------------------
    if not str(_c).isnumeric():
        print(_Pc.WARNING + "\tunknown option" + _Pc.ENDC)
        return
    _c = int(_c)
    if _c >= len(_m):
        print(_Pc.WARNING + "\tbad option" + _Pc.ENDC)
        return

    # safety check, SN length
    mac, sn = _m[_c][0], _m[_c][1]
    if len(sn) != 7:
        e = "\terror, got {}, but serial numbers must be 7 digits long"
        print(_Pc.FAIL + e.format(sn) + _Pc.ENDC)
        return


    # =====================================
    # call main routine logger preparation
    # =====================================
    print(_Pc.OKBLUE + f"\ndeploying TDO logger {mac}..." + _Pc.ENDC)
    rv = ael.run_until_complete(deploy_logger_tdo(mac, sn, g_cfg))


    # show green or red success
    _ = "\n\t========================="
    s_ok = _Pc.OKGREEN + _ + "\n\t✅ OK {}" + _ + _Pc.ENDC
    s_nok = _Pc.FAIL + _ + "\n\t❌ {}" + _ + _Pc.ENDC
    s = s_ok if rv == 0 else s_nok
    print(s.format(mac))




def main_logger_tdo_deploy():
    ble_linux_logger_disconnect_all()
    _screen_clear()
    d_macs_file = get_ddh_toml_all_macs_content()
    d_macs_file = dict((k.upper(), v) for k, v in d_macs_file.items())
    menu_size = 10
    if not d_macs_file:
        e = "error -> all_macs list is empty"
        print(_Pc.FAIL + e + _Pc.ENDC)
        return

    while True:
        # sr: ('D9:E8:C8:13:08:BE', -83)
        sr = ael.run_until_complete(ble_scan_for_tdo_loggers())

        # builds menu of up to 'n' entries d[#i]: (mac, sn, rssi)
        d_menu = {}
        i = 0
        for r in sr:
            mac, rssi = r
            mac = mac.upper()
            if mac not in d_macs_file.keys():
                continue
            sn = str(d_macs_file[mac])
            d_menu[i] = (mac, sn, rssi)
            i += 1
            if i == menu_size - 1:
                break

        c = _menu_display_for_tdo_loggers(d_menu)
        _menu_execute(d_menu, c)
        _screen_separation()




if __name__ == "__main__":
    if not linux_is_rpi():
        # Pycharm, be sure starting directory is 'ddh/scripts'
        assert str(os.getcwd()).endswith('scripts')
    main_logger_tdo_deploy()
