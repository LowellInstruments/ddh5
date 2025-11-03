import sys
import setproctitle
import time
import redis
from rd_ctt.ddh import RD_DDH_LOG_QUEUE
from datetime import datetime, timezone
from utils.ddh_common import (
    ddh_get_path_to_folder_logs,
    NAME_EXE_LOG,
    ddh_config_get_vessel_name, ddh_this_process_needs_to_quit
)
from pathlib import Path
from mat.utils import PrintColors as PC




# ===============================================
# ddh_log
# dequeues print requests from other processes
# ===============================================



r = redis.Redis('localhost', port=6379)
q = RD_DDH_LOG_QUEUE
p_name = NAME_EXE_LOG
ymd = datetime.now().strftime('%Y-%m-%d')
vn = ddh_config_get_vessel_name().replace(" ", "_")
d = str(ddh_get_path_to_folder_logs())
Path(d).mkdir(parents=True, exist_ok=True)
log_file = f'{d}/{vn}_{ymd}.log'
f = open(log_file, 'a')
g_last_now = ''



# a class to enqueue messages to our redis LOG queue
class LogDDHByModule:
    def __init__(self, label):
        self.label = label
        self.debug = False


    def a(self, s):
        s = f'{self.label.upper()}: {s}'
        r.rpush(q, s)


    def x(self):
        r.rpush(q, '\n')




lg_ble = LogDDHByModule("ble")
lg_aws = LogDDHByModule("aws")
lg_cnv = LogDDHByModule("cnv")
lg_sqs = LogDDHByModule("sqs")
lg_gps = LogDDHByModule("gps")
lg_gui = LogDDHByModule("gui")
lg_net = LogDDHByModule("net")
lg_emo = LogDDHByModule("emo")
lg_gra = LogDDHByModule("gra")
lg_trk = LogDDHByModule("trk")
lg_tst = LogDDHByModule("tst")



def _color_write_to_console(b):
    s = b.decode()
    if 'error' in s:
        PC.R(s)
    elif 'debug' in s:
        PC.B(s)
    elif 'warning' in s:
        PC.Y(s)
    elif 'OK' in s:
        PC.G(s)
    elif 'success' in s:
        PC.G(s)
    else:
        PC.N(s)
    sys.stdout.flush()




def _write_to_log_file(s):
    f.write(s)
    f.flush()




# -------------------------------------------
# LOG_HANDLES things queued by using lg.a()
# from DDH subprocesses, not print()
# -------------------------------------------

def _dequeue_n_log():
    global g_last_now

    for i in range(r.llen(q)):
        _, b = r.blpop([q])
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # time header
        if now != g_last_now:
            u_now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            _write_to_log_file(f'\n{now} / {u_now}\n')
            print(f'\n\n{now} / {u_now}', flush=True)
        g_last_now = now

        # bunch of text to file
        _write_to_log_file(f'{b.decode()}\n')

        # PRINTS a bunch of colored text to console
        _color_write_to_console(b)



def _ddh_log(ignore_gui):

    r.delete(q)
    setproctitle.setproctitle(p_name)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    _write_to_log_file(f'\n\n\n\n\n\n=== DDH log for vessel {vn} starts on local time {now} ===\n')
    print(f"LOG: process '{p_name}' is running")


    # forever loop collecting messages to log
    while 1:

        if ddh_this_process_needs_to_quit(ignore_gui, p_name):
            sys.exit(0)

        time.sleep(1)
        _dequeue_n_log()





def main_ddh_log(ignore_gui=False):
    while 1:
        try:
            _ddh_log(ignore_gui)
        except (Exception, ) as ex:
            print(f'LOG: error, process {p_name} restarting after crash -> {ex}')




if __name__ == '__main__':
    main_ddh_log(ignore_gui=False)