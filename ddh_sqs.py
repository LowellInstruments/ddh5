import signal
import sys

import setproctitle
import time
import redis
from mat.utils import linux_is_rpi
from rd_ctt.ddh import RD_DDH_SQS_FINISH_BOOT
from utils.ddh_common import (
    ddh_config_get_vessel_name,
    NAME_EXE_SQS, ddh_config_is_sqs_enabled,
    ddh_this_process_needs_to_quit, exp_get_use_debug_print
)
from ddh_log import lg_aws as lg
import glob
import os
import uuid
import boto3
import json
from ddh_aws import ddh_write_timestamp_aws_sqs
from ddh_net import ddh_net_calculate_via
from ddh_log import lg_sqs as lg
from utils.ddh_common import (
    ddh_get_path_to_folder_sqs,
    ddh_config_get_one_aws_credential_value,
)
import warnings




# =================================================
# ddh_sqs
# periodically sends SQS local files to DDN
# =================================================



# remove ugly prints
warnings.filterwarnings("ignore",
                        category=FutureWarning,
                        module="botocore.client")



# used when S3 and SQS keys are the same or when developing
sqs_key_id = (ddh_config_get_one_aws_credential_value("cred_aws_key_id") or
              os.getenv('CRED_AWS_KEY_ID'))
sqs_access_key = (ddh_config_get_one_aws_credential_value("cred_aws_secret") or
                  os.getenv('CRED_AWS_SECRET'))



# only used when S3 and SQS keys are different
custom_sqs_key_id = ddh_config_get_one_aws_credential_value("cred_aws_custom_sqs_key_id")
custom_sqs_access_key = ddh_config_get_one_aws_credential_value("cred_aws_custom_sqs_access_key")
if custom_sqs_key_id:
    sqs_key_id = custom_sqs_key_id
if custom_sqs_access_key:
    sqs_access_key = custom_sqs_access_key




# global variables
sqs = boto3.client(
    "sqs",
    region_name="us-east-2",
    aws_access_key_id=sqs_key_id,
    aws_secret_access_key=sqs_access_key,
)
r = redis.Redis('localhost', port=6379)
p_name = NAME_EXE_SQS
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



def _sqs_serve():

    if not ddh_config_is_sqs_enabled():
        lg.a("warning, sqs_en = False")
        return


    if ddh_net_calculate_via() == "none":
        return


    # grab / collect SQS files to send
    fol = ddh_get_path_to_folder_sqs()
    files = glob.glob(f"{fol}/*.sqs")
    if files:
        lg.a(f"serving {len(files)} SQS files")



    # -----------------------------
    # loop through SQS local files
    # -----------------------------

    for i_f in files:

        # this happens not often but did once
        if os.path.getsize(i_f) == 0:
            lg.a(f'error, file {i_f} has file length zero')
            os.unlink(i_f)
            continue


        # reads each local SQS file as JSON
        try:
            f = open(i_f, "r")
            j = json.load(f)
        except (Exception, ) as ex:
            lg.a(f'error, SQS file {i_f} cannot be JSON decoded -> {ex}')
            os.unlink(i_f)
            lg.a(f'warning, deleted SQS file {i_f}')
            continue


        # display basename
        _bn = os.path.basename(i_f)
        lg.a(f"serving file {_bn}")


        try:
            # ENQUEUES the JSON as string to SQS service
            m = json.dumps(j)
            rsp = sqs.send_message(
                QueueUrl=ddh_config_get_one_aws_credential_value("cred_aws_sqs_queue_name"),
                MessageGroupId=str(uuid.uuid4()),
                MessageDeduplicationId=str(uuid.uuid4()),
                MessageBody=m,
            )

            md = rsp["ResponseMetadata"]
            if md and int(md["HTTPStatusCode"]) == 200:
                # delete SQS file
                os.unlink(i_f)
                # tell status database for API all went fine
                ddh_write_timestamp_aws_sqs('sqs', 'ok')
            else:
                lg.a(f"error, not sent msg\n\t{m}")


        except (Exception,) as ex:
            lg.a(f"error sqs_serve: {ex}")
            ddh_write_timestamp_aws_sqs('sqs', f'error {str(ex)}')

        finally:
            if f:
                f.close()




def _ddh_sqs(ignore_gui):

    # prepare SQS process
    setproctitle.setproctitle(p_name)
    r.set(RD_DDH_SQS_FINISH_BOOT, 1)


    # forever loop serving local SQS files, do not hog CPU
    while 1:
        if ddh_this_process_needs_to_quit(ignore_gui, p_name, g_killed):
            sys.exit(0)

        time.sleep(1)
        _sqs_serve()






def main_ddh_sqs(ignore_gui=False):
    signal.signal(signal.SIGINT, _cb_ctrl_c)
    signal.signal(signal.SIGTERM, _cb_kill)

    lg.set_debug(exp_get_use_debug_print())

    while 1:
        try:
            _ddh_sqs(ignore_gui)
        except (Exception,) as ex:
            print(f"AWS: error, process '{p_name}' restarting after crash -> {ex}")




if __name__ == '__main__':

    # normal run
    main_ddh_sqs(ignore_gui=False)

    # for debug on pycharm
    # main_ddh_sqs(ignore_gui=True)
