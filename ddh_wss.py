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
    ddh_get_path_to_root_application_folder, ddh_get_path_to_folder_dl_files, ddh_get_path_local_folder_dl_files_sondes,
    app_state_set, EV_BLE_DL_PROGRESS, t_str, STR_EV_BLE_DL_PROGRESS
)
from utils.redis import RD_DDH_GUI_STATE_EVENT_ICON_LOCK

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


            # iterate files within this sonde
            while 1:
                # prd: path remote dat file
                # pri: path remote info file
                prd, pri = wss.wss_cmd_get_next_filename_to_be_pulled()


                if not pri:
                    lg.a(f'OK, {sn} is empty')
                    break


                # parse remote path fields
                fol = ddh_get_path_local_folder_dl_files_sondes()
                bn_info = os.path.basename(pri)
                sub_fol_timestamp = pri.split('/')[-3]
                sub_fol_deploy = pri.split('/')[-2]


                # -----------------------------------------
                # pull file info, needed for its METADATA
                # -----------------------------------------
                # pli: path local info file
                pli = f'{fol}/{sub_fol_timestamp}/{sub_fol_deploy}/{sn}_{bn_info}'
                if not os.path.exists(pli):
                    lg.a(f'⬅️ {sn} ({ip}) PULL = {pri}')
                    rv = wss.wss_cmd_pull_remote_file_info(pri, pli)
                    if rv:
                        lg.a(f'❌ error, cannot pull info file {bn_info}')
                        # todo: show GUI retries or whatever?
                        break
                    lg.a(f'✅ OK, pulled file {bn_info}')


                if not prd:
                    # DONE for this sonde
                    break


                # -------------------------------------------------------------
                # pull file data, delete it from remote and upload it to cloud
                # -------------------------------------------------------------
                # p_remote_dat: '/home/pi/Downloads/20260415_100954/D2/AC2_39.dat$1839104'
                prd, z_dat = prd.split('$')
                bn_dat = os.path.basename(prd)
                pld = f'{fol}/{sub_fol_timestamp}/{sub_fol_deploy}/{sn}_{bn_dat}'
                lg.a(f'⬅️ {sn} ({ip}) PULL = {prd}')
                if os.path.exists(pld) and os.path.getsize(pld) == z_dat:
                    lg.a(f'✅ pull OK, {bn_dat} already exists')
                else:
                    app_state_set(EV_BLE_DL_PROGRESS, t_str(STR_EV_BLE_DL_PROGRESS) + f' {sn}')
                    r.set(RD_DDH_GUI_STATE_EVENT_ICON_LOCK, value=1, ex=1)
                    rv = wss.wss_cmd_pull_remote_file_dat(prd, pld, z_dat)
                    if rv == 0:
                        lg.a(f'✅ pull OK, {bn_dat}')
                        lg.a(f'⬅️ {sn} ({ip}) DELETE = {prd}')
                        rv = wss.wss_cmd_delete_remote_filename(prd)
                        if rv == 0:
                            lg.a(f'✅ delete OK, {bn_dat}')
                        else:
                            lg.a(f'❌ error, cannot delete file {bn_dat}')
                            break
                    else:
                        lg.a(f'❌ error, cannot pull file {bn_dat}')



                # create symlink files.dat so AWS can upload-copy-delete them
                fol_upload = str(ddh_get_path_to_root_application_folder()) + '/upload'
                os.makedirs(fol_upload, exist_ok=True)
                bn_pld = os.path.basename(pld)
                link = f'{fol_upload}/{bn_pld}'
                if not os.path.exists(link):
                    lg.a(f'creating symlink {link}')
                    os.symlink(pld, link)


            # time between sondes
            time.sleep(5)

        # don't hag cpu, time between wss loops
        time.sleep(10)




def main_ddh_wss(ignore_gui=False):

    while 1:
        try:
            _ddh_wss(ignore_gui)
        except (Exception, ) as ex:
            lg.a(f"error, process '{p_name}' restarting after crash -> {ex}")




if __name__ == '__main__':

    # normal run
    main_ddh_wss(ignore_gui=False)

    # for debug
    # main_ddh_wss(ignore_gui=True)
