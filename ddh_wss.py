import time
import sys
import redis
import setproctitle

from ddh.wss import WSS
from ddh_log import lg_wss as lg
from utils.ddh_common import (
    ddh_this_process_needs_to_quit,
    NAME_EXE_WSS,
    ddh_config_get_dict_of_monitored_sondes
)



# =====================================================
# ddh_wss
# downloads wireless super sondes
# =====================================================



# r = redis.Redis('localhost', port=6379)
# p_name = NAME_EXE_WSS
# g_d_sondes = ddh_config_get_dict_of_monitored_sondes()



def _ddh_wss(ignore_gui):

    setproctitle.setproctitle(p_name)
    print(f"WSS: process '{p_name}' is running")
    # todo: create WSS needed folders


    # forever loop downloading super sondes
    while 1:

        if ddh_this_process_needs_to_quit(ignore_gui, p_name):
            sys.exit(0)


        # not hag cpu
        time.sleep(1)


        # for sn, ip in g_d_sondes.items():
        #     wss = WSS(ip)
        #     p = wss.send_cmd_get_filename_to_be_sent()
        #     print(f'{sn} ({ip}) has file {p} to send to DDH')
        #     time.sleep(10)



def main_ddh_wss(ignore_gui=False):

    while 1:
        try:
            # _ddh_wss(ignore_gui)
            time.sleep(1)
        except (Exception, ) as ex:
            lg.a(f"error, process '{p_name}' restarting after crash -> {ex}")




if __name__ == '__main__':

    # normal run
    main_ddh_wss(ignore_gui=False)

    # for debug on pycharm
    # main_ddh_wss(ignore_gui=True)
