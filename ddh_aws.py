import datetime
import glob
import json
import os
import pathlib
import sys
import setproctitle
import time
import redis
import subprocess as sp

from clear import ddh_write_timestamp_aws_sqs
from ddh.emolt import ddh_this_box_has_grouped_s3_uplink
from ddh.notifications_v2 import notify_error_sw_aws_s3
from ddh.tracking import get_path_current_track_file
from ddh_net import ddh_net_calculate_via
from ddh_sqs import main_ddh_sqs

from utils.redis import (
    RD_DDH_BLE_SEMAPHORE,
    RD_DDH_AWS_NO_EXPIRES_PROCESS_OUTPUT,
    RD_DDH_AWS_NO_EXPIRES_RV,
    RD_DDH_GUI_ON_DEMAND_CHECK_ICON_CLOUD,
    RD_DDH_AWS_NO_EXPIRES_SYNC_USER_REQUEST,
    RD_DDH_AWS_SYNC_PERIODIC_FLAG
)
from utils.ddh_common import (
    NAME_EXE_AWS,
    ddh_get_path_to_folder_dl_files,
    TESTMODE_FILENAME_PREFIX,
    ddh_get_path_to_db_aws_status_file,
    ddh_config_get_vessel_name,
    ddh_config_get_one_aws_credential_value,
    LI_PATH_LAST_YEAR_AWS_TEMPLATE,
    ddh_this_process_needs_to_quit, linux_is_rpi, ddh_get_path_to_root_application_folder)
from ddh_log import lg_aws as lg




# ===================================================================
# ddh_aws
#   - dequeues AWS-CP requests from BLE download (LID + track files)
#   - dequeues AWS-CP requests from CNV for new CSV files
#   - attends AWS sync requests from GUI or periodically
#   - also updates AWS redis state
# ===================================================================



r = redis.Redis('localhost', port=6379)
p_name = NAME_EXE_AWS
vessel = (ddh_config_get_vessel_name()
          .replace("'", "").replace(" ", "_").upper())
dev = not linux_is_rpi()
this_box_has_grouped_s3_uplink = ddh_this_box_has_grouped_s3_uplink()
g_counter_sqs = 0



def _get_path_of_aws_binary():
    # apt install awscli
    # 2024 is 1.22.34
    return "aws"



def _ddh_aws_set_state(s):
    r.set(RD_DDH_AWS_NO_EXPIRES_PROCESS_OUTPUT, s)



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




def _aws_sync(past_year):

    # doing past year AWS sync
    yyyy = datetime.datetime.now().year
    y_p = yyyy - 1
    yyyy_prev_flag = LI_PATH_LAST_YEAR_AWS_TEMPLATE + str(y_p)
    if past_year and os.path.exists(yyyy_prev_flag):
        lg.a(f'warning, skip AWS sync for LAST YEAR {y_p}, flag detected')
        return 0
    if past_year:
        lg.a(f'doing sync for LAST YEAR {y_p}')
        yyyy = y_p


    # check AWS credentials
    _k = ddh_config_get_one_aws_credential_value("cred_aws_key_id")
    _s = ddh_config_get_one_aws_credential_value("cred_aws_secret")
    _n = ddh_config_get_one_aws_credential_value("cred_aws_bucket")
    if _k is None or _s is None or _n is None:
        lg.a("error, missing credentials")
        return 1
    if not _n.startswith("bkt-"):
        lg.a('warning, bucket name does not start with bkt-')



    # cannot do anything without internet access
    if ddh_net_calculate_via() == 'none':
        lg.a('warning, no AWS sync, no internet access')
        return 1



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
        if dev:
            lg.a('warning, AWS dry-run for S3 upload-sync')
        if this_box_has_grouped_s3_uplink:
            um = f"{str(y)}/{vessel}/{um}"

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
        lg.a(f"success, cloud S3 sync on {_t} for year {yyyy}")
        if past_year:
            pathlib.Path(yyyy_prev_flag).touch()
            lg.a(f"created last year flag {yyyy_prev_flag} so next runs skip this")
    else:
        lg.a(f"error, cloud S3 sync on {_t}, rv {all_rv}, year {yyyy}")
    return all_rv





