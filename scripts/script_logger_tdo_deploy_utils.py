import toml
from ble.ble import *
from ble.ble_linux import ble_linux_find_best_interface
from mat.utils import PrintColors



def _e(_rv, s):
    if _rv:
        _ = "[ BLE ] example exception {}, rv {}"
        raise Exception(_.format(s, _rv))




async def deploy_logger_tdo(mac, sn, cfg_from_menu):
    rv = 0

    try:
        rv = await connect_by_mac(mac)
        _e(not rv, 'connecting')


        # firmware version the first
        rv, v = await cmd_gfv()
        _e(rv, "gfv")
        ver = v
        print('ver', ver)


        g = ("-3.333333", "-4.444444", None, None)
        rv = await cmd_sws(g)
        _e(rv, "sws")


        rv = await cmd_led()
        _e(rv, "led")


        rv = await cmd_sts()
        _e(rv[0], "sts")


        rv, t = await cmd_gtm()
        _e(rv, "gtm")


        rv = await cmd_stm()
        _e(rv, "stm")


        rv = await cmd_frm()
        _e(rv, "frm")


        rv = await cmd_wli("BA8007")
        _e(rv, "wli_ba")
        await asyncio.sleep(.1)


        rv = await cmd_wli("CA1234")
        _e(rv, "wli_ca")
        await asyncio.sleep(.1)


        rv = await cmd_wli(f"SN{sn}")
        _e(rv, "wli_sn")
        await asyncio.sleep(.1)


        rv, info = await cmd_rli()


        # First Deployment Get / Set on TDO loggers
        rv, v = await cmd_fdg()
        _e(rv, 'fdg')
        rv = await cmd_fds()
        _e(rv, 'fds')
        rv, v = await cmd_fdg()
        _e(rv, 'fdg')


        rv, b = await cmd_bat()
        _e(rv == 1, "bat")
        print("\t\tBAT | {} mV".format(b))


        # check sensor Temperature
        rv, v = await cmd_gst()
        bad_rv = not rv or rv[0] == 1 or rv[1] == 0xFFFF or rv[1] == 0
        _e(bad_rv, 'gst')


        # check sensor Pressure
        rv, v = await cmd_gsp()
        bad_rv = not rv or rv[0] == 1 or rv[1] == 0xFFFF or rv[1] == 0
        _e(bad_rv, 'gsp')


        # -----------------------------
        # new loggers with unified SCC
        # -----------------------------
        prf_file = cfg_from_menu['PRF']
        if ver >= "4.0.06":
            # LOAD profiling configuration, new files are TOML
            prf_file = prf_file.replace('.json', '.toml')
            print('prf_file', prf_file)
            with open(prf_file, 'r') as f:
                d = toml.load(f)['profiling']

            # send the hardcoded DHU
            # I was told to keep this here
            rv = await cmd_scc('DHU', '00101')
            _e(rv, "scc_dhu")
            await asyncio.sleep(.1)

        else:
            # not present in newer loggers
            rv = await cmd_wli("MA1234ABC")
            _e(rv, "wli_ma")
            await asyncio.sleep(.1)
            # LOAD profiling configuration, old files are JSON
            with open(prf_file) as f:
                d = json.load(f)


        # send the loaded SCF configuration via BLE commands
        print(f'SCF: loaded {prf_file}')
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

            rv = await cmd_scf(tag, v)
            bad_rv = rv == 1
            _e(bad_rv, f"scf {tag}")


        # -------------------------------
        # RUNs logger, depending on flag
        # -------------------------------
        if cfg_from_menu['RUN']:
            await asyncio.sleep(1)
            g = (1.111111, 2.222222, None, None)
            rv = await cmd_rws(g)
            print("\t\tRWS --> {}".format(rv))
            _e(rv, "rws")
        else:
            print("\t\tRWS --> omitted: current flag value is False")


        # do NOT remove this
        rv = 0


    except (Exception,) as ex:
        print(PrintColors.FAIL +
              "\t{}".format(ex) +
              PrintColors.ENDC)
        rv = 1


    finally:
        await disconnect()
        return rv




async def ble_scan_for_tdo_loggers(t=5.0):
    ad_i = ble_linux_find_best_interface()
    ad_s = f'hci{ad_i}'
    print(f"\nscanning for {int(t)} seconds for TDO loggers on {ad_s}")
    ls_dev = await BleakScanner(adapter=ad_s).discover(
        timeout=t,
        return_adv=True
    )
    ls_macs_rssi = []
    for dev, adv in ls_dev.values():
        ls_macs_rssi = (dev.address, adv.rssi)
    return ls_macs_rssi
