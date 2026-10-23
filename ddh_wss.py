import os
import time
import sys
import redis
import setproctitle
from ddh.wss import WSS, RD_ACB_SS_GUI_STATE
from ddh_log import lg_wss as lg
from utils.ddh_common import (
    ddh_this_process_needs_to_quit,
    NAME_EXE_WSS,
    ddh_config_get_dict_of_monitored_sondes,
    ddh_get_path_local_folder_dl_files_sondes,
    app_state_set, EV_BLE_DL_PROGRESS,
    t_str, STR_EV_BLE_DL_PROGRESS,
    ddh_not_enough_space_to_run_super_sonde
)
from utils.redis import RD_DDH_GUI_STATE_EVENT_ICON_LOCK




# =====================================================
# ddh_wss
# downloads wireless super sondes and deletes files
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


        if ddh_not_enough_space_to_run_super_sonde():
            lg.a('error, not enough space to run DDH for super-sondes')
            time.sleep(60)
            continue


        for sn, ip in g_d_sondes.items():

            # download each Wireless Super Sonde in config.toml
            wss = WSS(ip, sn)
            if not wss.wss_cmd_is_sonde_present():
                # lg.a(f'error, {sn} with {ip} not detected')
                continue


            # debug
            lg.a(f'OK, detected {sn} on {ip}')


            # debug
            # todo: delete this line
            lg.a('error, remember to delete this line')
            os.system('rm $HOME/PycharmProjects/ddh/dl_files_sondes/D2/*')


            # iterate files within this sonde
            while 1:

                # prd: path remote dat file
                prd = wss.wss_cmd_get_next_filename_to_be_pulled()
                if not prd:
                    # DONE for this sonde
                    lg.a(f'OK, {sn} is empty')
                    wss.wss_cmd_redis_set(RD_ACB_SS_GUI_STATE, 'ready')
                    break



                # --------------------------------------------------------------------------
                # pull remote data (prd) file: '/home/pi/.../<date>/D2/AC2_39.dat$1839104'
                # --------------------------------------------------------------------------

                fol = ddh_get_path_local_folder_dl_files_sondes()
                sub_fol_deploy = prd.split('/')[-2]
                sub_fol_timestamp = prd.split('/')[-3]
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
                    if rv:
                        lg.a(f'❌ error, cannot pull file {bn_dat}')
                        break
                    lg.a(f'✅ pull OK, {bn_dat}')



                # ------------------------------------------
                # delete remote file .dat from super sonde
                # ------------------------------------------

                lg.a(f'⬅️ {sn} ({ip}) DELETE = {prd}')
                rv = wss.wss_cmd_delete_remote_filename(prd)
                if rv:
                    lg.a(f'❌ error, cannot delete file {bn_dat}')
                    break
                lg.a(f'✅ delete OK, {bn_dat}')


            # time between sondes within same WSS loop
            time.sleep(1)

        # don't hag cpu, time between different WSS loops
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
