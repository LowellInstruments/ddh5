import time
import shlex
import subprocess as sp
import os
from utils.ddh_common import (
    ddh_get_path_local_folder_dl_files_sondes,
    ddh_config_get_path_remote_fol_dat_files
)



PATH_LOCAL_SSH_PRIVATE_KEY = '/home/kaz/Downloads/id_key'
FOL_REMOTE_DAT_FILES = ddh_config_get_path_remote_fol_dat_files()




class WSS:

    _cmd = "ssh -i {} pi@{} \"{}\""

    def __init__(self, ip, pk=PATH_LOCAL_SSH_PRIVATE_KEY):
        self.ip = ip
        self.pk = pk
        self.cmd = ""


    def _send_cmd(self, c, timeout=2):

        # display full SSH command
        self.cmd = self._cmd.format(self.pk, self.ip, c)
        # print(f'\n<- {self.cmd}')


        # execute full SSH command
        p = sp.Popen(
            shlex.split(self.cmd),
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            text=True
        )


        # wait for answer full SSH command
        ts = time.perf_counter()
        all_s = ""
        while True:
            if time.perf_counter() > ts + timeout:
                # print('_cmd end')
                break
            # useful, this does NOT block
            o = p.stdout.read(1)
            if not o:
                # do not hag CPU
                time.sleep(.1)
                continue
            s = o + p.stdout.readline()
            all_s += s
            # print(f'.{s}', end='', flush=True)
            ts = time.perf_counter()


        # return all string, if any or your '||' tricks
        return all_s





    def send_cmd_get_filename_to_be_sent(self):
        fol = FOL_REMOTE_DAT_FILES
        # this finds only one file
        # c = f'\"find {fol_ss_root_dat_files} -name *.dat -type f -printf \"%p - %s bytes\\n\" -quit\"'
        c = f'\"find {fol} -name *.dat -type f -printf \"%p$%s\" -quit\"'
        p = self._send_cmd(c)
        p = p.replace('\n', '')
        p_remote_info = ''
        if p:
            # we get the subfolder index to build the meta info file name
            n = os.path.dirname(p)[-1:]
            # see if we already have this file
            p_local_info = f'{ddh_get_path_local_folder_dl_files_sondes()}/meta_{n}_1.info'
            if not os.path.exists(p_local_info):
                p_remote_info = f'{os.path.dirname(p)}/meta_{n}_1.info'
        return p, p_remote_info






    def send_cmd_pull_file(self, sn, rp):
        # rp: remote_path: '/home/pi/Downloads/20260415_100954/D2/AC2_39.dat$1839104'
        ip = self.ip
        p_src = rp.split('$')[0]
        print(f'\n⬅️ {sn} ({ip}) PULL = {p_src}')
        ls = rp.split('/')
        ts = ls[-3].replace('_', '-')
        bn_size = ls[-1]
        bn, z = bn_size.split('$')
        if not z:
            print(f'\t❌ pull error, z = {z}')
            return 1
        z = int(z)
        dst_bn = f'{sn}_{ts}_{z}_{bn}'
        p_dst = f'{ddh_get_path_local_folder_dl_files_sondes()}/{dst_bn}'
        pk = self.pk
        ip = self.ip

        # check we already have it
        if os.path.exists(p_dst) and os.path.getsize(p_dst) == z:
            print(f'\t✅ pull OK (already exists)')
            return 0
        cy = f"rsync -avzP  -e \"ssh -i {pk}\" pi@{ip}:{p_src} {p_dst}"
        sp.run(cy, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        if os.path.exists(p_dst) and os.path.getsize(p_dst) == z:
            print(f'\t✅ pull OK')
            return 0
        print(f'\t❌ pull error')
        return 1





    def send_cmd_delete_filename_in_remote(self, sn, rp):
        # remote_path: '/home/pi/Downloads/20260415_100954/D2/AC2_39.dat$1839104'
        ip = self.ip
        p_src = rp.split('$')[0]
        print(f'\n⬅️ {sn} ({ip}) DELETE = {p_src}')
        c = f'rm -f {p_src}'
        self._send_cmd(c)
        c = f'test -f {p_src} || echo "nope"'
        s = self._send_cmd(c)
        if 'nope' in s:
            print(f'\t✅ delete OK')
            return 0
        print(f'\t❌ delete error')
        return 1




    def send_cmd_is_sonde_there(self):
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
    wss = WSS("192.168.0.195")
    wss.send_cmd_is_sonde_there()

