import time
import shlex
import subprocess as sp
import os

from ble.li_cmds import DEV_SHM_DL_PROGRESS
from utils.ddh_common import (
    ddh_get_path_local_folder_dl_files_sondes,
    ddh_config_get_path_remote_fol_dat_files, ddh_config_get_box_sn
)



PATH_LOCAL_SSH_PRIVATE_KEY = '/home/kaz/Downloads/id_key'
FOL_REMOTE_DAT_FILES = ddh_config_get_path_remote_fol_dat_files()
rg = 'acb:ss_gui:'
RD_ACB_SS_GUI_STATE = rg + 'state'
RD_ACB_SS_GUI_UPLOAD_PROGRESS = rg + 'upload_progress'
RD_ACB_SS_GUI_UPLOAD_FILENAME = rg + 'upload_filename'
RD_ACB_SS_GUI_UPLOAD_DDH = rg + 'upload_ddh'
my_ddh_sn = ddh_config_get_box_sn()





# ---------------------------------------------------------------------------------------
# p_remote: /home/pi/Downloads/20260415_100954/D2/meta_2_1.info
# p_local:  /home/kaz/.../ddh/dl_files_sondes/20260415_100954/sonde1_meta_2_1.info
# this code pulls files from remote
# this code writes Redis in remote to tell about download progress
# ---------------------------------------------------------------------------------------



class WSS:

    _cmd = "ssh -i {} pi@{} \"{}\""

    def __init__(self, ip, sn, pk=PATH_LOCAL_SSH_PRIVATE_KEY):
        self.ip = ip
        self.sn = sn
        self.pk = pk
        self.cmd = ""




    def _send_cmd(self, c, timeout_secs=None):
        self.cmd = self._cmd.format(self.pk, self.ip, c)
        if timeout_secs:
            self.cmd = f'timeout {timeout_secs} {self.cmd}'
        rv = sp.run(self.cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        return rv.stdout.decode()



    def wss_cmd_redis_set(self, k, v, ex_secs=5):
        c = f'redis-cli SET {k} {v}'
        if ex_secs:
            c += f' EX {ex_secs}'
        s = self._send_cmd(c)
        return 0 if 'OK' in s else 1





    def wss_cmd_get_next_filename_to_be_pulled(self):
        # finds only one file
        fol_remote = FOL_REMOTE_DAT_FILES
        c = f'find {fol_remote} -name *.dat -type f -printf \"%p$%s\" -quit'
        p = self._send_cmd(c)

        p = p.replace('\n', '')
        if not p:
            return '', ''
        # p: '/home/pi/Downloads/20260415_100954/D2/AC2_32.dat$7077888'
        sub_fol_deploy = p.split('/')[-2]
        sub_fol_timestamp = p.split('/')[-3]
        p_remote_info = ''
        # get subfolder index (Dx) to build the meta info file name
        x = sub_fol_deploy[1:]
        if p:
            fol_local = ddh_get_path_local_folder_dl_files_sondes()
            p_local_info = f'{fol_local}/{sub_fol_timestamp}/{self.sn}_meta_{x}_1.info'
            if not os.path.exists(p_local_info):
                p_remote_info = f'{os.path.dirname(p)}/meta_{x}_1.info'
        return p, p_remote_info






    def wss_cmd_pull_remote_file_dat(self, rp, p_local_dat, z_dat):
        # rp: remote_path: '/home/pi/Downloads/20260415_100954/D2/AC2_39.dat'
        pld = str(p_local_dat)
        bn_pld = os.path.basename(pld)
        os.makedirs(os.path.dirname(pld), exist_ok=True)
        cy = f"rsync -avzP  -e \"ssh -i {self.pk}\" pi@{self.ip}:{rp} {pld}"
        # print('cy', cy)

        pr = sp.Popen(
            shlex.split(cy),
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            text=True,
            # USEFUL when child process is buffering
            bufsize=0
        )


        # note: a value of 1 here is too demanding
        timeout_download = 2
        ts = time.perf_counter()
        self.wss_cmd_redis_set(RD_ACB_SS_GUI_STATE, 'upload')
        self.wss_cmd_redis_set(RD_ACB_SS_GUI_UPLOAD_FILENAME, bn_pld)
        with open(DEV_SHM_DL_PROGRESS, 'w') as f:
            f.write('0')
        while True:
            if time.perf_counter() > ts + timeout_download:
                # print('_cmd end')
                break

            # useful, this does NOT block
            o = pr.stdout.readline()
            if not o:
                continue
                # do not hag CPU
            time.sleep(.1)
            self.wss_cmd_redis_set(RD_ACB_SS_GUI_STATE, 'upload')
            self.wss_cmd_redis_set(RD_ACB_SS_GUI_UPLOAD_FILENAME, bn_pld)
            self.wss_cmd_redis_set(RD_ACB_SS_GUI_UPLOAD_DDH, my_ddh_sn)
            o = o.replace('\n', '')
            if '%' in o:
                # o: 1,269,760 100%    1.18GB/s    0:00:00 (xfr#1, to-chk=0/1)
                v = o.split('%')[0].rsplit(' ')[-1]
                self.wss_cmd_redis_set(RD_ACB_SS_GUI_UPLOAD_PROGRESS, v)
                print(f'\t{v} %')
                # update progress bar in DDH GUI
                with open(DEV_SHM_DL_PROGRESS, 'w') as f:
                    f.write(str(v))
            ts = time.perf_counter()


        return 0 if os.path.exists(pld) and os.path.getsize(pld) == int(z_dat) else 1




    def wss_cmd_pull_remote_file_info(self, rp, p_local_info):
        # rp: remote_path: '/home/pi/Downloads/20260415_100954/D2/meta_2_1.info'
        pli = str(p_local_info)
        os.makedirs(os.path.dirname(pli), exist_ok=True)
        cy = f"rsync -avzP  -e \"ssh -i {self.pk}\" pi@{self.ip}:{rp} {pli}"
        sp.run(cy, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        return 0 if os.path.exists(pli) else 1





    def wss_cmd_delete_remote_filename(self, rp):
        # rp: '/home/pi/Downloads/20260415_100954/D1/SENS_1_1.dat'
        c = f'rm -f {rp}'
        self._send_cmd(c)
        c = f'test -f {rp} || echo "nope"'
        s = self._send_cmd(c)
        return 0 if 'nope' in s else 1




    def wss_cmd_is_sonde_present(self):
        ip = self.ip
        timeout_secs = 2
        interval_secs = 0.5
        # todo: detect adhoc interface (-I capital)
        c = f'ping -w {timeout_secs} {ip} -i {interval_secs}'
        rv = sp.run(c, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        return rv.returncode == 0







if __name__ == '__main__':
    # if os.path.exists(dp):
    #     os.unlink(dp)
    # send_cmd_download_file()
    wss = WSS("192.168.0.195", 'sonde1')
    wss.wss_cmd_is_sonde_present()

