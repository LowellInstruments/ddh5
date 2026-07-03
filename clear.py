import sys

from ddh_log import LogDDHByModule
import subprocess as sp
import time

from utils.ddh_common import (
    NAME_EXE_AWS,
    NAME_EXE_BLE,
    NAME_EXE_GPS,
    NAME_EXE_CNV,
)



lg_gui = LogDDHByModule("gui")
d_processes = {
    NAME_EXE_AWS: None,
    NAME_EXE_BLE: None,
    NAME_EXE_CNV: None,
    NAME_EXE_GPS: None,
}



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
