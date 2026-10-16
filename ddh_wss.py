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


        for sn, ip in g_d_sondes.items():

            # download each Wireless Super Sonde in config.toml
            wss = WSS(ip, sn)
            if not wss.wss_cmd_is_sonde_present():
                lg.a(f'error, {sn} with {ip} not detected')
                continue


            # debug
            lg.a(f'OK, detected {sn} on {ip}')


            # get the next REMOTE filename within this sonde
            # prd: path remote dat file
            # pri: path remote info file
            prd, pri = wss.wss_cmd_get_next_filename_to_be_pulled()


            if not pri:
                lg.a(f'warning, {sn} is empty')
                continue


            # parse remote path fields
            fol = ddh_get_path_local_folder_dl_files_sondes()
            bn_info = os.path.basename(pri)
            sub_fol_timestamp = pri.split('/')[-3]
            sub_fol_deploy = pri.split('/')[-2]



            # file info, needed for its METADATA
            # pli: path local info file
            pli = f'{fol}/{sub_fol_timestamp}/{sub_fol_deploy}/{sn}_{bn_info}'
            if not os.path.exists(pli):
                lg.a(f'⬅️ {sn} ({ip}) PULL = {pri}')
                rv = wss.wss_cmd_pull_remote_file_info(pri, pli)
                if rv:
                    lg.a(f'❌ error, cannot pull info file {bn_info}')
                    # todo: show GUI retries or whatever?
                    continue
                lg.a(f'✅ OK, pulled file {bn_info}')


            if not prd:
                # DONE for this sonde
                continue


            # get the file data, delete it from remote and upload it to cloud
            # p_remote_dat: '/home/pi/Downloads/20260415_100954/D2/AC2_39.dat$1839104'
            bn_dat = os.path.basename(prd).split('$')[0]
            z_dat = int(os.path.basename(prd).split('$')[1])
            p_local_dat = f'{fol}/{sub_fol_timestamp}/{sub_fol_deploy}/{sn}_{bn_dat}'
            lg.a(f'⬅️ {sn} ({ip}) PULL = {prd}')
            if os.path.exists(p_local_dat) and os.path.getsize(p_local_dat) == z_dat:
                lg.a(f'✅ pull OK, {bn_dat} already exists')
            else:
                rv = wss.wss_cmd_pull_remote_file_dat(prd, p_local_dat, z_dat)
                if rv == 0:
                    lg.a(f'✅ pull OK, {bn_dat}')
                else:
                    lg.a(f'❌ error, cannot pull file {bn_dat}')


            # delete the DAT downloaded file
            lg.a(f'⬅️ {sn} ({ip}) DELETE = {prd}')
            wss.wss_cmd_delete_remote_filename(prd)

            # symlink files.dat so AWS can upload-copy-delete them
            fol_upload = str(ddh_get_path_to_root_application_folder()) + '/upload'
            os.makedirs(fol_upload, exist_ok=True)
            link = f'{fol_upload}/{os.path.basename(prd)}'
            if not os.path.exists(link):
                os.symlink(prd, link)


            # wait between files of same sonde
            time.sleep(1)


        # don't hag cpu
        time.sleep(10)




def main_ddh_wss(ignore_gui=False):

    while 1:
        try:
            _ddh_wss(ignore_gui)
        except (Exception, ) as ex:
            lg.a(f"error, process '{p_name}' restarting after crash -> {ex}")




if __name__ == '__main__':

    # normal run
    # main_ddh_wss(ignore_gui=False)

    # for debug
    main_ddh_wss(ignore_gui=True)
