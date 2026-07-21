import json
import redis
import time
from utils.redis import (
    RD_DDH_NET_PROCESS_OUTPUT
)
from utils.ddh_common import (
    TMP_PATH_INET_VIA,
)
import subprocess as sp
from ddh_log import lg_gui as lg




# =================================
# th_net
# updates redis with internet via
# =================================



IP = "8.8.8.8"
r = redis.Redis('localhost', port=6379)




def ddh_net_calculate_via():

    # check ANY NET via
    c = f"timeout 1 ping -c 1 www.google.com -4"
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




def main_ddh_net():
    while 1:
        time.sleep(1)
        try:
            if not r.exists(RD_DDH_NET_PROCESS_OUTPUT):
                via = ddh_net_calculate_via()
                r.setex(RD_DDH_NET_PROCESS_OUTPUT, 30, via)
                with open(TMP_PATH_INET_VIA, "w") as f:
                    json.dump({"internet_via": via}, f)
        except (Exception,) as ex:
            lg.a(f"error, process NET restarting after crash -> {ex}")




if __name__ == '__main__':
    main_ddh_net()
