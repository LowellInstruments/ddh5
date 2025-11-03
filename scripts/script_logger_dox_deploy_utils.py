from ble.ble import *
from ble.ble_linux import ble_linux_adapter_find_best_index_by_app
from mat.utils import PrintColors as _Pc



def _e(_rv, s):
    if _rv:
        _ = "[ BLE ] exception {}, rv {}"
        raise Exception(_.format(s, _rv))


def get_script_cfg_file():
    # here it is OK to crash to detect bad json files
    p = f"script_logger_dox_deploy_cfg.json"
    with open(p) as f:
        return json.load(f)



def set_script_cfg_file(cfg_d: dict):
    p = f"script_logger_dox_deploy_cfg.json"
    with open(p, "w") as f:
        return json.dump(cfg_d, f)




async def deploy_logger_dox(mac, sn, flag_run, flag_sensor, dn):
    rv = 0

    try:
        rv = await ble_connect_by_mac(mac)
        _e(not rv, "connecting TDO logger")

        rv, v = await cmd_gfv()
        _e(rv, "gfv")
        ver = v
        print(f'firmware version = {ver}')


        g = ("-3.333333", "-4.444444", None, None)
        rv = await cmd_sws(g)
        _e(rv, "sws")


        print(f'blinking LEDs')
        rv = await cmd_led()
        _e(rv, "led")


        rv = await cmd_sts()
        _e(rv[0], "sts")

        print('synchronizing time')
        rv, t = await cmd_gtm()
        _e(rv, "gtm")

        rv = await cmd_stm()
        _e(rv, "stm")


        print('formatting logger file-system')
        rv = await cmd_frm()
        _e(rv, "frm")


        print(f'setting deployment name to {dn}')
        rv = await cmd_dns(dn)
        _e(rv, "dns")


        d = get_script_cfg_file()
        rv = await cmd_cfg(d)
        _e(rv, "cfg")


        rv = await cmd_wli("BA8007")
        _e(rv, "wli_ba")
        await asyncio.sleep(.1)

        rv = await cmd_wli("MA1234ABC")
        _e(rv, "wli_ma")
        await asyncio.sleep(.1)


        rv = await cmd_wli("CA1234")
        _e(rv, "wli_ca")
        await asyncio.sleep(.1)

        rv = await cmd_wli(f"SN{sn}")
        _e(rv, "wli_sn")
        await asyncio.sleep(.1)

        rv, info = await cmd_rli()


        print('measuring battery')
        rv, b = await cmd_bat()
        _e(rv == 1, "bat")
        print(f'battery is {b} mV')


        print('measuring oxygen sensor')
        rv = await cmd_gdo()
        print(f'oxygen value is {rv}')
        bad_rv = not rv or (rv and rv[0] in ("0000", -1))
        if flag_sensor:
            _e(bad_rv, "gdo")


        # -------------------------------
        # RUNs logger, depending on flag
        # -------------------------------
        if flag_run:
            await asyncio.sleep(1)
            g = (1.111111, 2.222222, None, None)
            rv = await cmd_rws(g)
            _e(rv, "rws")
            print('DOX logger is running')

            rv = await cmd_wak("on")
            _e(rv, "wak")
            print('DOX logger set wake mode 1')

        else:
            s = (_Pc.WARNING +
                 "DOX logger not running, current RUN flag = 'False'" +
                 _Pc.ENDC)
            print(s)


        # do NOT remove this
        rv = 0

    except (Exception,) as ex:
        print(_Pc.FAIL + "\t{}".format(ex) + _Pc.ENDC)
        rv = 1

    finally:
        await ble_disconnect()
        return rv



async def ble_scan_for_dox_loggers(t=5.0):
    ad_i = ble_linux_adapter_find_best_index_by_app('')
    ad_s = f'hci{ad_i}'
    print(f"scanning {int(t)} seconds for DOX loggers on {ad_s}")
    ls_dev = await BleakScanner(adapter=ad_s).discover(
        timeout=t,
        return_adv=True
    )
    ls_macs_rssi = []
    for dev, adv in ls_dev.values():
        n = dev.name
        if n and ('DO-1' in n or 'DO-2' in n or 'DO2' in n):
            ls_macs_rssi.append((dev.address, adv.rssi))
    return ls_macs_rssi
