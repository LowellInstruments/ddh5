import glob
import os
from pathlib import Path
from ddh.timecache import is_it_time_to
from utils.ddh_common import (
    ddh_get_path_to_folder_dl_files,
    ddh_get_path_to_folder_lef,
    TESTMODE_FILENAME_PREFIX, ddh_config_get_vessel_name, ddh_config_does_flag_file_download_test_mode_exist,
)
from ddh_log import lg_trk as lg



g_last_track_ts_unit = ''
g_last_track_file_name = ''
vessel_name = ddh_config_get_vessel_name()



# --------------------------------------
# these TRACKING logs get uploaded
# they are based on UTC, not local time
# --------------------------------------
def ddh_log_tracking_add(lat, lon, tg):

    if not is_it_time_to("track_boat_gps", t=10):
        return
    if not lat:
        lg.a("error, ddh_log_tracking_add() no lat")
        return
    if not tg:
        lg.a("error, ddh_log_tracking_add() no tg")
        return


    # how often filename rotates, compare between runs
    global g_last_track_ts_unit
    flag_new_file = g_last_track_ts_unit != tg.strftime("%d")
    g_last_track_ts_unit = tg.strftime("%d")


    # create TRACKING log folder if it does not exist
    v = vessel_name.replace(" ", "_")
    d = str(ddh_get_path_to_folder_dl_files())
    d = f"{d}/ddh#{v}/"
    Path(d).mkdir(parents=True, exist_ok=True)


    # get the filename, either new or re-use previous one
    tg = tg.replace(microsecond=0)
    iso_tg = tg.isoformat()
    str_iso_tg_tz_utc = f'{iso_tg}Z'
    global g_last_track_file_name
    file_out = g_last_track_file_name
    if flag_new_file:
        if g_last_track_file_name:
            lg.a("closing current tracking file due to rotation")
        file_out = f'{d}{str_iso_tg_tz_utc}#{v}_track.txt'
        _bn = os.path.basename(file_out)
        lg.a(f"started new tracking file {_bn}")
        g_last_track_file_name = file_out
    if ddh_config_does_flag_file_download_test_mode_exist():
        file_out = os.path.dirname(file_out) + '/' + \
                   TESTMODE_FILENAME_PREFIX + os.path.basename(file_out)


    # write the tracking line alone
    lat = '{:.6f}'.format(float(lat))
    lon = '{:.6f}'.format(float(lon))
    with open(file_out, 'a') as f:
        f.write(f"{str_iso_tg_tz_utc},{lat},{lon}\n")


    # add info from LEF files to the TRACK file, if so
    ff_lef = glob.glob(f"{ddh_get_path_to_folder_lef()}/*.lef")
    for f_lef in ff_lef:
        with open(f_lef, 'r') as fl:
            j = fl.read()
            with open(file_out, 'a') as fo:
                fo.write(f"{str_iso_tg_tz_utc},{lat},{lon}***{j}\n")

        # delete the LEF file
        _bn = os.path.basename(f_lef)
        lg.a(f"deleting LEF file {_bn}")
        os.unlink(f_lef)


def get_path_current_track_file():
    return g_last_track_file_name
