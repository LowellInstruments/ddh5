import os
import time
import sys
import redis
import setproctitle
from ddh.wss import WSS
from ddh_log import lg_wss as lg
from utils.ddh_common import (
    ddh_this_process_needs_to_quit,
    NAME_EXE_WSS,
    ddh_config_get_dict_of_monitored_sondes,
    ddh_get_path_to_root_application_folder
)



# =====================================================
# ddh_wss
# downloads wireless super sondes
# =====================================================



r = redis.Redis('localhost', port=6379)
p_name = NAME_EXE_WSS
g_d_sondes = ddh_config_get_dict_of_monitored_sondes()



def _ddh_wss(ignore_gui):

    setproctitle.setproctitle(p_name)
    print(f"WSS: process '{p_name}' is running")


    # forever loop downloading super sondes
    while 1:

        if ddh_this_process_needs_to_quit(ignore_gui, p_name):
            sys.exit(0)


        # not hag cpu
        time.sleep(1)


        for sn, ip in g_d_sondes.items():
            wss = WSS(ip)
            if not wss.send_cmd_is_sonde_there():
                lg.a(f'error, {sn} with {ip} not detected')
                continue
            p_dl, p_info = wss.send_cmd_get_filename_to_be_sent()
            if not p_dl:
                time.sleep(10)
                continue

            rv_pull = wss.send_cmd_pull_file(sn, p_dl)
            if rv_pull == 0:
                wss.send_cmd_delete_filename_in_remote(sn, p_dl)
                # symlink files.dat so AWS can upload-copy-delete them
                fol_upload = str(ddh_get_path_to_root_application_folder()) + '/upload'
                os.makedirs(fol_upload, exist_ok=True)
                bn_dl = os.path.basename(p_dl)
                link_dl = f'{ddh_get_path_to_root_application_folder()}/upload/{bn_dl}'
                if not os.path.exists(link_dl):
                    os.symlink(p_dl, link_dl)

            time.sleep(1)






def main_ddh_wss(ignore_gui=False):

    while 1:
        try:
            _ddh_wss(ignore_gui)
        except (Exception, ) as ex:
            lg.a(f"error, process '{p_name}' restarting after crash -> {ex}")




if __name__ == '__main__':

    # normal run
    # main_ddh_wss(ignore_gui=False)

    # for debug on pycharm
    main_ddh_wss(ignore_gui=True)
