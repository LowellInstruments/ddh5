import glob
import os
import pathlib
import time
from utils.ddh_common import (
    ddh_get_path_to_folder_macs, ddh_config_get_forget_time_seconds,
)
from ddh_log import lg_ble as lg


# ---------------------------------------------
# small file-based DB of black and orange macs
# ---------------------------------------------


PERIOD_MACS_ORANGE_SECS = 15


def macs_color_show_at_boot():
    b = macs_black()
    o = macs_orange()
    lg.a(f"debug, boot macs_black  = {b}")
    lg.a(f"debug, boot macs_orange = {o}")



def _macs_get_them_by_color(s) -> list:
    assert s in ("orange", "black")
    now = int(time.time())
    fol = str(ddh_get_path_to_folder_macs() / s)
    mask = f"{fol}/*"
    ls = []

    for f in glob.glob(mask):
        # f: absolute path
        mac, t = os.path.basename(f).split("@")
        # purge while searching
        if now > int(t):
            lg.a(f"macs {s} purge {f}")
            os.unlink(f)
        else:
            ls.append(mac)
    return ls


def macs_black():
    return _macs_get_them_by_color("black")


def macs_orange():
    return _macs_get_them_by_color("orange")


def _add_mac(c, mac):
    assert c in ("orange", "black")
    ft = ddh_config_get_forget_time_seconds()
    if c == "orange":
        ft = PERIOD_MACS_ORANGE_SECS
    t = int(time.time()) + ft
    fol = str(ddh_get_path_to_folder_macs() / c)
    mac = mac.replace(":", "-")
    f = f"{fol}/{mac}@{t}"
    pathlib.Path(f).touch()
    now = int(time.time())
    lg.a(f"{c}'ed mac {mac}, value {t}, now {now}")


def _rm_mac(c, m):
    assert c in ("orange", "black")
    m = m.replace(":", "-")
    fol = str(ddh_get_path_to_folder_macs() / c)
    mask = f"{fol}/{m}@*"
    for f in glob.glob(mask):
        lg.a(f"MACS delete {f}")
        os.unlink(f)


def add_mac_black(m):
    _add_mac("black", m)


def add_mac_orange(m):
    _add_mac("orange", m)


def rm_mac_black(m):
    _rm_mac("black", m)


def rm_mac_orange(m):
    _rm_mac("orange", m)


def is_mac_in_black(m):
    b = macs_black()
    m = m.replace(":", "-")
    return m in str(b)


def is_mac_in_orange(m):
    o = macs_orange()
    m = m.replace(":", "-")
    return m in str(o)
