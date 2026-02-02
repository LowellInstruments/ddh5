import os
import asyncio
import copy
import glob
import pathlib
import redis
import time
import git
import socket
from pathlib import Path
from git import InvalidGitRepositoryError
import toml
import subprocess as sp
from rd_ctt.ddh import (
    RD_DDH_GUI_STATE_EVENT_CODE,
    RD_DDH_GUI_STATE_EVENT_TEXT,
)



STR_NOTE_PURGE_BLACKLIST = "Purge all loggers' lock-out time?"
STR_NOTE_GPS_BAD = "Skipping logger until valid GPS fix is obtained"
TESTMODE_FILENAME_PREFIX = 'testfile_'


NAME_EXE_DDH = "ddh_main"
NAME_EXE_LOG = 'ddh_log'
NAME_EXE_CNV = 'ddh_cnv'
NAME_EXE_NET = 'ddh_net'
NAME_EXE_AWS = 'ddh_aws'
NAME_EXE_SQS = 'ddh_sqs'
NAME_EXE_GPS = 'ddh_gps'
NAME_EXE_BLE = 'ddh_ble'
NAME_EXE_BTN = 'ddh_btn'
NAME_EXE_API = "main_api"
NAME_EXE_BRT = "main_brt"
DDN_API_IP = 'ddn.lowellinstruments.com'
DDN_API_PORT = 9000



_sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
r = redis.Redis('localhost')
ael = asyncio.get_event_loop()



