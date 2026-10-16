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
    ddh_get_path_to_root_application_folder, ddh_get_path_to_folder_dl_files, ddh_get_path_local_folder_dl_files_sondes
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


            # get the next REMOTE filename within this sonde
            p_dl, p_info = wss.wss_cmd_get_next_filename_to_be_pulled()


            # we need meta info file because to decode timestamps of DAT files
            n = os.path.dirname(p_info)[1:]
            fol = ddh_get_path_local_folder_dl_files_sondes()
            p_local_info = f'{fol}/D{n}/meta_{n}_1.info'
            if not os.path.exists(p_local_info):
                rv_pull = wss.wss_cmd_pull_remote_filename(p_local_info)
                if rv_pull != 0:
                    bn = os.path.basename(p_local_info)
                    lg.a(f'error, we cannot pull file {bn} from sonde {sn}')
                    # we cannot continue
                    # todo: show retries or whatever?
                    continue


            if not p_dl:
                # DONE for this sonde
                continue


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


            # wait between files of same sonde
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
