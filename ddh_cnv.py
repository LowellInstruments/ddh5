import glob
import os
import time
import redis
from ddh.graph_draw import graph_request
from lix.lix import parse_lid_v2_data_file
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
from utils.redis import (
    RD_DDH_CNV_QUEUE,
    RD_DDH_GUI_PLOT_REASON, RD_DDH_GUI_PLOT_FOLDER,
    RD_DDH_GUI_NO_EXPIRES_PERIODIC_REFRESH_HISTORY_TABLE
)
from utils.ddh_common import (
    TESTMODE_FILENAME_PREFIX,
    ddh_get_path_to_folder_dl_files,
    ddh_get_path_to_root_application_folder,
    ddh_get_path_to_db_new_history_file,
    ddh_summarize_csv_file
)
from ddh_log import lg_cnv as lg



# =========================================================
# ddh_cnv
#   - dequeues requests to convert LID to CSV from BLE
#   - creates CSV symlinks for  AWS copy queue
#   - also enqueues new requests to plot
# =========================================================



r = redis.Redis('localhost', port=6379)
PERIOD_CNV_SECS = 3600 * 12
BAROMETRIC_PRESSURE_SEA_LEVEL_IN_DECIBAR = 10.1
DDH_BPSL = BAROMETRIC_PRESSURE_SEA_LEVEL_IN_DECIBAR



def _lid_v1_file_has_sensor_data_type(path, suffix):
    if suffix == '_TDO':
        # this cannot be
        return None
    _map = {
        "_DissolvedOxygen": "DOS",
        "_Temperature": "TMP",
        "_Pressure": "PRS"}
    header = load_data_file(path).header()
    return header.tag(_map[suffix])



def _convert_lid_file_v1(f, suf):
    if id_lid_file_flavor(f) != LID_FILE_V1:
        return 1
    bn = os.path.basename(f)
    dn = os.path.dirname(f).split('/')[-1]
    lg.a(f"converting LID file v1 {dn}/{bn} for suffix {suf}")

    # check v1 file header to skip files w/o this sensor data / suffix
    if not _lid_v1_file_has_sensor_data_type(f, suf):
        lg.a(f'warning, skip v1 conversion, file {dn}/{bn} has no {suf} data')
        return 1

    # old v1 conversion
    _params = default_parameters()
    DataConverter(f, _params).convert()
    lg.a(f"OK, converted LID file v1 {dn}/{bn} for suffix {suf}")
    return 0



def _convert_lid_file_v2(f, suf):
    if id_lid_file_flavor(f) != LID_FILE_V2:
        return 1
    if not lid_file_v2_has_sensor_data_type(f, suf):
        return 1
    bn = os.path.basename(f)
    dn = os.path.dirname(f).split('/')[-1]
    lg.a(f"converting LID file v2 {dn}/{bn} suffix {suf}")
    rv = parse_lid_v2_data_file(f)
    lg.a(f"OK, converted LID file v2 {dn}/{bn} suffix {suf}")
    return rv





def _convert_lid_file(p):

    for suf in ("_DissolvedOxygen", "_Temperature", "_Pressure", "_TDO", "_CTD"):
        if os.path.basename(p).startswith('test'):
            return 1, ''
        if TESTMODE_FILENAME_PREFIX in os.path.basename(p):
            return 1, ''
        if not p.endswith('.lid'):
            bn = os.path.basename(p)
            lg.a(f'error, filename {bn} does not end in .lid')
            return 1, ''


        # SKIP when CSV files already exist
        f_csv = f"{p.split('.')[0]}{suf}.csv"
        if os.path.exists(f_csv):
            bn = os.path.basename(p)
            lg.a(f'CSV file already exists for {bn}')
            return 1, ''


        # try to convert LID file
        try:
            rv_v1 = _convert_lid_file_v1(p, suf)
            rv_v2 = _convert_lid_file_v2(p, suf)
            if rv_v1 == 0 or rv_v2 == 0:
                graph_request(reason='ble')

                # ----------------------------------------------------------
                # SYM: create a symlink for AWS to know to upload CSV file
                # ----------------------------------------------------------
                fol = str(ddh_get_path_to_root_application_folder())
                os.makedirs(f'{fol}/upload', exist_ok=True)
                f_csv = p.replace('.lid', f'{suf}.csv')
                link_csv = f'{fol}/upload/{os.path.basename(f_csv)}'
                if not os.path.exists(link_csv):
                    os.symlink(f_csv, link_csv)
                return 0, f_csv

        except (ValueError, Exception) as ex:
            bn = os.path.basename(p)
            lg.a(f"error, converting file {bn}, metric {suf} --> {str(ex)}")
            return 1, ''



