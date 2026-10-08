import time
import shlex
import subprocess as sp
import os



class WSS:

    _cmd = "ssh -i {} pi@{} {}"

    def __init__(self, ip, pk="/home/kaz/Downloads/id_key"):
        self.ip = ip
        self.pk = pk
        self.cmd = ""


    def _send_cmd(self, c, timeout=2):
        self.cmd = self._cmd.format(self.pk, self.ip, c)
        print(f'\n<- {self.cmd}')
        p = sp.Popen(
            shlex.split(self.cmd),
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            text=True
        )

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

        return all_s



    def send_cmd_get_filename_to_be_sent(self):
        cr = "redis-cli --raw --scan --pattern \"to_be_sent*\" | head -n 1"
        # (0, '') or (0, 'filename\n')
        p = self._send_cmd(cr)
        p = p.replace('\n', '')
        return p


    def send_cmd_set_filename_to_be_deleted(self, p):
        cr = f"redis-cli --raw set to_be_deleted_{p} 1"
        return self._send_cmd(cr)


    def send_cmd_download_file(self, bn="100m.bin"):
        p_src = f"/home/pi/li/ddh/dl_files/{bn}"
        p_dst = f"/home/kaz/Downloads/{bn}"
        pk = self.pk
        ip = self.ip
        cy = f"rsync -avzP  -e \"ssh -i {pk}\" pi@{ip}:{p_src} {p_dst}"
        self._send_cmd(cy, timeout=10)
        if os.path.exists(p_dst):
            z = os.path.getsize(p_dst)
            print('z', z)




if __name__ == '__main__':
    # if os.path.exists(dp):
    #     os.unlink(dp)
    # send_cmd_download_file()
    wss = WSS("192.168.0.104")
    wss.send_cmd_download_file()