def ddh_is_gui_running():
    # we DONT import MAT library in ddh_common
    cmd = f'ps -aux | grep -w {NAME_EXE_DDH} | grep -v grep'
    rv = sp.run(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    return rv.returncode == 0



def ddh_this_process_needs_to_quit(ignore_gui, p_name):
    if ignore_gui:
        return False
    if ddh_is_gui_running():
        return False
    print(f"debug, process '{p_name}' ends because no GUI")
    return True




def ddh_get_path_to_folder_gui_res() -> Path:
    p = str(ddh_get_path_to_root_application_folder())
    return Path(f"{p}/ddh/gui/res")



def ddh_do_we_graph_out_of_water_data():
    return not os.path.exists(LI_PATH_PLT_ONLY_INSIDE_WATER)



def ddh_get_path_to_app_override_flag_file() -> str:
    # set this with the clear-lockout physical button
    # to force at least one execution even with
    # boat not moving on haul mode
    return TMP_PATH_DDH_APP_OVERRIDE



def ddh_get_template_of_path_of_hbw_flag_file() -> str:
    # works with the clear-lockout physical button
    # to force download even when logger has not been in water
    return TMP_PATH_DDH_HBW



def ddh_get_path_to_db_history_file() -> str:
    p = str(ddh_get_path_to_root_application_folder())
    return f"{p}/ddh/db/db_his.json"



def ddh_get_path_to_db_aws_status_file() -> str:
    p = str(ddh_get_path_to_root_application_folder())
    return f"{p}/ddh/db/db_status.json"



def ddh_get_local_software_commit_id():
    try:
        _r = git.Repo(".")
        c = _r.head.commit
        return str(c)[:5]
    except InvalidGitRepositoryError:
        return "none"



def ddh_get_local_software_version():
    try:
        with open(LI_PATH_DDH_VERSION, 'r') as f:
            return f.readline().replace('\n', '')
    except (Exception, ):
        return 'error_get_version'



def ddh_get_path_to_folder_dl_files() -> Path:
    p = str(ddh_get_path_to_root_application_folder())
    return Path(f"{p}/dl_files")



def ddh_get_path_to_folder_logs() -> Path:
    p = str(ddh_get_path_to_root_application_folder())
    return Path(p) / "logs"



def ddh_get_path_to_folder_macs() -> Path:
    p = str(ddh_get_path_to_root_application_folder())
    return Path(f"{p}/ddh/macs")



def ddh_get_path_to_folder_macs_black() -> Path:
    return ddh_get_path_to_folder_macs() / "black"



def ddh_get_path_to_folder_macs_orange() -> Path:
    return ddh_get_path_to_folder_macs() / "orange"



def ddh_get_path_to_folder_sqs() -> Path:
    p = str(ddh_get_path_to_root_application_folder())
    return Path(f"{p}/ddh/sqs")



def ddh_get_path_to_folder_lef() -> Path:
    p = str(ddh_get_path_to_root_application_folder())
    return Path(f"{p}/ddh/lef")



def ddh_get_path_to_folder_settings() -> Path:
    p = str(ddh_get_path_to_root_application_folder())
    return Path(f"{p}/settings")



def ddh_get_path_to_folder_tweak() -> Path:
    p = str(ddh_get_path_to_root_application_folder())
    return Path(f"{p}/ddh/tweak")



def ddh_get_path_to_folder_scripts() -> pathlib.Path:
    p = str(ddh_get_path_to_root_application_folder())
    return Path(f"{p}/scripts")



def calculate_mac_address_from_folder_within_dl_files(fol):
    """returns '11:22:33' from 'dl_files/11-22-33'"""
    fol = str(fol)
    try:
        return fol.split("/")[-1].replace("-", ":")
    except (ValueError, Exception):
        return None



def calculate_path_to_folder_within_dl_files_from_mac_address(mac):
    """returns 'dl_files/11-22-33' from '11:22:33'"""
    fol = ddh_get_path_to_folder_dl_files()
    fol = fol / f'{mac.replace(":", "-").upper()}/'
    return fol




def create_path_to_folder_dl_files_from_mac(mac):
    """mkdir folder based on MAC address, replaces ':' with '-'"""
    fol = ddh_get_path_to_folder_dl_files()
    fol = fol / f'{mac.replace(":", "-").upper()}/'
    os.makedirs(fol, exist_ok=True)
    return fol



def get_total_number_of_hauls(path):
    # path: /home/kaz/PycharmProjects/ddh/dl_files/<mac>
    ls_lid = len(glob.glob(f'{path}/*.lid'))
    ls_bin = (len(glob.glob(f'{path}/moana*.bin')) +
              len(glob.glob(f'{path}/MOANA*.bin')))
    mask = '__what__'
    if ls_lid:
        # for DO & TP & TDO loggers
        mask_do = f'{path}/*_DissolvedOxygen.csv'
        mask_mat = f'{path}/*_Pressure.csv'
        mask_tdo = f'{path}/*_TDO.csv'
        n_do = len(glob.glob(mask_do))
        n_tdo = len(glob.glob(mask_tdo))
        if n_tdo:
            mask = mask_tdo
        elif n_do:
            mask = mask_do
        else:
            mask = mask_mat
    elif ls_bin:
        # NOT MOANA*.csv but Lowell generated files
        mask = f'{path}/*_Pressure.csv'

    # example, when no .LID or .BIN files downloaded
    n = len(glob.glob(mask))
    # bn = os.path.basename(path)
    # print(f"debug, get_number_of_hauls = {n} for {bn}, mask {os.path.basename(mask)}")
    return n



def linux_is_rpi(i=""):
    # we DONT import MAT library in ddh_common
    cmd = f'cat /proc/cpuinfo | grep aspberry'
    if i:
        cmd = cmd + f' Pi {i}'
    rv = sp.run(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    return rv.returncode == 0



def linux_is_rpi3():
    return linux_is_rpi(3)



def linux_is_rpi4():
    return linux_is_rpi(4)




def ddh_get_path_to_root_application_folder() -> Path:
    if linux_is_rpi():
        return Path(str(pathlib.Path.home()) + '/li/ddh')
    return Path(str(pathlib.Path.home()) + '/PycharmProjects/ddh')




def get_ddh_platform():
    if linux_is_rpi3():
        return "rpi3"
    elif linux_is_rpi4():
        return "rpi4"
    elif linux_is_rpi():
        return "rpi"
    return "unk"






FILE_ALL_MACS_TOML = f"{str(ddh_get_path_to_folder_settings())}/all_macs.toml"
FILE_DO_NOT_RERUN_TOML = "/tmp/ddh_do_not_rerun_flag.toml"




def ddh_get_contents_of_config_file_all_macs():
    try:
        with open(FILE_ALL_MACS_TOML, 'r') as f:
            # d: {'11:22:33:44:55:66': 'sn1234567'}
            return toml.load(f)
    except (Exception,) as ex:
        print('error, ddh_get_contents_of_config_file_all_macs: ', ex)
        os._exit(1)



def ddh_does_do_not_rerun_file_flag_exist():
    return os.path.exists(FILE_DO_NOT_RERUN_TOML)



def ddh_create_do_not_rerun_file_flag():
    pathlib.Path(FILE_DO_NOT_RERUN_TOML).touch()



def ddh_clear_do_not_rerun_file_flag():
    try:
        os.unlink(FILE_DO_NOT_RERUN_TOML)
    except (Exception, ) as ex:
        print(f'error clr_ddh_rerun_flag_li -> {ex}')



def sh(c):
    rv = sp.run(c, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    return rv.returncode




def ddh_get_path_to_config_file():
    p = pathlib.Path.home()
    if sh('cat /proc/cpuinfo | grep aspberry') == 0:
        return str(p) + '/li/ddh/settings/config.toml'
    return str(p) + '/PycharmProjects/ddh/settings/config.toml'



def ddh_config_load_file():
    try:
        p = ddh_get_path_to_config_file()
        with open(p, 'r') as f:
            c = toml.load(f)
            for k, v in c['monitored_macs'].items():
                if '-' in k:
                    print('error, "-" symbol in monitored macs, use ":"')
                    time.sleep(2)
                    os._exit(1)
                if type(k) is not str:
                    print(f'error, {k} in config file is not a string')
                    time.sleep(2)
                    os._exit(1)
                if type(v) is not str:
                    print(f'error, {v} in config file is not a string')
                    time.sleep(2)
                    os._exit(1)
            return c
    except (Exception, ) as ex:
        print('error, cfg_load_from_file: ', ex)
        os._exit(1)



def ddh_config_save_to_file(c):
    try:
        p = ddh_get_path_to_config_file()
        with open(p, 'w') as f:
            toml.dump(c, f)
    except (Exception, ) as ex:
        print('error, cfg_save_to_file: ', ex)
        os._exit(1)



cfg = ddh_config_load_file()



def ddh_config_get_vessel_name():
    return cfg['behavior']['ship_name']



def ddh_config_get_is_aws_s3_enabled():
    return cfg['flags']['aws_en']



def ddh_config_is_skip_in_port_enabled():
    rv = cfg['flags']['skip_dl_in_port_en']
    return rv



def ddh_config_does_flag_file_graph_test_mode_exist():
    return os.path.exists(TMP_PATH_GRAPH_TEST_MODE_JSON)



def ddh_config_does_flag_file_download_test_mode_exist():
    return os.path.exists(LI_PATH_TEST_MODE)



def ddh_config_is_gps_error_forced_enabled():
    return cfg['flags']['hook_gps_error_measurement_forced']



def ddh_config_get_list_of_monitored_serial_numbers():
    return list(cfg['monitored_macs'].values())



def ddh_config_get_list_of_monitored_macs():
    ls = list(cfg['monitored_macs'].keys())
    return [i.upper() for i in ls]



def ddh_create_needed_folders():
    fol = ddh_get_path_to_folder_macs()
    os.makedirs(fol, exist_ok=True)
    fol = ddh_get_path_to_folder_macs_black()
    os.makedirs(fol, exist_ok=True)
    fol = ddh_get_path_to_folder_macs_orange()
    os.makedirs(fol, exist_ok=True)
    fol = ddh_get_path_to_folder_sqs()
    os.makedirs(fol, exist_ok=True)
    fol = ddh_get_path_to_folder_lef()
    os.makedirs(fol, exist_ok=True)
    fol = ddh_get_path_to_folder_dl_files()
    os.makedirs(fol, exist_ok=True)
    fol = ddh_get_path_to_folder_logs()
    os.makedirs(fol, exist_ok=True)



def ddh_config_get_monitored_pairs():
    return cfg['monitored_macs']



def ddh_config_get_gps_fake_position():
    return cfg['behavior']['fake_gps_position']



def ddh_config_get_forget_time_seconds():
    return int(cfg['behavior']['forget_time'])



def ddh_config_get_logger_sn_from_mac(mac):
    mac = mac.upper()

    # happens when g_graph_test_mode()
    test_graph_d = {
        '00:00:00:00:00:00': 'test000',
        '11:22:33:44:55:66': 'test111',
        '99:99:99:99:99:99': 'test999',
        '55:55:55:55:55:55': 'test555',
        '33:33:33:33:33:33': 'test333'
    }
    if mac in test_graph_d.keys():
        return test_graph_d[mac]

    # do it like this to avoid case errors
    for k, v in cfg['monitored_macs'].items():
        if mac == k.upper():
            return v.upper()



def ddh_config_get_logger_mac_from_sn(sn):
    sn = sn.upper()

    # happens when g_graph_test_mode()
    test_graph_d = {
        'test000': '00:00:00:00:00:00',
        'test111': '11:22:33:44:55:66',
        'test999': '99:99:99:99:99:99',
        'test555': '55:55:55:55:55:55',
        'test333': '33:33:33:33:33:33',
    }
    if sn in test_graph_d.keys():
        return test_graph_d[sn]

    # do it like this to avoid case errors
    for k, v in cfg['monitored_macs'].items():
        if sn == v.upper():
            return k.upper()



def ddh_config_get_language_index():
    # 0 en 1 pt 2 fr 3 ca 4 pl 5 sp
    try:
        return cfg['behavior']['language']
    except KeyError:
        # print('\033[33mwarning, defaulting to language english\033[0m')
        return 0



def ddh_config_get_language_str_by_index(i):
    d_lang = {0: 'en', 1: 'pt', 2: 'fr', 3: 'ca', 4: 'pl', 5: 'sp'}
    return d_lang.get(i, 'en')



def ddh_config_contains_monitored_lowell_loggers():
    d_macs = cfg['monitored_macs']
    if not d_macs:
        return 'empty'
    for mac, sn in d_macs.items():
        if sn.startswith('2') and len(sn) == 7:
            return 'yes'
        if sn.startswith('3') and len(sn) == 7:
            return 'yes'
    return 'no'



def ddh_config_check_file_is_ok():
    b = copy.deepcopy(cfg)
    aux = None

    # check for MISSING ones
    try:
        for i in [
            'aws_en',
            'sqs_en',
            'ble_en',
            'sms_en',
            'skip_dl_in_port_en',
            'hook_gps_error_measurement_forced',
        ]:
            aux = i
            del b['flags'][i]
    except (Exception, ) as ex:
        print(f'error, ddh_config_check_file_is_ok -> {ex}')
        print(f'error, missing flag {aux}')
        return aux

    # check for EXTRA UNKNOWN ones, but this is NOT critical
    aux = b['flags']
    if len(aux):
        print(f'warning, ddh_config_check_file_is_ok extra flags {aux}')

    assert type(b['behavior']['fake_gps_position']) is list

    sn = cfg['credentials']['cred_ddh_serial_number']
    if not sn:
        print('***********************')
        print('  error! need box sn')
        print('***********************')
        os._exit(1)
    prj = cfg['credentials']['cred_ddh_project_name']
    if not prj:
        print('********************************')
        print('  error, need box project name')
        print('********************************')
        os._exit(1)




def ddh_config_is_sqs_enabled():
    return cfg['flags']['sqs_en']



def ddh_config_get_one_aws_credential_value(k):
    assert k in cfg['credentials'].keys() and k.startswith("cred_aws_")
    return cfg['credentials'][k]



def ddh_config_get_box_sn():
    return cfg["credentials"]["cred_ddh_serial_number"]



def ddh_config_get_box_project():
    return cfg["credentials"]["cred_ddh_project_name"]



def _get_exp_key_from_cfg(k):
    try:
        return int(cfg['experimental'][k])
    except (Exception, ) as ex:
        # no value in [experimental] section
        print(f'error, _get_exp_key_from_cfg -> {ex}')
        return -1



def exp_get_conf_dox():
    rv = _get_exp_key_from_cfg('conf_dox')
    if rv == -1:
        # no such key in config.toml
        return None
    if rv not in (60, 300, 900, "60", "300", "900"):
        print('rv NOT in expt_get_conf_dox() possible keys')
        return None
    return int(rv)



def exp_get_custom_side_buttons_debounce_time():
    return _get_exp_key_from_cfg('custom_side_buttons_debounce_time')



def exp_debug_skip_hbw():
    return _get_exp_key_from_cfg('use_skip_hbw')



def ddh_ble_logger_needs_a_reset(mac):
    mac = mac.replace(':', '-')
    p = f'{ddh_get_path_to_folder_tweak()}/{mac}.rst'
    rv = os.path.exists(p)
    if rv:
        os.unlink(p)
    return rv



# ----------------------------
# files stored in /tmp folder
# ----------------------------

# when present, DDH graphs test data
TMP_PATH_GRAPH_TEST_MODE_JSON = '/tmp/ddh_graph_test_mode.json'

# written by real GPS to know the last GPS position
TMP_PATH_GPS_LAST_JSON = "/tmp/gps_last.json"

# written by BLE to tell which BLE interface is using
TMP_PATH_BLE_IFACE = "/tmp/ble_iface_used.json"

# indicates press of "clear lock out" to clear macs, force logger downloads ...
TMP_PATH_DDH_APP_OVERRIDE = "/tmp/ddh_app_override_file.flag"

# internet via
TMP_PATH_INET_VIA = '/tmp/ddh_internet_via.json'

# indicates we will download NOT depending on the mac has been in water or not
TMP_PATH_DDH_HBW = '/tmp/ddh_hbw_{}.flag'




# -----------------------------------------------------------------
# files stored in /li folder so permanent even removing DDH folder
# -----------------------------------------------------------------

d = '/home/pi/li/' if linux_is_rpi() else '/tmp'
LI_PATH_GROUPED_S3_FILE_FLAG = f'{d}/.ddt_this_box_has_grouped_s3_uplink.flag'
LI_PATH_CELL_FW = f'{d}/.fw_cell_ver'
DDH_USES_SHIELD_JUICE4HALT = f'{d}/.ddt_j4h_shield.flag'
DDH_USES_SHIELD_SAILOR = f'{d}/.ddt_sailor_shield.flag'
LI_FILE_ICCID = f'{d}/.iccid'
LI_PATH_TEST_MODE = f'{d}/.ddh_test_mode.flag'
LI_PATH_PLT_ONLY_INSIDE_WATER = f'{d}/.ddh_plt_only_inside_water'
# when present, DDH simulates latitude and longitude values from config.toml
LI_PATH_GPS_DUMMY = f'{d}/.gps_dummy_mode.json'





# ------------------------------
# files stored in /li/ddh folder
# ------------------------------

h = str(pathlib.Path.home())
h_ddh = f'{h}/li/ddh' if linux_is_rpi() else f'{h}/PycharmProjects/ddh'
LI_PATH_DDH_VERSION = f'{h_ddh}/.ddh_version'
LI_PATH_API_VERSION = f'{h_ddh}/.api_version'
LI_PATH_LAST_YEAR_AWS_TEMPLATE = f'{h_ddh}/.ddh_aws_last_year_'




# ----------------------------------------
# this will be moved to gettext module,
# but it did not work for me when I tried
# ----------------------------------------


EV_CONF_BAD = '0'
EV_GPS_IN_PORT = '1'
EV_BLE_CONNECTING = '2'
EV_BLE_DL_NO_NEED = '3'
EV_BLE_DL_PROGRESS = '4'
EV_BLE_DL_OK = '5'
EV_BLE_DL_ERROR = '6'
EV_BLE_LOW_BATTERY = '7'
EV_BLE_DL_OK_NO_RERUN = '8'
EV_GPS_HW_ERROR = '9'
EV_NO_ASSIGNED_LOGGERS = '10'
EV_GUI_BOOT = '11'
EV_GPS_WAITING_BOOT = '12'
EV_BLE_SCAN = '13'
EV_GPS_SYNC_CLOCK = '14'
EV_BLE_DL_RETRY = '15'
EV_BLE_HW_ERROR = '16'
EV_GUI_ERROR_REDIS = '17'
EV_GUI_ERROR_POWER_SAH = '18'
EV_GUI_ERROR_POWER_J4H = '19'




STR_EV_CONF_BAD = 'error config, see log'
STR_EV_GPS_IN_PORT = 'we are in port'
STR_EV_BLE_CONNECTING = 'connecting'
STR_EV_BLE_DL_NO_NEED = 'no new in-water data'
STR_EV_BLE_DL_PROGRESS = 'downloading'
STR_EV_BLE_DL_OK = 'done'
STR_EV_BLE_LOW_BATTERY = "low battery!"
STR_EV_BLE_DL_OK_NO_RERUN = "stopped & auto-wake OFF"
STR_EV_GPS_HW_ERROR = 'need GPS'
STR_NO_ASSIGNED_LOGGERS = 'no loggers assigned'
STR_EV_GUI_BOOT = 'DDH starting'
STR_EV_GPS_WAITING_BOOT = 'boot GPS, up to'
STR_EV_BLE_SCAN = 'searching for loggers'
STR_EV_GPS_SYNC_CLOCK = 'syncing GPS time'
STR_EV_BLE_DL_RETRY = 'retrying'
STR_EV_BLE_HW_ERROR = 'no BLE service'
STR_EV_ERROR_REDIS = 'error redis'
STR_EV_ERROR_POWER_SAH = 'error power SAH'
STR_EV_ERROR_POWER_J4H = 'error power J4H'




g_lang_idx = ddh_config_get_language_index()
g_lang = ddh_config_get_language_str_by_index(g_lang_idx)


lang_msg_db = {
    STR_EV_BLE_SCAN: {
        'fr': 'cherchant sondes',
        'ca': 'buscant loggers',
        'pl': 'earchingsay orfay ogerslay',
        'sp': '--', # spanish
        'pt': '--'  # portuguese
    },
    STR_EV_BLE_CONNECTING: {
        'fr': 'en cours de connexion',
        'ca': 'connectant',
        'pl': 'onnectinglay oggerlay',
        'sp': '--', # spanish
        'pt': '--'  # portuguese
    },
    STR_EV_GPS_SYNC_CLOCK: {
        'fr': 'synchronisation GPS',
        'ca': 'esperant GPS',
        'pl': 'ycningay GPA imetay',
        'sp': '--', # spanish
        'pt': '--'  # portuguese
    },
    STR_EV_GUI_BOOT: {
        'fr': "--",
        'ca': '--',
        'pl': 'ootingbay',
        'sp': '--', # spanish
        'pt': '--'  # portuguese
    },
    STR_EV_BLE_DL_PROGRESS: {
        'fr': "téléchargement en cours",
        'ca': '--',
        'pl': "ownloadingday oggerlay",
        'sp': '--', # spanish
        'pt': '--'  # portuguese
    },
    STR_EV_BLE_DL_OK: {
        'fr': "complété",
        'ca': '--',
        'pl': "kosay",
        'sp': '--',  # spanish
        'pt': '--'  # portuguese
    },
    STR_EV_BLE_DL_NO_NEED: {
        'fr': "complété",
        'ca': '--',
        'pl': 'ownloadinglay oggerlay oneday',
        'sp': '--', # spanish
        'pt': '--'  # portuguese
    },
    STR_EV_BLE_DL_OK_NO_RERUN: {
        'fr': "arrêté, auto-réveille éteint",
        'ca': '--',
        'pl': 'oppedstay autowakeyay offyay',
        'sp': '--', # spanish
        'pt': '--'  # portuguese
    },
    STR_EV_BLE_DL_RETRY: {
        'fr': "nouvel essai",
        'ca': '--',
        'pl': 'etryingray oggerlay',
        'sp': '--', # spanish
        'pt': '--'  # portuguese
    },
    STR_EV_GPS_HW_ERROR: {
        'fr': "aucun signal GPS",
        'ca': '--',
        'pl': 'eednay GPS',
        'sp': '--', # spanish
        'pt': '--'  # portuguese
    },
    STR_EV_GPS_WAITING_BOOT: {
        'fr': "en attente du GPS",
        'ca': '--',
        'pl': 'yncingay GPS imetay illstay aitingway ootbay',
        'sp': '--',  # spanish
        'pt': '--'  # portuguese
    },
    STR_EV_BLE_HW_ERROR: {
        'pt': '--',
        'fr': "erreur du signal radio",
        'ca': '--',
        'pl': 'oggerlay errorlay adioray',
        'sp': '--',  # spanish
    },
    STR_EV_CONF_BAD: {
        'fr': "erreur de config, voir log",
        'ca': '--',
        'pl': "DDS adbay onfcay",
        'sp': '--', # spanish
        'pt': '--'  # portuguese
    },
    STR_EV_GPS_IN_PORT: {
        'fr': "dans port",
        'ca': '--',
        'pl': "eway arelay inlay ortpay",
        'sp': '--', # spanish
        'pt': '--'  # portuguese
    },
    STR_EV_BLE_LOW_BATTERY: {
        'fr': "batterie faible!",
        'ca': '--',
        'pl': 'oggerlay owlay atterybay!',
        'sp': '--', # spanish
        'pt': '--'  # portuguese
    },
    STR_NO_ASSIGNED_LOGGERS: {
        'fr': "aucune sonde attribué",
        'ca': '--',
        'pl': 'onay oggerlay assignedlay',
        'sp': '--', # spanish
        'pt': '--'  # portuguese
    },
}



def t_str(s):
    # putting this here allows for dynamic changing of language
    if s not in lang_msg_db.keys():
        print(f"** error, no translation for text '{s}'")
        return s
    if g_lang == 'en':
        return s
    d_s = lang_msg_db[s]
    if g_lang not in d_s.keys():
        print(f"\033[31merror: no language '{g_lang}' for text '{s}'\033[0m")
        return s
    return lang_msg_db[s][g_lang]



# -------------------------------
# new GUI state update mechanism
# -------------------------------

def app_state_set(code, text, expiration_time=None):
    # ex: code STATE_BLE_DL_ERROR, text: logger 1234567
    r.set(RD_DDH_GUI_STATE_EVENT_CODE, code)
    r.set(RD_DDH_GUI_STATE_EVENT_TEXT, text)
    if expiration_time:
        r.expire(RD_DDH_GUI_STATE_EVENT_CODE, expiration_time)
        r.expire(RD_DDH_GUI_STATE_EVENT_TEXT, expiration_time)



def app_state_get():
    code = r.get(RD_DDH_GUI_STATE_EVENT_CODE)
    text = r.get(RD_DDH_GUI_STATE_EVENT_TEXT)
    return code, text



# ok or error
_p = 'ddh/gui/res'
PATH_GPS_ANTENNA_ICON_OK = f"{_p}/new_icon_gps_antenna_ok.png"
PATH_GPS_ANTENNA_ICON_ERROR = f"{_p}/new_icon_gps_antenna_error.png"
PATH_GPS_ANTENNA_ICON_START = f"{_p}/new_icon_gps_antenna_start.png"
PATH_BLE_ANTENNA_ICON_OK = f"{_p}/new_icon_ble_antenna_ok.png"
PATH_BLE_ANTENNA_ICON_ERROR = f"{_p}/new_icon_ble_antenna_error.png"
PATH_BLE_ANTENNA_ICON_START = f"{_p}/new_icon_ble_antenna_start.png"
PATH_CELL_ICON_OK = f"{_p}/new_icon_cell_wifi_ok.png"
PATH_CELL_ICON_ERROR = f'{_p}/new_icon_cell.png'
PATH_TEMPLATE_MAIN_BLE_SCAN_IMG = _p + '/blue{}.png'
PATH_TEMPLATE_MAIN_GPS_BOOT_IMG = _p + '/gps_boot{}.png'
PATH_TEMPLATE_MAIN_GPS_CLOCK_IMG = f'{_p}/gps_clock.png'
PATH_MAIN_BOOT = f'{_p}/booting.png'
PATH_MAIN_NO_LOGGERS_ASSIGNED = f'{_p}/attention_old.png'
PATH_MAIN_CONF_BAD = f'{_p}/bad_conf.png'
PATH_MAIN_IN_PORT = f'{_p}/gps_in_port.png'
PATH_MAIN_BLE_CONNECTING = f'{_p}/ble_connecting.png'
PATH_MAIN_BLE_DL_OK = f'{_p}/ok.png'
PATH_MAIN_BLE_DL_OK_NO_RERUN = f'{_p}/attention.png'
PATH_MAIN_BLE_DL_ERROR = f'{_p}/error.png'
PATH_MAIN_BLE_DL_NO_NEED = f'{_p}/no_water_data_dl.png'
PATH_MAIN_BLE_DL_LOW_BATTERY = f'{_p}/low_battery.png'
PATH_MAIN_BLE_DL_RETRY = f'{_p}/sand_clock.png'
PATH_MAIN_BLE_DL_PROGRESS = f'{_p}/dl2.png'
PATH_MAIN_GPS_HW_ERROR = f'{_p}/gps_err.png'



if __name__ == '__main__':
    print('vessel_name', ddh_config_get_vessel_name())
    print('aws_en', ddh_config_get_is_aws_s3_enabled())
    print('flag_graph_test', ddh_config_does_flag_file_graph_test_mode_exist())
    print('flag_gps_error_forced', ddh_config_is_gps_error_forced_enabled())
    print('ls_sn_macs', ddh_config_get_list_of_monitored_serial_numbers())
    print('json_mac_dns', ddh_config_get_logger_sn_from_mac("11-22-33-44-55-66"))
    print('ft', ddh_config_get_forget_time_seconds())
    print('monitored_macs', ddh_config_get_list_of_monitored_macs())
    print('mac_from_sn_json_file', ddh_config_get_logger_mac_from_sn('1234567'))
    print('ddh_config_is_sqs_enabled', ddh_config_is_sqs_enabled())
    print('conf_dox', exp_get_conf_dox())
    print('has lowell logger', ddh_config_contains_monitored_lowell_loggers())
    print('buttons debounce time', exp_get_custom_side_buttons_debounce_time())

