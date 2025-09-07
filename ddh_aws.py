import datetime
import glob
import json
import os
import pathlib
import signal
import sys

import setproctitle
import time
import redis
import subprocess as sp
from ddh.emolt import this_box_has_grouped_s3_uplink
from ddh_net import ddh_net_calculate_via
from mat.utils import linux_is_rpi
from rd_ctt.ddh import (
    RD_DDH_AWS_COPY_QUEUE,
    RD_DDH_BLE_SEMAPHORE,
    RD_DDH_AWS_SYNC_REQUEST, RD_DDH_GUI_PROCESS_AWS_OUTPUT
)
from utils.ddh_common import (
    NAME_EXE_AWS,
    ddh_get_path_to_folder_dl_files,
    TESTMODE_FILENAME_PREFIX,
    ddh_get_path_to_db_aws_status_file,
    ddh_config_get_vessel_name,
    ddh_config_get_one_aws_credential_value,
    LI_PATH_LAST_YEAR_AWS_TEMPLATE, ddh_this_process_needs_to_quit)
from ddh_log import lg_aws as lg




# ===================================================================
# ddh_aws
#   - dequeues AWS-CP requests from BLE download (LID + track files)
#   - dequeues AWS-cop requests from CNV for new CSV files
#   - attends AWS sync requests from GUI or periodically
#   - also updates AWS redis state
# ===================================================================




r = redis.Redis('localhost', port=6379)
p_name = NAME_EXE_AWS
q = RD_DDH_AWS_COPY_QUEUE
vessel = (ddh_config_get_vessel_name()
          .replace("'", "").replace(" ", "_").upper())
dev = not linux_is_rpi()
g_killed = False



def _cb_kill(n, _):
    print(f'{p_name}: captured signal kill', flush=True)
    global g_killed
    g_killed = True



def _cb_ctrl_c(n, _):
    print(f'{p_name}: captured signal ctrl + c', flush=True)
    global g_killed
    g_killed = True



def _get_path_of_aws_binary():
    # apt install awscli
    # 2024 is 1.22.34
    return "aws"



def _ddh_aws_set_state(s):
    r.set(RD_DDH_GUI_PROCESS_AWS_OUTPUT, s)



def ddh_aws_get_state():
    return r.get(RD_DDH_GUI_PROCESS_AWS_OUTPUT)



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
        lg.a(f'error, cannot ddh_write_timestamp_aws_sqs to {p}')




def _ddh_get_timestamp_aws_sqs(k):
    assert k in ('aws', 'sqs')
    p = ddh_get_path_to_db_aws_status_file()
    try:
        with open(p, 'r') as f:
            j = json.load(f)
            # {"aws": ["unknown", 1724246474], ... }
            return j[k][1]
    except (Exception, ):
        return 0




