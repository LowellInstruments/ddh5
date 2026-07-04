import sys

from ddh_log import LogDDHByModule
import subprocess as sp
import time
import json
from utils.ddh_common import (
    NAME_EXE_AWS,
    NAME_EXE_BLE,
    NAME_EXE_GPS,
    NAME_EXE_CNV, ddh_get_path_to_db_aws_status_file,
)



lg_gui = LogDDHByModule("gui")
d_processes = {
    NAME_EXE_AWS: None,
    NAME_EXE_BLE: None,
    NAME_EXE_CNV: None,
    NAME_EXE_GPS: None,
}



def ddh_write_timestamp_aws_sqs(k, v):
    assert k in ('aws', 'sqs')
    # v: 'ok', 'error', 'unknown'
    assert type(v) is str

    # epoch utc
    t = int(time.time())
    p = ddh_get_path_to_db_aws_status_file()

    # first time ever
    j = {
        'aws': ('unknown', t),
        'sqs': ('unknown', t)
    }

    # load file or get default content
    try:
        with open(p, 'r') as f:
            j = json.load(f)
    except (Exception, ):
        pass

    # update file content
    try:
        j[k] = (v, t)
        with open(p, 'w') as f:
            json.dump(j, f)
    except (Exception, ):
        lg_gui.a(f'error, cannot ddh_write_timestamp_aws_sqs to {p}')




def linux_is_process_running_strict(name) -> bool:
    cmd = f'ps -aux | grep -w {name} | grep -v grep'
    rv = sp.run(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    return rv.returncode == 0



def gui_kill_all_processes():
    lg_gui.a(f'killing all processes')
    # ensure process log finds this
    time.sleep(1.1)
    for p in d_processes.keys():
        sp.run(f'killall {p}', shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        sp.run(f'kill -9 $(pidof {p})', shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    time.sleep(.1)



def gui_check_all_processes():
    for p in d_processes.keys():
        if not linux_is_process_running_strict(p):
            lg_gui.a(f'warning, process {p} not present')



def cb_when_ddh_receives_ctrl_c(signal_num, _):
    lg_gui.a(f'captured signal ctrl + c ({signal_num})')
    gui_kill_all_processes()
    # so DDH GUI is the last to cease to exist
    time.sleep(1)
    sys.exit(0)



def cb_when_ddh_receives_kill_signal(signal_num, _):
    lg_gui.a(f'captured kill signal ({signal_num})')
    gui_kill_all_processes()
    # so DDH GUI is the last to cease to exist
    time.sleep(1)
    sys.exit(0)
