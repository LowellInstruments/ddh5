import os
import pathlib
import sys
import time
from os.path import exists
import serial
from gps.gps import gps_find_any_usb_port, gps_hardware_read
from gps.gps_adafruit import gps_adafruit_init
from gps.gps_quectel import gps_hat_detect_list_of_usb_ports, gps_hat_init, gps_hat_get_firmware_version, \
    gps_power_cycle_ddc
from scripts.script_nadv import main_nadv
from utils.ddh_common import (
    ddh_get_path_to_folder_settings, ddh_config_load_file,
    ddh_get_path_to_config_file, \
    LI_PATH_GPS_DUMMY,
    LI_PATH_TEST_MODE,
    DDH_USES_SHIELD_JUICE4HALT, DDH_USES_SHIELD_SAILOR,
    ddh_get_local_software_version
)
import subprocess as sp
from mat.utils import PrintColors as PC



def is_rpi():
    return sh('cat /proc/cpuinfo | grep aspberry') == 0



def sh(c):
    rv = sp.run(c, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    return rv.returncode


def sho(c):
    rv = sp.run(c, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    return rv.returncode, rv.stdout.decode()



# cwd() is ddh folder here
h = str(pathlib.Path.home())
p = 'li/ddh' if is_rpi() else 'PycharmProjects/ddh'
path_script_deploy_dox = f'{h}/{p}/scripts/run_script_deploy_logger_dox.sh'
path_script_deploy_tdo = f'{h}/{p}/scripts/run_script_deploy_logger_tdo.sh'
path_script_scan_li = f'{h}/{p}/scripts/run_script_scan_li.sh'
VP_GPS_PUCK_1 = '067b:2303'
VP_GPS_PUCK_2 = '067b:23a3'
VP_QUECTEL = '2c7c:0125'
MD5_MOD_BTUART = '95da1d6d0bea327aa5426b7f90303778'
TMP_DDC_ERR = '/tmp/ddc_err'
DEBUG_TIME = False
g_d_cache_aws_cred_check = {}



# variables for errors and warnings
g_e = None
g_w = None
g_i = None


def _p(s):
    print(s)


def p_e(s):
    PC.R('[ error ] ' + s)
    with open(TMP_DDC_ERR, 'a') as f:
        f.write(f'error, {s}\n')



def p_w(s):
    PC.Y('[ warning ] ' + s)



def p_i(s):
    PC.B('[ information ] ' + s)


def _show_issues_error():
    if g_e:
        p_e('\nthe following can prevent DDH from starting')
        PC.R(g_e)


def _show_issues_warning():
    if g_w:
        p_w('\nplease notice')
        PC.Y(g_w)


def _show_issues_info():
    if g_i:
        p_i('\nmiscellaneous info')
        PC.B(g_i)



def _menu_cb_gps_dummy():
    if exists(LI_PATH_GPS_DUMMY):
        os.unlink(LI_PATH_GPS_DUMMY)
    else:
        pathlib.Path(LI_PATH_GPS_DUMMY).touch()


def _menu_cb_test_mode():
    if exists(LI_PATH_TEST_MODE):
        os.unlink(LI_PATH_TEST_MODE)
    else:
        pathlib.Path(LI_PATH_TEST_MODE).touch()


def _menu_cb_get_flag_j4h():
    return sh(f'ls {DDH_USES_SHIELD_JUICE4HALT}') == 0


def _menu_cb_quit():
    sys.exit(0)


def c_e():
    if os.path.exists(TMP_DDC_ERR):
        os.unlink(TMP_DDC_ERR)



def _menu_cb_crontab(s):
    cf = '/etc/crontab'
    cf_run = f'/home/pi/li/ddt/_dt_files/crontab_{s}.sh'
    if sh(f'grep -q crontab_{s}.sh {cf}') == 1:
        # string NOT FOUND in file /etc/crontab, add it
        sh(f'echo "* * * * * pi {cf_run}" | sudo tee -a {cf}')
        # new line because -e sucks
        sh(f'echo "" | sudo tee -a {cf}')
        return

    # string is there, detect a "commented" symbol
    rv = sh(f"grep crontab_{s}.sh {cf} | grep -F '#' > /dev/null")

    # delete any lines containing "crontab_ddh.sh"
    sh(f"sudo sed -i '/crontab_{s}/d' {cf}")

    if rv == 0:
        sh(f'echo "* * * * * pi {cf_run}" | sudo tee -a {cf}')
    else:
        sh(f'echo "#* * * * * pi {cf_run}" | sudo tee -a {cf}')

    # restart the cron service
    sh("sudo systemctl restart cron.service")




# needed because we cannot call with parameters from menu
def _menu_cb_toggle_crontab_ddh(): return _menu_cb_crontab('ddh')
def _menu_cb_toggle_crontab_api(): return _menu_cb_crontab('api')
def _menu_cb_toggle_crontab_lxp(): return _menu_cb_crontab('lxp')



# contains errors in system check
str_e = ''
str_w = ''
str_i = ''




def _menu_cb_show_ddh_issues():
    _p('')
    _show_issues_error()
    _show_issues_warning()
    _show_issues_info()
    input()



# simply see there is stuff coming from Quectel NMEA port
def _menu_cb_test_gps_quectel():
    ls_p = gps_hat_detect_list_of_usb_ports()
    if not ls_p:
        _p_e('could not detect quectel USB ports')
        input()
        return
    port_nmea = ls_p[1]
    port_ctrl = ls_p[-2]
    rv = gps_hat_init(port_ctrl)
    if rv:
        print(f'OK! found GPS output on quectel port {port_nmea}')
    else:
        _p_e('cannot find GPS output for hat')
    input()



def _p_e(e):
    print(f'DDC error, {e}')



# CSQ: cell signal quality
def _menu_cb_cell_signal_quality():

    ls_p = gps_hat_detect_list_of_usb_ports()
    if not ls_p:
        _p_e('could not detect quectel USB ports to get CELL signal quality')
        time.sleep(2)
        return
    port_ctrl = ls_p[-2]

    till = time.perf_counter() + 1
    b = bytes()
    ser = None
    try:
        ser = serial.Serial(port_ctrl, 115200, timeout=.1, rtscts=True, dsrdtr=True)
        ser.write(b'AT+CSQ \r')
        time.sleep(.5)
        while time.perf_counter() < till:
            b += ser.read()
        ser.close()
    except (Exception,):
        _p_e('working with serial port on CSQ')
        if ser:
            ser.close()
        input()
        return

    # +CSQ: 19,99 among other lines
    try:
        v = b.split(b'+CSQ: ')[1].split(b',')[0]
        v = int(v.decode())
    except (Exception,) as ex:
        _p_e(f'exception on CSQ {ex}')
        input()
        return

    # page 81 datasheet EG25
    s = ''
    if v == 0:
        s = '< -113 dBm'
    elif v == 1:
        s = '-111 dBm'
    elif 2 <= v <= 30:
        s = f'{-113 + (2 * v)} dBm'
    elif v == 31:
        s = '> -51 dBm'
    elif v == 99:
        s = 'not detectable'
    elif v == 100:
        s = '< -116 dBm'
    elif v == 101:
        s = '-115 dBm'
    elif 102 <= v <= 190:
        s = f'{-114 + (1 * v)} dBm'
    elif v == 191:
        s = '> -25 dBm'
    elif v == 199:
        s = 'not detectable'
    _p(f'\ncell signal quality = {s} (minimum is -115 dBm)')
    print('test end, press ENTER to go back to DDC menu')
    input()




def _menu_cb_gps_signal_quality():


    # get the USB ports
    p_gps, p_ctl, port_type = gps_find_any_usb_port()
    if not port_type:
        _p_e('could not detect quectel USB ports to get GPS signal quality')
        time.sleep(3)
        return
    print('port_gps', p_gps)
    print('port_ctrl', p_ctl)


    # let the user decide
    if port_type == 'hat':
        print('\nQUESTION: Do you want to power-cycle GPS shield? (y/n) -> ', end='')
        question = input().lower()
        if question in ('y', 'yes'):
            gps_power_cycle_ddc(p_ctl)


    # figure out the baudrate
    br = 115200
    if port_type == 'hat':
        gps_hat_init(p_ctl)
    elif port_type == 'adafruit':
        gps_adafruit_init(p_gps)
    else:
        # gps puck
        br = 4800


    # when hat, ensure GPS output activated, code is same as gps_power_cycle()
    ser_ctl = None
    try:
        ser_ctl = serial.Serial(p_ctl, 115200, timeout=1)
        print('now')
        ser_ctl.write(b'AT+QGPSEND\r')
        time.sleep(.1)
        rv = ser_ctl.read_all()
        print(rv)
        ser_ctl.write(b'AT+QGPSDEL=1\r')
        time.sleep(.1)
        rv = ser_ctl.read_all()
        print(rv)
        ser_ctl.write(b'AT+QGPS=1\r')
        time.sleep(.1)
        rv = ser_ctl.read_all()
        print(rv)
        ser_ctl.reset_input_buffer()
        time.sleep(1)
    except (Exception, ) as ex:
        print(f'error: gps_power_cycle_ddc {ex}')
    finally:
        if ser_ctl and ser_ctl.is_open:
            ser_ctl.close()



    # starts GPS signal quality loop
    while 1:

        # get a lot of GPS bytes
        os.system('clear')
        print('GPS quality test running\n')
        d_gps = {}
        gps_hardware_read(p_gps, br, d_gps, debug=False)
        bb = []
        if 'bb' in d_gps.keys():
            bb = d_gps['bb']



        # we only keep GPRMC / GPGSV lines
        ls_gps = bb.split(b'\r\n')
        ls_rmc = [i for i in ls_gps if i and i.startswith(b'$GPRMC') and i[-3] == 42]
        ls_gsv = [i for i in ls_gps if i and i.startswith(b'$GPGSV') and i[-3] == 42]
        line_rmc = ''
        if ls_rmc:
            line_rmc = ls_rmc[-1].decode()
        print(ls_rmc)
        print(ls_gsv)



        # parse line GPRMC
        s = '\n'
        if not line_rmc:
            s += "RMC --> none\n"
        else:
            g = line_rmc.split(',')
            # g: ['$GPRMC', '145557.00', 'A', '4136.603719', 'N', '07036.560277', 'W', ...]
            if g[2] == 'A':
                def to_deg(deg_s):
                    deg_f = float(deg_s[:-7])
                    deg_m = float(deg_s[-7:]) / 60
                    return deg_f + deg_m

                last_lat_lon = (to_deg(g[3]), g[4], to_deg(g[5]), g[6])
                last_time = f'{g[1][0:2]}:{g[1][2:4]}:{g[1][4:6]}'
                s += f'RMC --> {last_lat_lon}    {last_time}\n'
            else:
                s += "RMC --> ,,,,\n"

        print(s, end='')
        s = ''



        # build GPGSV set
        d = {}
        for i in ls_gsv:
            f = i.decode().split(',')
            # 1    = Total number of messages of this type in this cycle
            # 2    = Message number
            # 3    = Total number of SVs in view
            # 4    = SV PRN number
            # 5    = Elevation in degrees, 90 maximum
            # 6    = Azimuth, degrees from true north, 000 to 359
            # 7    = SNR, 00-99 dB (null when not tracking)
            # 8-11 = Information about second SV, same as field 4-7
            # 12-15= Information about third SV, same as field 4-7
            # 16-19= Information about fourth SV, same as field 4-7
            for j in range(4, 17, 4):
                try:
                    s_id = f[j]
                    s_snr = f[j + 3]
                    d[s_id] = s_snr
                except (Exception, ):
                    pass

        n = len(d)
        if d:
            # d: {'1': {'04': '26', '05': '35', '06': '34', '09': '32'},
            #     '2': {'11': '30', '12': '35', '19': '30', '21': '34'},
            #     '3': {'25': '30', '29': '30', '13': '', '17': ''}}
            d = {k: v for k, v in d.items() if v}
            m = len(d)
            s += f'GSV --> {n} satellites, {n - m} of which reporting no SNR\n'
            s += '\n[ id ] snr     (max 99)\n'
            s += '-----------------------\n'
            for k, v in d.items():
                s += f'[ {k} ] snr {v} '
                s += ('#' * int(v)) + '\n'

        print(s)
        time.sleep(3)




def _menu_cb_test_buttons():
    try:
        if not is_rpi():
            p_e('no Rpi for buttons test')
            return
        from scripts.script_test_box_buttons import main_test_box_buttons
        main_test_box_buttons()
    except (Exception,) as ex:
        p_e(str(ex))




def _menu_cb_run_brt():

    print("\nQUESTION: Do you want to edit the BRT config file? (y/n) -> ", end='')
    if input().lower in ('y', 'yes', 'Y'):
        p_cfg = f'{h}/Downloads/cfg_brt_nadv.toml'
        if not os.path.exists(p_cfg):
            sp.run(f'cp scripts/cfg_brt_nadv_template.toml {p_cfg}')
        sp.call(['nano', p_cfg],
                stdin=sys.stdin, stdout=sys.stdout)

    c = '/home/pi/li/ddh/run_brt.sh'
    rv = sp.run(c, shell=True, stderr=sp.PIPE, stdout=sp.PIPE)
    if rv.returncode:
        print(f'BRT error, {rv.stderr}')
        input()




def ddc_menu_cb_run_nadv():
    main_nadv()




def _menu_cb_run_deploy_dox():
    try:
        # do this or this script's prompts fail
        sp.run(path_script_deploy_dox)
    except (Exception,) as ex:
        p_e(f'{ex} running deploy_dox')




def _menu_cb_run_deploy_tdo():
    try:
        # do this or this script's prompts fail
        sp.run(path_script_deploy_tdo)
    except (Exception,) as ex:
        p_e(f'{ex} running deploy_tdo')




def _menu_cb_run_scan_li():
    try:
        # do this or this script's prompts fail
        sp.run(path_script_scan_li)
    except (Exception,) as ex:
        p_e(f'{ex} running scan_li')




def ddc_menu_cb_edit_ddh_config_file():
    sp.call(['nano', ddh_get_path_to_config_file()],
            stdin=sys.stdin, stdout=sys.stdout)




def _check_aws_run(f):
    # f: {'cred_aws_bucket': '',
    #     'cred_aws_key_id': '',
    #     'cred_aws_secret': '',
    #     'cred_aws_sqs_queue_name': '',
    _k = f['cred_aws_key_id']
    _s = f["cred_aws_secret"]
    _n = f["cred_aws_bucket"]

    # 0 is bad
    if _k is None or _s is None or _n is None:
        return 0

    # cache so this is not run over and over again
    global g_d_cache_aws_cred_check
    key_cache = f'{_k}_{_s}_{_n}'
    if (key_cache in g_d_cache_aws_cred_check.keys() and
            g_d_cache_aws_cred_check[key_cache] == 1):
        return 1

    # build the AWS command
    c = (
        f'AWS_ACCESS_KEY_ID={_k} AWS_SECRET_ACCESS_KEY={_s} '
        f'aws s3 ls s3://{_n}'
    )

    # run test AWS ls command
    try:
        rv = sp.run(c, shell=True, stdout=sp.PIPE, stderr=sp.PIPE, timeout=10)
        if rv.returncode:
            print(f'error, listing buckets {rv.stderr}')
            g_d_cache_aws_cred_check[key_cache] = 0
            return 0
    except (Exception, ) as ex:
        print(f'error, check_aws_run -> {ex}')
        g_d_cache_aws_cred_check[key_cache] = 0
        return 0

    # 1 is good
    g_d_cache_aws_cred_check[key_cache] = 1
    return 1




def _menu_cb_print_check_all_keys(verbose=True):
    path_w = '/etc/wireguard/wg0.conf'
    if is_rpi():
        c = f'sudo ls {path_w}'
        rv = sp.run(c, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        w = rv.returncode == 0
    else:
        w = os.path.exists(path_w)
    a = os.path.exists(f'{h}/.ssh/authorized_keys')

    c = ddh_config_load_file()
    f = c['credentials']
    for k, v in f.items():
        if not v:
            if 'custom' not in k:
                # 0 is bad
                c = 0
    if c:
        c = _check_aws_run(f)

    m = os.path.exists(f'{ddh_get_path_to_folder_settings()}/all_macs.toml')

    rv = w and a and c and m

    if rv:
        return rv

    if verbose and not w:
        p_e('missing wireguard VPN conf file')
    if verbose and not a:
        p_i('missing SSH authorized keys file')
    if verbose and not c:
        p_e('missing ddh/settings/config.toml credentials section')
    if verbose and not m:
        p_e('missing ddh/settings/all_macs.toml file')

    if verbose:
        input()
    return 0




def _get_crontab(s):
    assert s in ('api', 'ddh', 'lxp')
    s = f'crontab_{s}.sh'
    # assume crontab off
    cf = '/etc/crontab'
    if sh(f'grep -q {s} {cf}'):
        # line NOT even present
        return 0
    # line IS present, search for special character with 'F'
    if sh(f"grep {s} {cf} | grep -F '#' > /dev/null") == 0:
        return 0
    # line IS present and uncommented
    return 1




# --------------
# main DCC loop
# --------------


def _menu_cb_show_help():
    _p('test mode    -> prefixes downloaded filenames with "testfile_"')
    _p('GPS dummy    -> GPS is simulated, it uses position in config.toml')
    _p('crontab      -> automatically starts or not DDH app upon boot')
    # _p('kill DDH     -> forces DDH app to quit')
    _p('graph demo   -> the DDH plotting tab will use simulated data')
    _p('credentials  -> checks the DDH has all the passwords to run OK')
    _p('GPS hat      -> tests the GPS hat, not the GPS USB puck')
    _p('side buttons -> tests the DDH real side buttons to be working')
    _p('BLE range    -> tests how well a logger\'s signal reaches the DDH')
    _p('deploy DOX   -> prepares a DO1 or DO2 logger for deployment')
    _p('deploy TDO   -> prepares a TDO logger for deployment')
    _p('detect LI    -> detects BLE Lowell Instruments loggers around')
    _p('cell quality -> tests how good cell reception is')
    _p('GPS quality  -> tests how good GPS reception is')
    # _p('calibrate    -> tunes the DDH touch display')
    _p('see issues   -> check any potential DDH conflict or misconfiguration')
    input()








def _ddc_run_check():

    global str_e
    global str_w
    global str_i
    str_e = ''
    str_w = ''
    str_i = ''

    def _e(s):
        global str_e
        str_e += f'   - {s}\n'

    def _i(s):
        global str_i
        str_i += f'   - {s}\n'

    def _w(s):
        global str_w
        str_w += f'   - {s}\n'



    def _ddc_run_check_version_ddh():
        vl = ddh_get_local_software_version()

        # get DDH version from github
        repo = 'https://raw.githubusercontent.com/LowellInstruments/ddh/toml'
        s = '.ddh_version'
        c = f'timeout 2 wget {repo}/{s}'
        c += f' -q -O /tmp/{s}'
        rv_gfv = sp.run(c, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        if rv_gfv.returncode:
            _e('cannot obtain github remote DDH version')
            # 0 is bad
            return 0

        # we sure we have version here
        with open(f'/tmp/{s}', 'r') as f:
            vg = f.readline().replace('\n', '')

        if vl > vg[0]:
            # you are ahead, ok
            pass
        elif vl[0] != vg[0]:
            _w(f'app major version mismatch, local {vl}, github {vg}')
        elif vl[2] != vg[2]:
            _w(f'app minor version mismatch, local {vl}, github {vg}')
        elif vl[4] != vg[4]:
            _i(f'app patch version mismatch, local {vl}, github {vg}')
        elif vl[5] != vg[5]:
            _i(f'app patch version mismatch, local {vl}, github {vg}')
        return 1



    def _ddc_run_check_fw_cell():
        ls = gps_hat_detect_list_of_usb_ports()
        if not ls:
            _e('no cell USB hat detected')
            return 0
        port_ctrl = ls[-2]
        gfv, _ = gps_hat_get_firmware_version(port_ctrl)
        return gfv and b'2022' in gfv



    def _ddc_run_check_aws_credentials():
        c = ddh_config_load_file()
        f = c['credentials']
        for k, v in f.items():
            if not v:
                if 'custom' not in k:
                    _e(f'file config.toml missing credential {k}')
                    # 0 is bad
                    return 0
                else:
                    _w(f'file config.toml no {k}')
        if not _check_aws_run(f):
            _e(f'file config.toml AWS credentials cannot connect')
            return 0
        return 1



    def _ddc_run_check_gps_dummy():
        if os.path.exists(LI_PATH_GPS_DUMMY):
            _w(f'GPS dummy ON')
            return 1
        return 0



    def _ddc_run_check_files_network():
        path_w = '/etc/wireguard/wg0.conf'
        if is_rpi():
            c = f'sudo ls {path_w}'
            _rv = sp.run(c, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
            w = _rv.returncode == 0
        else:
            w = os.path.exists(path_w)

        if not w:
            _w('file wireguard VPN conf is missing')

        # a = os.path.exists(f'/home/pi/.ssh/authorized_keys')
        # if not a:
        #   _i('file SSH authorized keys is missing')



    def _ddc_run_check_files_all_macs_toml():
        m = os.path.exists(f'{ddh_get_path_to_folder_settings()}/all_macs.toml')
        if not m:
            _e('file all_macs.toml is missing')


    # -----------------------------------------------------
    # issue: Raspberry Pi reference 2023-05-03
    # is_rpi3: Raspberry Pi 3 Model B Plus Rev 1.3
    # hostname: raspberrypi
    # hardware flags
    # grep exact (-w) for 'active' detection
    # dwservice
    # -----------------------------------------------------
    ok_issue_20240315 = sh('cat /boot/issue.txt | grep 2024-03-15') == 0
    ok_issue_20230503 = sh('cat /boot/issue.txt | grep 2023-05-03') == 0
    ok_issue_20220922 = sh('cat /boot/issue.txt | grep 2022-09-22') == 0
    is_rpi3 = sh("cat /proc/cpuinfo | grep 'aspberry Pi 3'") == 0
    ok_hostname = sh('hostname | grep raspberrypi') == 0
    flag_vp_gps_puck1 = sh(f'lsusb | grep {VP_GPS_PUCK_1}') == 0
    flag_vp_gps_puck2 = sh(f'lsusb | grep {VP_GPS_PUCK_2}') == 0
    flag_vp_gps_quectel = sh(f'lsusb | grep {VP_QUECTEL}') == 0
    flag_mod_btuart = sh(f'md5sum /usr/bin/btuart | grep {MD5_MOD_BTUART}') == 0
    ok_ble_v = sh('bluetoothctl -v | grep 5.66') == 0
    _c = 'systemctl is-active unit_switch_net.service | grep -w active'

    ts = time.perf_counter()
    ok_aws_cred = _ddc_run_check_aws_credentials()
    if DEBUG_TIME:
        el_ts = time.perf_counter() - ts
        print(f'ok_aws_cred took {int(el_ts)}')

    ts = time.perf_counter()
    ok_check_ddh_version = _ddc_run_check_version_ddh() == 1
    if DEBUG_TIME:
        el_ts = time.perf_counter() - ts
        print(f'_check_version_ddh took {int(el_ts)}')

    ts = time.perf_counter()
    ok_service_cell_sw = sh(_c) == 0
    if DEBUG_TIME:
        el_ts = time.perf_counter() - ts
        print(f'ok_service_cell_sw took {int(el_ts)}')

    ts = time.perf_counter()
    ok_fw_cell = _ddc_run_check_fw_cell()
    if DEBUG_TIME:
        el_ts = time.perf_counter() - ts
        print(f'_check_fw_cell took {int(el_ts)}')

    ts = time.perf_counter()
    ok_sixfab_installed = sh('ps -aux | grep ppp_connection_manager.sh | grep -v grep') == 0
    if DEBUG_TIME:
        el_ts = time.perf_counter() - ts
        print(f'ok_sixfab_installed {int(el_ts)}')

    ts = time.perf_counter()
    ok_ppp0_installed = sh('ifconfig -a | grep ppp0') == 0
    if DEBUG_TIME:
        el_ts = time.perf_counter() - ts
        print(f'ok_ppp0_installed {int(el_ts)}')

    ts = time.perf_counter()
    ok_internet_via_cell = sh('timeout 1 ping -c 1 -I ppp0 www.google.com -4') == 0
    if DEBUG_TIME:
        el_ts = time.perf_counter() - ts
        print(f'ok_internet_via_cell took {int(el_ts)}')

    ok_dwservice = sh('ps -aux | grep dwagent') == 0

    ok_crontab_ddh = _get_crontab('ddh') == 1
    ok_crontab_api = _get_crontab('api') == 1
    ok_crontab_lxp = _get_crontab('lxp') == 1
    ok_shield_j4h = _menu_cb_get_flag_j4h() == 1
    ok_shield_sailor = sh(f'ls {DDH_USES_SHIELD_SAILOR}') == 0


    ts = time.perf_counter()
    ok_file_wireguard = _ddc_run_check_files_network() == 0
    if DEBUG_TIME:
        el_ts = time.perf_counter() - ts
        print(f'ok_file_wireguard took {int(el_ts)}')

    ts = time.perf_counter()
    ok_file_all_macs_toml = _ddc_run_check_files_all_macs_toml() == 0
    if DEBUG_TIME:
        el_ts = time.perf_counter() - ts
        print(f'ok_file_all_macs_toml took {int(el_ts)}')

    # check conflicts
    rv = 0
    if not ok_file_wireguard:
        # error indicated inside other function
        rv += 1
    if not ok_file_all_macs_toml:
        # error indicated inside other function
        rv += 1
    if not ok_aws_cred:
        # error indicated inside other function
        rv += 1

    if not ok_ppp0_installed:
        _e('no cell interface ppp0 detected')
        rv += 1
    if not ok_sixfab_installed:
        # checks for ppp_connection_manager.sh
        _e('no cell sixfab software running')
        rv += 1
    if not ok_internet_via_cell:
        # checks for good output on command ping
        _e('no cell internet access via ping')
        rv += 1
    if not ok_fw_cell:
        _w('no cell hat proper firmware')
    if not ok_service_cell_sw:
        _e('service switch cell / wifi not running')
    if not ok_dwservice:
        _e('service DWS not running')
        rv += 1

    if not ok_ble_v != '5.66':
        _e('bad bluez version')
        rv += 1
    if is_rpi3 and not flag_mod_btuart:
        _e(f'bad mod_uart, is_rpi3 {is_rpi3}')
        rv += 1

    if not (ok_issue_20230503 or
            ok_issue_20220922 or
            ok_issue_20240315):
        _e('bad issue.txt file')
        rv += 1
    if not ok_hostname:
        _e('bad hostname')
        rv += 1
    if not ok_crontab_ddh:
        _e('crontab DDH not set')
    if not ok_crontab_api:
        _e('crontab API not set')
    if not ok_crontab_lxp:
        _e('crontab LXP not set')
    if not ok_check_ddh_version:
        _e('could not check DDH application version')
    if not (flag_vp_gps_quectel or flag_vp_gps_puck1 or flag_vp_gps_puck2):
        _e('no GPS hardware present')

    if not ok_shield_j4h and not ok_shield_sailor:
        _e('no power shield detected')
        rv += 1

    # make GPS dummy permanent
    _ddc_run_check_gps_dummy()

    return rv, str_e, str_w, str_i




def main_ddc():
    # clearing error log file
    c_e()

    while 1:
        os.system('clear')
        print(' --------')
        print('   DDC')
        print(' --------\n')

        global g_e
        global g_w
        global g_i


        # ----------
        # RUN check
        # ----------
        _, g_e, g_w, g_i = _ddc_run_check()

        # get flags
        fgd = 1 if exists(LI_PATH_GPS_DUMMY) else 0
        fcd = _get_crontab('ddh')
        fdk = _menu_cb_print_check_all_keys(verbose=False)
        ftm = 1 if exists(LI_PATH_TEST_MODE) else 0

        # create options
        d = {
            '0': (f"0) set dl_test mode  [{ftm}]", _menu_cb_test_mode),
            '1': (f"1) set GPS dummy     [{fgd}]", _menu_cb_gps_dummy),
            '2': (f"2) set crontab       [{fcd}]", _menu_cb_toggle_crontab_ddh),
            '3': (f"3) check all keys    [{fdk}]", _menu_cb_print_check_all_keys),
            '4': (f"4) test GPS", _menu_cb_test_gps_quectel),
            '5': (f"5) test side buttons", _menu_cb_test_buttons),
            'r': (f"r) BLE range tool", _menu_cb_run_brt),
            'o': (f"o) deploy logger DOX", _menu_cb_run_deploy_dox),
            't': (f"t) deploy logger TDO", _menu_cb_run_deploy_tdo),
            'b': (f"b) detect LI loggers around", _menu_cb_run_scan_li),
            's': (f"s) get cell signal quality", _menu_cb_cell_signal_quality),
            'g': (f"g) get GPS  signal quality (new)", _menu_cb_gps_signal_quality),
            'i': (f"i) ~ see issues detected by DDC ~", _menu_cb_show_ddh_issues),
            'h': (f"h) help", _menu_cb_show_help),
            'q': (f"q) quit", _menu_cb_quit)
        }

        # show menu
        for k, v in d.items():
            if 'issues' in v[0]:
                # color of the 'see issues' entry
                if g_e:
                    PC.R(f'\t{v[0]}')
                elif g_w:
                    PC.Y(f'\t{v[0]}')
                elif g_i:
                    PC.B(f'\t{v[0]}')
                else:
                    PC.G(f'\t{v[0]}')


            # normal entry
            else:
                print(f'\t{v[0]}')

        # get user input
        c = input('\nenter your choice > ')
        try:
            os.system('clear')
            print(f'you selected:\n\t{d[c][0]}')
            time.sleep(.5)

            # -----------------
            # hidden options
            # -----------------
            if c == 'k':
                ddc_menu_cb_edit_ddh_config_file()
            else:
                _, cb = d[c]
                cb()

        except (Exception,):
            p_e(f'invalid menu option {c}')
            time.sleep(2)


if __name__ == "__main__":
    main_ddc()