def _aws_cp(path):

    # check AWS credentials
    _k = ddh_config_get_one_aws_credential_value("cred_aws_key_id")
    _s = ddh_config_get_one_aws_credential_value("cred_aws_secret")
    _n = ddh_config_get_one_aws_credential_value("cred_aws_bucket")
    if _k is None or _s is None or _n is None:
        lg.a("warning, missing credentials")
        return 1
    if not _n.startswith("bkt-"):
        lg.a('warning, bucket name does not start with bkt-')


    # cannot do anything without internet access
    if ddh_net_calculate_via() == 'none':
        lg.a('error, no AWS copy, no internet access')
        return 1


    # build the AWS COPY command
    _bin = _get_path_of_aws_binary()
    dr = "--dryrun" if dev else ""
    um = path.split('/')[-2]
    f_bn = os.path.basename(path)
    y = datetime.datetime.utcnow().year
    if dev:
        lg.a('warning, AWS dry-run for S3 upload-cp')
    if this_box_has_grouped_s3_uplink:
        um = f"{str(y)}/{vessel}/{um}"
    cmd = (
        f"AWS_ACCESS_KEY_ID={_k} AWS_SECRET_ACCESS_KEY={_s} "
        f"timeout 60 {_bin} s3 cp {path} s3://{_n}/{um}/{f_bn} {dr} "
    )


    # run AWS cp command
    _ddh_aws_set_state('busy')
    rv = sp.run(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    if rv.returncode:
        lg.a(f"error, S3 copy {os.path.basename(path)}, year {y}, {rv.stderr}")
        _ddh_aws_set_state('error')
        return 1

    lg.a(f"OK, S3 copy {os.path.basename(path)}, year {y}")
    _ddh_aws_set_state('OK')
    return 0




def aws_sync(past_year=False):
    try:
        _ddh_aws_set_state('busy')
        rv = _aws_sync(past_year)
        s = 'OK' if rv == 0 else 'error'
        _ddh_aws_set_state(s)


        # upon AWS error, we create a timestamped entry
        k = RD_DDH_AWS_NO_EXPIRES_RV
        if rv:
            r.set(f'{k}_{int(time.time())}', 1)


        # when too many of these entries, alarm
        ls = list(r.scan_iter(f'{k}_*', count=10))
        if ls:
            lg.a(f'warning, current AWS sync number of errors = {len(ls)}')
        if len(ls) >= 5:
            notify_error_sw_aws_s3()


        # delete the entries when OK or when we notified the alarm
        if rv == 0 or len(ls) >= 5:
            for i in ls:
                r.delete(i)

    except (Exception, ) as ex:
        lg.a(f'error, aws_sync -> {ex}')
        _ddh_aws_set_state('error')




def _ddh_aws(ignore_gui):


    # prepare AWS process
    r.delete(RD_DDH_AWS_NO_EXPIRES_PROCESS_OUTPUT)
    setproctitle.setproctitle(p_name)
    _ddh_aws_set_state('boot')

    if '&' in vessel:
        lg.a('--------------------------------------------------------------')
        lg.a("error, S3 does not like vessel names containing character '&'")
        lg.a('--------------------------------------------------------------')


    # first, do the past year one
    aws_sync(past_year=True)


    # force first AWS sync for the current year
    if r.exists(RD_DDH_AWS_SYNC_PERIODIC_FLAG):
        r.delete(RD_DDH_AWS_SYNC_PERIODIC_FLAG)


    # forever AWS loop waiting requests
    while 1:

        if ddh_this_process_needs_to_quit(ignore_gui, p_name):
            sys.exit(0)


        # prevent CPU hog
        time.sleep(1)

        if r.exists(RD_DDH_BLE_SEMAPHORE):
            lg.a('waiting a bit for BLE to finish ...')
            while r.exists(RD_DDH_BLE_SEMAPHORE):
                time.sleep(1)


        # do SQS from time to time
        global g_counter_sqs
        g_counter_sqs += 1
        if g_counter_sqs == 300:
            g_counter_sqs = 0
            main_ddh_sqs()



        # -------------------------------------------------
        # AWS COPY individual files inside 'upload' folder
        # -------------------------------------------------
        did_aws = False
        ls_aws_copy = glob.glob(f'{ddh_get_path_to_root_application_folder()}/upload/*')
        for link in ls_aws_copy:
            if not os.path.islink(link):
                lg.a(f'error, {link} is not link')
                continue
            p = os.readlink(link)
            bn = os.path.basename(p)
            if 'MAT.cfg' in bn:
                continue
            dn = os.path.dirname(p).split('/')[-1]
            lg.a(f'copying to bucket file {dn}/{bn}')
            did_aws = True
            try:
                _aws_cp(p)
                # SYM: delete the link once file uploaded
                if p.endswith('_track.txt'):
                    yyyymmdd = datetime.datetime.now(datetime.UTC)
                    s_yyyymmdd = yyyymmdd.strftime('%Y-%m-%d')
                    if s_yyyymmdd not in os.path.basename(p):
                        lg.a(f'deleting old track file {bn} AND its link')
                        os.unlink(p)
                    else:
                        lg.a(f'deleting link but NOT today\'s track file {s_yyyymmdd}')
                    os.unlink(link)
                else:
                    # delete the rest
                    lg.a(f'deleting link {link}')
                    os.unlink(link)
            except (Exception,) as ex:
                lg.a(f'error, aws_cp -> {ex}')
                _ddh_aws_set_state('error')


        # user asked for a AWS sync via GUI
        if r.exists(RD_DDH_AWS_NO_EXPIRES_SYNC_USER_REQUEST):
            did_aws = True
            r.delete(RD_DDH_AWS_NO_EXPIRES_SYNC_USER_REQUEST)
            r.setex(RD_DDH_AWS_SYNC_PERIODIC_FLAG, 12 * 3600, 1)
            aws_sync()


        # helps updating GUI
        if did_aws:
            r.set(RD_DDH_GUI_ON_DEMAND_CHECK_ICON_CLOUD, 1)





def main_ddh_aws(ignore_gui=False):


    while 1:
        try:
            _ddh_aws(ignore_gui)
        except (Exception, ) as ex:
            lg.a(f"error, process '{p_name}' restarting after crash -> {ex}")





if __name__ == '__main__':

    # normal run
    main_ddh_aws(ignore_gui=False)

    # for debug on pycharm
    #main_ddh_aws(ignore_gui=True)
