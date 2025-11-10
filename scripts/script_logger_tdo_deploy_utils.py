import asyncio
import json
import os

import toml
from bleak import BleakScanner

from ble.ble_linux import ble_linux_adapter_find_best_index_by_app
from ble.ble_oop import LoggerBle
from mat.utils import PrintColors as _Pc



lc = LoggerBle()



def _e(_rv, s):
    if _rv:
        _ = "[ BLE ] exception {}, rv {}"
        raise Exception(_.format(s, _rv))




async def deploy_logger_tdo(mac, sn, cfg_from_menu):
    rv = 0

    try:
        rv = await lc.ble_connect_by_mac(mac)
        _e(not rv, 'connecting DOX logger')


        rv, v = await lc.cmd_gfv()
        _e(rv, "gfv")
        ver = v
        print(f'firmware version = {ver}')


        g = ("-3.333333", "-4.444444", None, None)
        rv = await lc.cmd_sws(g)
        _e(rv, "sws")


        print(f'blinking LEDs')
        rv = await lc.cmd_led()
        _e(rv, "led")


        rv = await lc.cmd_sts()
        _e(rv[0], "sts")


        print('synchronizing time')
        rv, t = await lc.cmd_gtm()
        _e(rv, "gtm")


        rv = await lc.cmd_stm()
        _e(rv, "stm")


        print('formatting logger file-system')
        rv = await lc.cmd_frm()
        _e(rv, "frm")


        rv = await lc.cmd_wli("BA8007")
        _e(rv, "wli_ba")
        await asyncio.sleep(.1)


        rv = await lc.cmd_wli("CA1234")
        _e(rv, "wli_ca")
        await asyncio.sleep(.1)


        rv = await lc.cmd_wli(f"SN{sn}")
        _e(rv, "wli_sn")
        await asyncio.sleep(.1)


        rv, info = await lc.cmd_rli()


        print('doing command First Deployment Set')
        rv, v = await lc.cmd_fdg()
        _e(rv, 'fdg')
        rv = await lc.cmd_fds()
        _e(rv, 'fds')
        rv, v = await lc.cmd_fdg()
        _e(rv, 'fdg')

        dn = cfg_from_menu['DFN']
        print(f'setting deployment name to {dn}')
        rv = await lc.cmd_dns(dn)
        _e(rv, "dns")

        print('measuring battery')
        rv, b = await lc.cmd_bat()
        _e(rv == 1, "bat")
        print(f'battery is {b} mV')


        # check sensor Temperature
        rv, v = await lc.cmd_gst()
        bad_rv = rv == 1 or v == 0xFFFF or v == 0
        _e(bad_rv, 'gst')


        # check sensor Pressure
        rv, v = await lc.cmd_gsp()
        bad_rv = rv == 1 or v == 0xFFFF or v == 0
        _e(bad_rv, 'gsp')


        prf_file = cfg_from_menu['PRF']
        if ver >= "4.0.06":
            # LOAD profiling configuration, new files are TOML
            prf_file = prf_file.replace('.json', '.toml')
            with open(prf_file, 'r') as f:
                d = toml.load(f)['profiling']

            # send the hardcoded DHU, I was told to keep this here
            rv = await lc.cmd_scc('DHU', '00101')
            _e(rv, "scc_dhu")
            await asyncio.sleep(.1)

        else:
            # NOT present in NEW loggers
            rv = await lc.cmd_wli("MA1234ABC")
            _e(rv, "wli_ma")
            await asyncio.sleep(.1)
            # LOAD profiling configuration, old files are JSON
            with open(prf_file) as f:
                d = json.load(f)


        # send the loaded SCF configuration via BLE commands
        bn = os.path.basename(prf_file)
        print(f'sending profiler configuration file {bn}')
        for tag, v in d.items():
            if len(tag) != 3:
                print(f'error, bad SCF tag {tag}')
                break
            if tag == 'MAC':
                print('ignoring tag MAC for now')
                continue
            if len(v) != 5:
                print(f'error, bad SCF value {v} for tag {tag}')
                break

            rv = await lc.cmd_scf(tag, v)
            bad_rv = rv == 1
            _e(bad_rv, f"scf {tag}")


        # RUNs logger, depending on flag
        if cfg_from_menu['RUN']:
            await asyncio.sleep(1)
            g = (1.111111, 2.222222, None, None)
            rv = await lc.cmd_rws(g)
            _e(rv, "rws")
            print('TDO logger is running')

            # don't do this because battery consumption on TDO loggers
            # rv = await lc.cmd_wak("on")
            # _e(rv, "wak")

        else:
            s = (_Pc.WARNING +
                 "TDO logger not running, current RUN flag = 'False'" +
                 _Pc.ENDC)
            print(s)


        # do NOT remove this
        rv = 0


    except (Exception,) as ex:
        print(_Pc.FAIL + "\t{}".format(ex) + _Pc.ENDC)
        rv = 1


    finally:
        await lc.ble_disconnect()
        return rv




async def ble_scan_for_tdo_loggers(t=5.0):
    ad_i = ble_linux_adapter_find_best_index_by_app('')
    ad_s = f'hci{ad_i}'
    print(f"scanning {int(t)} seconds for TDO loggers on {ad_s}")
    ls_dev = await BleakScanner(adapter=ad_s).discover(
        timeout=t,
        return_adv=True
    )
    ls_macs_rssi = []
    for dev, adv in ls_dev.values():
        if dev.name and 'TDO' in dev.name:
            ls_macs_rssi.append((dev.address, adv.rssi))
    return ls_macs_rssi
