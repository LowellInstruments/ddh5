import glob
import os
import signal
import sys

import setproctitle
import time
import redis
from ddh.draw_graph import graph_request
from ddh.utils_graph import utils_graph_classify_file_wc_mode
from mat.data_converter import (
    default_parameters,
    DataConverter
)
from mat.data_file_factory import load_data_file
from mat.lix import (
    id_lid_file_flavor,
    LID_FILE_V1, LID_FILE_V2,
    lid_file_v2_has_sensor_data_type
)
from mat.lix_pr import convert_lix_file
from mat.utils import linux_is_rpi
from rd_ctt.ddh import (
    RD_DDH_CNV_QUEUE,
    RD_DDH_AWS_COPY_QUEUE, RD_DDH_GUI_PLOT_REASON, RD_DDH_GUI_PLOT_FOLDER
)
from utils.ddh_common import (
    NAME_EXE_CNV,
    TESTMODE_FILENAME_PREFIX, ddh_get_path_to_folder_dl_files, ddh_this_process_needs_to_quit, exp_get_use_debug_print
)
from ddh_log import lg_cnv as lg



# =========================================================
# ddh_cnv
#   - dequeues requests to convert LID to CSV from BLE
#   - enqueues new CSV files to AWS copy queue
#   - also classify files for Water Column mode
#   - also enqueues new requests to plot
# =========================================================



r = redis.Redis('localhost', port=6379)
p_name = NAME_EXE_CNV
PERIOD_CNV_SECS = 3600 * 12
BAROMETRIC_PRESSURE_SEA_LEVEL_IN_DECIBAR = 10.1
DDH_BPSL = BAROMETRIC_PRESSURE_SEA_LEVEL_IN_DECIBAR
g_killed = False



def _cb_kill(n, _):
    print(f'{p_name}: captured signal kill', flush=True)
    global g_killed
    g_killed = True



def _cb_ctrl_c(n, _):
    print(f'{p_name}: captured signal ctrl + c', flush=True)
    global g_killed
    g_killed = True



def _lid_v1_file_has_sensor_data_type(path, suffix):
    if suffix == '_TDO':
        return
    _map = {
        "_DissolvedOxygen": "DOS",
        "_Temperature": "TMP",
        "_Pressure": "PRS"}
    header = load_data_file(path).header()
    return header.tag(_map[suffix])



def _convert_lid_file_v1(f, suf):
    if id_lid_file_flavor(f) != LID_FILE_V1:
        return 1
    lg.a(f"converting LID file v1 {f} for suffix {suf}")

    # check v1 file header to skip files w/o this sensor data / suffix
    if not _lid_v1_file_has_sensor_data_type(f, suf):
        bn = os.path.basename(f)
        lg.a(f'warning, skip v1 conversion because file {bn} has no {suf} data')
        return 1

    # do the v1 conversion
    _params = default_parameters()
    DataConverter(f, _params).convert()
    lg.a(f"OK: converted LID file v1 {f} for suffix {suf}")
    return 0



def _convert_lid_file_v2(f, suf):
    if id_lid_file_flavor(f) != LID_FILE_V2:
        return 1
    if not lid_file_v2_has_sensor_data_type(f, suf):
        return 1
    lg.a(f"converting LID file v2 {f} suffix {suf}")
    rv = convert_lix_file(f)
    lg.a(f"OK: converted LID file v2 {f} suffix {suf}")
    return rv



