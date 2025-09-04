import json
import signal
import sys

import setproctitle
import redis
import time

from mat.utils import linux_is_rpi
from rd_ctt.ddh import (
    RD_DDH_GUI_PROCESS_NET_OUTPUT
)
from utils.ddh_common import (
    NAME_EXE_NET,
    TMP_PATH_INET_VIA,
    ddh_this_process_needs_to_quit, exp_get_use_debug_print
)
import subprocess as sp
from ddh_log import lg_net as lg



# =================================
# th_net
# updates redis with internet via
# =================================



IP = "8.8.8.8"
r = redis.Redis('localhost', port=6379)
p_name = NAME_EXE_NET
g_killed = False



def _cb_kill(n, _):
    print(f'{p_name}: captured signal kill', flush=True)
    global g_killed
    g_killed = True



def _cb_ctrl_c(n, _):
    print(f'{p_name}: captured signal ctrl + c', flush=True)
    global g_killed
    g_killed = True



def ddh_net_get_internet_via():
    via = r.get(RD_DDH_GUI_PROCESS_NET_OUTPUT)
    return via.decode() if via else None




def ddh_net_calculate_via():

    # check ANY NET via
    c = f"timeout .5 ping -c 1 www.google.com -4"
    for i in range(3):
        rv = sp.run(c, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        if rv.returncode == 0:
            break
        if i == 2:
            return "none"
        time.sleep(.1)

    # we have internet, find specific VIA
    c = f"ip route get {IP}"
    rv = sp.run(c, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    if b"ppp0" in rv.stdout:
        return "cell"
    if b"usb0" in rv.stdout:
        return "cell"
    return "wifi"




def _net():

    via = ddh_net_calculate_via()

    # save to file for API purposes
    try:
        with open(TMP_PATH_INET_VIA, "w") as f:
            json.dump({"internet_via": via}, f)
    except (Exception, ) as ex:
        lg.a(f'error, saving {TMP_PATH_INET_VIA} -> {ex}')
    return via




def _ddh_net(ignore_gui):

    setproctitle.setproctitle(p_name)

    # forever loop set internet via to redis, do not hog CPU
    while 1:

        if ddh_this_process_needs_to_quit(ignore_gui, p_name, g_killed):
            sys.exit(0)


        time.sleep(1)
        if not r.exists(RD_DDH_GUI_PROCESS_NET_OUTPUT):
            via = _net()
            r.set(RD_DDH_GUI_PROCESS_NET_OUTPUT, via)
            r.expire(RD_DDH_GUI_PROCESS_NET_OUTPUT, 60)




def main_ddh_net(ignore_gui=False):

    signal.signal(signal.SIGINT, _cb_ctrl_c)
    signal.signal(signal.SIGTERM, _cb_kill)

    try:
        _ddh_net(ignore_gui)
    except (Exception,) as ex:
        lg.a(f"NET: error, process '{p_name}' restarting after crash -> {ex}")




if __name__ == '__main__':

    # normal run
    main_ddh_net(ignore_gui=False)

    # for debug on pycharm
    # main_ddh_net(ignore_gui=True)