def _aws_sync(past_year=False):

    # doing past year AWS sync
    yyyy = datetime.datetime.now().year
    yyyy_prev = yyyy - 1
    yyyy_prev_flag = LI_PATH_LAST_YEAR_AWS_TEMPLATE + str(yyyy_prev)
    if past_year and os.path.exists(yyyy_prev_flag):
        lg.a(f'skip AWS sync for LAST YEAR {yyyy_prev} because flag detected')
        return 0


    # cannot do anything without internet access
    if ddh_net_calculate_via() == 'none':
        lg.a('warning, no AWS copy, no internet access')
        return 1


    # check AWS credentials
    _k = ddh_config_get_one_aws_credential_value("cred_aws_key_id")
    _s = ddh_config_get_one_aws_credential_value("cred_aws_secret")
    _n = ddh_config_get_one_aws_credential_value("cred_aws_bucket")
    if _k is None or _s is None or _n is None:
        lg.a("error, missing credentials")
        return 1
    if not _n.startswith("bkt-"):
        lg.a('warning, bucket name does not start with bkt-')


    # run AWS sync in each sub-folder within folder dl_files
    fol_dl_files = ddh_get_path_to_folder_dl_files()
    mac_folders = [d for d in glob.glob(str(fol_dl_files) + '/*') if os.path.isdir(d)]
    all_rv = 0
    _bin = _get_path_of_aws_binary()
    dr = "--dryrun" if dev else ""
    for m in mac_folders:
        um = m.split('/')[-1]
        y = yyyy
        sy = str(y)[2:]
        if this_box_has_grouped_s3_uplink():
            lg.a(f'S3 upload-sync GROUPed for folder {um}, year {y}, dry-run = {dev}')
            um = f"{str(y)}/{vessel}/{um}"
        else:
            lg.a(f'S3 upload-sync NON-GROUPed mode for folder {um}, year {y}, dry-run = {dev}')

        # format AWS sync command
        cmd = (
            f"AWS_ACCESS_KEY_ID={_k} AWS_SECRET_ACCESS_KEY={_s} "
            f"{_bin} s3 sync {m} s3://{_n}/{um} "
            '--exclude "*" '
            # Moana filenames are unpredictable
            # MOANA_0113_173_240125092721.bin
            f'--include "*_*_*_{sy}*.bin" '
            f'--include "*_*_*_{sy}*.csv" '
            # Lowell's filenames
            # 3333333_low_20240521_101541.gps
            f'--include "*_*_{y}????_*.gps" '
            f'--include "*_*_{y}????_*.lid" '
            # 3333333_low_20240521_101541_DissolvedOxygen.csv
            f'--include "*_*_{y}????_*_*.csv" '
            f'--include "*_*_{y}????_*_*.cst" '
            # do not upload these for graph test mode
            '--exclude "test_*.csv" '
            '--exclude "test_*.lid" '
            # do not upload these for download test mode
            f'--exclude "{TESTMODE_FILENAME_PREFIX}_*.*" '
            # 2024-07-24T14:11:07Z#nameofboat_track
            f'--include "{y}-*.txt" '
            f'{dr}'
        )

        # run the AWS sync command
        rv = sp.run(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        if rv.returncode:
            lg.a(f"error, {rv.stderr}")
        all_rv += rv.returncode


    # API purposes
    s = 'ok' if all_rv == 0 else 'error'
    ddh_write_timestamp_aws_sqs('aws', s)


    # AWS S3 sync went OK or not
    _t = datetime.datetime.now()
    if all_rv == 0:
        lg.a(f"success: cloud sync on {_t} for year {yyyy}")
        if yyyy_prev == int(yyyy):
            pathlib.Path(yyyy_prev_flag).touch()
            lg.a(f"created last year flag {yyyy_prev_flag} so next runs skip this")
    else:
        lg.a(f"error, cloud sync on {_t}, rv {all_rv}, year {yyyy}")
    return all_rv





def _aws_cp(path):

    # cannot do anything without internet access
    if ddh_net_calculate_via() == 'none':
        lg.a('error, no AWS copy, no internet access')
        return 1

    # check AWS credentials
    _k = ddh_config_get_one_aws_credential_value("cred_aws_key_id")
    _s = ddh_config_get_one_aws_credential_value("cred_aws_secret")
    _n = ddh_config_get_one_aws_credential_value("cred_aws_bucket")
    if _k is None or _s is None or _n is None:
        lg.a("warning, missing credentials")
        return 1
    if not _n.startswith("bkt-"):
        lg.a('warning, bucket name does not start with bkt-')


    # build the AWS COPY command
    _bin = _get_path_of_aws_binary()
    dr = "--dryrun" if dev else ""
    um = path.split('/')[-2]
    f_bn = os.path.basename(path)
    y = datetime.datetime.utcnow().year
    if this_box_has_grouped_s3_uplink():
        lg.a(f'S3 upload-cp GROUPed for folder {um}, year {y}, dry-run = {dev}')
        um = f"{str(y)}/{vessel}/{um}"
    else:
        lg.a(f'S3 upload-cp NON-GROUPed for folder {um}, year {y}, dry-run = {dev}')
    cmd = (
        f"AWS_ACCESS_KEY_ID={_k} AWS_SECRET_ACCESS_KEY={_s} "
        f"timeout 60 {_bin} s3 cp {path} s3://{_n}/{um}/{f_bn} {dr} "
    )


    # run AWS cp command
    rv = sp.run(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    if rv.returncode:
        lg.a(f"error, {rv.stderr}")
        return 1
    lg.a(f"success, S3 copy {os.path.basename(path)}")
    return 0




def aws_sync(past_year=False):
    try:
        _ddh_aws_set_state('busy')
        rv = _aws_sync(past_year)
        s = 'OK' if rv == 0 else 'error'
        _ddh_aws_set_state(s)
    except (Exception, ) as ex:
        lg.a(f'error, aws_sync -> {ex}')
        _ddh_aws_set_state('error')




def _ddh_aws(ignore_gui):

    # prepare AWS process
    r.delete(RD_DDH_GUI_PROCESS_AWS_OUTPUT)
    setproctitle.setproctitle(p_name)
    _ddh_aws_set_state('boot')


    # first, do the past year one
    aws_sync(past_year=True)



    # forever loop waiting requests
    while 1:


        if ddh_this_process_needs_to_quit(ignore_gui, p_name, g_killed):
            sys.exit(0)

        # prevent CPU hog
        time.sleep(1)

        if r.exists(RD_DDH_BLE_SEMAPHORE):
            lg.a('waiting a bit for BLE to finish...')
            while r.exists(RD_DDH_BLE_SEMAPHORE):
                time.sleep(1)


        # AWS COPY individual files
        for i in range(r.llen(q)):
            _, path_to_file_to_cp = r.blpop([q])
            p = path_to_file_to_cp.decode()
            bn = os.path.basename(p)
            if 'MAT.cfg' in bn:
                continue
            dn = os.path.dirname(p).split('/')[-1]
            lg.a(f'copying to bucket file {dn}/{bn}')
            try:
                _aws_cp(p)
            except (Exception,) as ex:
                lg.a(f'error, aws_cp -> {ex}')
                _ddh_aws_set_state('error')


        # AWS SYNC upload every 12 hours or when user deletes the flag
        if not r.exists(RD_DDH_AWS_SYNC_REQUEST):
            aws_sync()
            r.set(RD_DDH_AWS_SYNC_REQUEST, 1)
            r.expire(RD_DDH_AWS_SYNC_REQUEST, 12 * 3600)




def main_ddh_aws(ignore_gui=False):
    signal.signal(signal.SIGINT, _cb_ctrl_c)
    signal.signal(signal.SIGTERM, _cb_kill)

    while 1:
        try:
            _ddh_aws(ignore_gui)
        except (Exception, ) as ex:
            lg.a(f"error, process '{p_name}' restarting after crash -> {ex}")





if __name__ == '__main__':
    # normal run
    main_ddh_aws(ignore_gui=False)

    # for debug on pycharm
    # main_ddh_aws(ignore_gui=True)