def _convert_file(p):

    for suf in ("_DissolvedOxygen", "_Temperature", "_Pressure", "_TDO"):
        if os.path.basename(p).startswith('test'):
            return 1
        if TESTMODE_FILENAME_PREFIX in os.path.basename(p):
            return 1
        if not p.endswith('.lid'):
            bn = os.path.basename(p)
            lg.a(f'error, filename {bn} does not end in .lid')
            return 1


        # SKIP when CSV files already exist
        f_csv = f"{p.split('.')[0]}{suf}.csv"
        if os.path.exists(f_csv):
            bn = os.path.basename(p)
            lg.a(f'CSV file already exists for {bn}')
            return 0


        # try to convert LID file
        try:
            rv_v1 = _convert_lid_file_v1(p, suf)
            rv_v2 = _convert_lid_file_v2(p, suf)
            if rv_v1 == 0 or rv_v2 == 0:
                graph_request(reason='ble')
                return 0
        except (ValueError, Exception) as ex:
            bn = os.path.basename(p)
            lg.a(f"error, converting file {bn}, metric {suf} --> {str(ex)}")
            return 1



def _boot_cnv():

    # upon boot, enqueue to our own CNV queue
    fol = ddh_get_path_to_folder_dl_files()
    mask_all_lid = f'{fol}/**/*.lid'
    ls_lid = glob.glob(mask_all_lid, recursive=True)
    for pb in ls_lid:
        pc = pb.replace('.lid', '')
        mask_one_csv = f'{pc}*.csv'
        ls_csv = glob.glob(mask_one_csv, recursive=True)
        if not ls_csv:
            bn = os.path.basename(pb)
            lg.a(f'debug, boot push {bn} to CNV queue')
            r.rpush(RD_DDH_CNV_QUEUE, pb)


    # upon boot, CSV to FMG / SMG
    ls_tdo = glob.glob(f'{fol}/**/*_TDO.csv', recursive=True)
    ls_dox = glob.glob(f'{fol}/**/*_DissolvedOxygen.csv', recursive=True)
    ls = ls_tdo + ls_dox
    for i in ls:
        utils_graph_classify_file_wc_mode(i)





def _ddh_cnv(ignore_gui):

    # prepare CNV process
    r.delete(RD_DDH_CNV_QUEUE)
    setproctitle.setproctitle(p_name)
    _boot_cnv()


    # forever loop collecting CNV requests
    while 1:


        if ddh_this_process_needs_to_quit(ignore_gui, p_name, g_killed):
            sys.exit(0)


        # prevent CPU hog
        time.sleep(1)


        # this queue has files when 1) CNV boot 2) BLE downloads
        ls_converted_files = []
        q = RD_DDH_CNV_QUEUE
        for i in range(r.llen(q)):
            _, p = r.blpop([q])
            p = p.decode()
            bn = os.path.basename(p)
            lg.a(f'dequeing and converting file {bn}')
            rv = _convert_file(p)
            if rv == 0:
                ls_converted_files.append(p)
            else:
                lg.a(f'error, file {p}')


        # push to AWS COPY queue any new CSV file
        for pb in ls_converted_files:
            mask = pb.replace('.lid', '') + '*.csv'
            ls_csv = glob.glob(mask)
            for pc in ls_csv:
                bn = os.path.basename(pc)
                lg.a(f'debug, push {bn} to AWS COPY queue')
                r.rpush(RD_DDH_AWS_COPY_QUEUE, pc)
                lg.a(f'debug, analyzing water mode for {bn}')
                utils_graph_classify_file_wc_mode(pc)
                lg.a(f'debug, plotting newly converted file {bn}')
                r.set(RD_DDH_GUI_PLOT_REASON, 'BLE')
                fol = os.path.dirname(pc)
                r.set(RD_DDH_GUI_PLOT_FOLDER, fol)




def main_ddh_cnv(ignore_gui=False):
    signal.signal(signal.SIGINT, _cb_ctrl_c)
    signal.signal(signal.SIGTERM, _cb_kill)

    while 1:
        try:
            _ddh_cnv(ignore_gui)
        except (Exception, ) as ex:
            lg.a(f"CNV: error, process '{p_name}' restarting after crash -> {ex}")




if __name__ == '__main__':
    # normal run
    # main_ddh_cnv(ignore_gui=False)

    # for debug on pycharm
    main_ddh_cnv(ignore_gui=True)