def _boot_cnv():

    # upon boot, enqueue LID files w/o proper CSV to our own CNV queue
    fol = ddh_get_path_to_folder_dl_files()
    mask_all_lid = f'{fol}/**/*.lid'
    ls_lid = glob.glob(mask_all_lid, recursive=True)
    for pb in ls_lid:
        pc = pb.replace('.lid', '')
        mask_one_csv = f'{pc}*.csv'
        ls_csv = glob.glob(mask_one_csv, recursive=True)
        if not ls_csv:
            bn = os.path.basename(pb)
            lg.a(f'boot, push {bn} to own queue')
            r.rpush(RD_DDH_CNV_QUEUE, pb)





def _ddh_cnv():

    r.delete(RD_DDH_CNV_QUEUE)
    _boot_cnv()


    while 1:

        # prevent CPU hog
        time.sleep(1)


        # dequeue messages that may contain '&' or not
        ls_converted_files = []
        q = RD_DDH_CNV_QUEUE
        for i in range(r.llen(q)):
            _, p = r.blpop([q])
            p = p.decode()
            sn = ''
            dt_s = ''
            e = ''
            rr = ''
            if '&' in p:
                p, sn, dt_s, e, rr = p.split('&')

            bn = os.path.basename(p)
            lg.a(f'dequeuing file {bn}')


            # --------------------------------
            # convert LID file from queue
            # 1) at CNV booting  (SN empty)
            # 2) at BLE download (SN filled)
            # --------------------------------

            rv, path_csv = _convert_lid_file(p)
            if rv == 0:
                ls_converted_files.append(p)
                if sn and 'ok' in e.lower():
                    try:
                        lg.a(f'doing summary for file {os.path.basename(path_csv)}')
                        summary = ddh_summarize_csv_file(path_csv)

                        # download BLE OK to history
                        # search for 'download BLE ERR to history'
                        path_file_history = ddh_get_path_to_db_new_history_file()
                        with open(path_file_history, 'a') as f:
                            f.write(f'{sn.lower()},{dt_s},{e},{rr},{summary}\n')
                    except Exception as ex:
                        lg.a(f'error, csv_do_summary -> {ex}')
                    finally:
                        r.set(RD_DDH_GUI_NO_EXPIRES_PERIODIC_REFRESH_HISTORY_TABLE, 1)


            else:
                lg.a(f'error, file {bn}')


        # plot
        for pb in ls_converted_files:
            mask = pb.replace('.lid', '') + '*.csv'
            ls_csv = glob.glob(mask)
            for pc in ls_csv:
                bn = os.path.basename(str(pc))
                dn = os.path.dirname(str(pc))
                lg.a(f'post conversion plot = {bn}')
                r.set(RD_DDH_GUI_PLOT_REASON, 'BLE')
                r.set(RD_DDH_GUI_PLOT_FOLDER, dn)




def main_ddh_cnv():
    while 1:
        try:
            _ddh_cnv()
        except (Exception, ) as ex:
            lg.a(f"error, thread CNV restarting after crash -> {ex}")




if __name__ == '__main__':
    main_ddh_cnv()

