import glob

import time
import shlex
import subprocess as sp
import os
from ble.li_cmds import DEV_SHM_DL_PROGRESS
from ddh_cnv import PATH_FOL_UPLOAD
from utils.ddh_common import (
    ddh_config_get_path_remote_fol_dat_files,
    ddh_config_get_box_sn, ddh_get_path_local_folder_dl_files_sondes
)



PATH_LOCAL_SSH_PRIVATE_KEY = '/home/kaz/Downloads/id_key'
if not os.path.exists(PATH_LOCAL_SSH_PRIVATE_KEY):
    print('*** ERROR, no DDH private key found. ***')
FOL_REMOTE_DAT_FILES = ddh_config_get_path_remote_fol_dat_files()
rg = 'acb:ss_gui:'
RD_ACB_SS_GUI_STATE = rg + 'state'
RD_ACB_SS_GUI_UPLOAD_PROGRESS = rg + 'upload_progress'
RD_ACB_SS_GUI_UPLOAD_FILENAME = rg + 'upload_filename'
RD_ACB_SS_GUI_UPLOAD_DDH = rg + 'upload_ddh'
my_ddh_sn = ddh_config_get_box_sn()
PATH_FOL_DL_SONDES = ddh_get_path_local_folder_dl_files_sondes()





# -----------------------------------------------------------------
# this code pulls files from remote sonde and
# writes Redis in remote to tell about download progress
# -----------------------------------------------------------------



class WSS:

    _CMD = "ssh -i {} pi@{} \"{}\""

    def __init__(self, ip, sn, pk=PATH_LOCAL_SSH_PRIVATE_KEY):

        self.ip = ip
        self.sn = sn
        self.pk = pk
        self.cmd = ""




    def _send_cmd(self, c, timeout_secs=None):

        self.cmd = self._CMD.format(self.pk, self.ip, c)
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

        # finds ONLY ONE file
        fol_remote = FOL_REMOTE_DAT_FILES
        c = f'find {fol_remote} -name *.dat -type f -printf \"%p$%s\" -quit'
        p = self._send_cmd(c)
        return p.replace('\n', '')




    def wss_cmd_pull_remote_file_dat(self, rp, p_local_dat, z_dat):

        # remote_path, rp: '/home/pi/Downloads/20260415_100954/D2/AC2_39.dat'
        # p_local_dat: '<dl_fol>/{sub_fol_timestamp}/{sub_fol_deploy}/{sn}_{bn_dat}'
        # z: size
        pld = str(p_local_dat)
        os.makedirs(os.path.dirname(pld), exist_ok=True)
        cy = f"rsync -avzP  -e \"ssh -i {self.pk}\" pi@{self.ip}:{rp} {pld}"
        # print('cy', cy)

        # -----------------------
        # run the rsync command
        # -----------------------
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
        bn_pld = os.path.basename(pld)
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
                # do not hag CPU while monitoring transfer progress
            time.sleep(.1)
            self.wss_cmd_redis_set(RD_ACB_SS_GUI_STATE, 'upload')
            self.wss_cmd_redis_set(RD_ACB_SS_GUI_UPLOAD_FILENAME, bn_pld)
            self.wss_cmd_redis_set(RD_ACB_SS_GUI_UPLOAD_DDH, my_ddh_sn)
            o = o.replace('\n', '')
            if '%' in o:
                # o: 1,269,760 100%    1.18GB/s    0:00:00 (xfr#1, to-chk=0/1)
                v = o.split('%')[0].rsplit(' ')[-1]
                self.wss_cmd_redis_set(RD_ACB_SS_GUI_UPLOAD_PROGRESS, v)
                # print(f'\t{v} %')

                # update progress bar in DDH GUI
                with open(DEV_SHM_DL_PROGRESS, 'w') as f:
                    f.write(str(v))
            ts = time.perf_counter()

        if not os.path.exists(pld):
            print(f'error PULL, LOCAL file {pld} does not exist')
            return 1
        if os.path.getsize(pld) != int(z_dat):
            print(f'error PULL, LOCAL size {os.path.getsize(pld)} != z_dat {z_dat}')
            return 1


        # ---------------------------------------------------------------
        # write symlink AC_files.dat so AWS can upload-copy-delete them
        # ---------------------------------------------------------------

        if 'AC' in pld:
            bn_pld = os.path.basename(pld)
            link = f'{PATH_FOL_UPLOAD}/{bn_pld}'
            if os.path.islink(link):
                os.unlink(link)
            if not os.path.exists(link):
                # print(f'creating AC.dat symlink {link}')
                os.symlink(pld, link)


        return 0




    def wss_cmd_delete_remote_filename(self, remote_path):

        # rp: '/home/pi/Downloads/20260415_100954/D1/SENS_1_1.dat'
        c = f'rm -f {remote_path}'
        self._send_cmd(c)
        c = f'test -f {remote_path} || echo "nope"'
        s = self._send_cmd(c)
        return 0 if 'nope' in s else 1




    def wss_cmd_is_sonde_present(self):

        timeout_secs = 2
        interval_secs = 0.5
        # todo: detect adhoc interface (-I capital)
        c = f'ping -w {timeout_secs} {self.ip} -i {interval_secs}'
        rv = sp.run(c, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        return rv.returncode == 0




if __name__ == '__main__':
    wss = WSS("192.168.9.11", 'sonde1')
    wss.wss_cmd_is_sonde_present()

