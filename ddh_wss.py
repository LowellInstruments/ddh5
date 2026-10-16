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
        time.sleep(10)


        for sn, ip in g_d_sondes.items():

            # download each Wireless Super Sonde in config.toml
            wss = WSS(ip, sn)
            if not wss.wss_cmd_is_sonde_present():
                lg.a(f'error, {sn} with {ip} not detected')
                continue

            # get the next filename within this sonde
            # todo: redo this SO file metainfo is ALWAYS the first one pulled
            # todo: because we need it for DAT conversion of timestamps
            p_dl, p_info = wss.wss_cmd_get_next_filename_to_be_pulled()
            if not p_dl:
                time.sleep(1)
                continue

            # todo: get FILE p_info too

            # get the file data, delete it from remote and upload it to cloud
            rv_pull = wss.wss_cmd_pull_remote_filename(p_dl)
            if rv_pull == 0:
                wss.wss_cmd_delete_remote_filename(p_dl)
                # symlink files.dat so AWS can upload-copy-delete them
                fol_upload = str(ddh_get_path_to_root_application_folder()) + '/upload'
                os.makedirs(fol_upload, exist_ok=True)
                link = f'{fol_upload}/{os.path.basename(p_dl)}'
                if not os.path.exists(link):
                    os.symlink(p_dl, link)

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
