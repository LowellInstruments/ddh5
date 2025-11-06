import signal
import sys
from pathlib import Path
import psutil
import glob
import pathlib
import setproctitle
from PyQt6 import QtCore
from PyQt6.QtCore import QProcess, QTimer, QCoreApplication, Qt, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QScreen, QMovie
from PyQt6.QtWidgets import (
    QApplication,
    QTableWidgetItem, QTableWidget,
    QWidget, QMessageBox,
    QMainWindow, QMenu
)
import ddh.gui.gui as d_m
from ble.li_cmds import DEV_SHM_DL_PROGRESS
from ddh.graph_draw import graph_request
from ddh.preferences import preferences_set_models_index
from ddh_gps import ddh_gps_get
from ddh.buttons import ddh_create_thread_buttons
from ddh.notifications_v2 import notify_via_sms, notify_ddh_alive, notify_error_sw_crash
from ddh.slo import slo_delete, slo_delete_all
from mat.linux import linux_is_process_running_strict
from mat.utils import linux_is_rpi
from rd_ctt.ddh import (
    RD_DDH_GUI_PLOT_REASON, RD_DDH_GUI_REFRESH_HISTORY_TABLE,
    RD_DDH_BLE_ANTENNA, \
    RD_DDH_GPS_ANTENNA, RD_DDH_AWS_PROCESS_STATE,
    RD_DDH_NET_PROCESS_OUTPUT, \
    RD_DDH_AWS_SYNC_REQUEST, RD_DDH_BLE_SEMAPHORE, \
    RD_DDH_GPS_COUNTDOWN_FOR_FIX_AT_BOOT,
    RD_DDH_GUI_STATE_EVENT_ICON_LOCK, RD_DDH_GUI_REFRESH_BLE_ICON_AUTO, \
    RD_DDH_GUI_REFRESH_GPS_ICON_AUTO, RD_DDH_GUI_REFRESH_CELL_WIFI_ICON_AUTO,
    RD_DDH_GUI_PLOT_FOLDER,
    RD_DDH_GUI_REFRESH_PROCESSES_PRESENT,
    RD_DDH_GUI_BOX_SIDE_BUTTON_LOW, RD_DDH_GUI_BOX_SIDE_BUTTON_MID,
    RD_DDH_GUI_BOX_SIDE_BUTTON_TOP, RD_DDH_GUI_GRAPH_STATISTICS, RD_DDH_GUI_MODELS_UPDATE, RD_DDH_GUI_RV
)
from utils.ddh_common import (
    ddh_get_path_to_folder_dl_files,
    ddh_get_path_to_folder_macs_black,
    ddh_get_path_to_app_override_flag_file,
    ddh_get_contents_of_config_file_all_macs,
    ddh_create_do_not_rerun_file_flag,
    ddh_clear_do_not_rerun_file_flag,
    NAME_EXE_API,
    ddh_get_template_of_path_of_hbw_flag_file,
    NAME_EXE_LOG, NAME_EXE_CNV, NAME_EXE_GPS, NAME_EXE_AWS,
    NAME_EXE_NET, ddh_config_get_vessel_name,
    ddh_config_get_box_sn,
    ddh_config_does_flag_file_download_test_mode_exist,
    ddh_config_is_skip_in_port_enabled,
    ddh_config_does_flag_file_graph_test_mode_exist,
    ddh_config_get_list_of_monitored_serial_numbers,
    ddh_config_get_forget_time_seconds, ddh_config_get_monitored_pairs,
    ddh_config_load_file, ddh_config_save_to_file,
    ddh_get_path_to_folder_scripts,
    ddh_config_get_logger_mac_from_sn,
    ddh_config_get_list_of_monitored_macs,
    ddh_config_get_logger_sn_from_mac, NAME_EXE_SQS, NAME_EXE_BLE,
    LI_PATH_PLT_ONLY_INSIDE_WATER,
    LI_PATH_GROUPED_S3_FILE_FLAG, app_state_get,
    EV_BLE_SCAN, EV_GUI_BOOT, EV_BLE_DL_PROGRESS,
    EV_BLE_DL_OK, EV_BLE_DL_OK_NO_RERUN, t_str, STR_EV_GUI_BOOT,
    app_state_set, ddh_config_check_file_is_ok,
    EV_CONF_BAD, STR_EV_CONF_BAD, EV_GPS_WAITING_BOOT,
    STR_EV_GPS_WAITING_BOOT, NAME_EXE_BRT,
    NAME_EXE_DDH, STR_NOTE_PURGE_BLACKLIST, PATH_TEMPLATE_MAIN_BLE_SCAN_IMG,
    EV_GPS_SYNC_CLOCK, PATH_TEMPLATE_MAIN_GPS_BOOT_IMG,
    PATH_TEMPLATE_MAIN_GPS_CLOCK_IMG, PATH_GPS_ANTENNA_ICON_START,
    PATH_BLE_ANTENNA_ICON_START, PATH_GPS_ANTENNA_ICON_OK,
    PATH_GPS_ANTENNA_ICON_ERROR, PATH_BLE_ANTENNA_ICON_ERROR,
    PATH_BLE_ANTENNA_ICON_OK, PATH_MAIN_BOOT, PATH_MAIN_NO_LOGGERS_ASSIGNED, EV_NO_ASSIGNED_LOGGERS,
    PATH_MAIN_CONF_BAD, EV_GPS_IN_PORT, PATH_MAIN_IN_PORT, EV_BLE_CONNECTING, EV_BLE_DL_ERROR, EV_BLE_DL_NO_NEED,
    EV_BLE_LOW_BATTERY, EV_BLE_DL_RETRY, PATH_MAIN_BLE_CONNECTING, PATH_MAIN_BLE_DL_OK, PATH_MAIN_BLE_DL_ERROR,
    PATH_MAIN_BLE_DL_OK_NO_RERUN, PATH_MAIN_BLE_DL_NO_NEED, PATH_MAIN_BLE_DL_LOW_BATTERY, PATH_MAIN_BLE_DL_RETRY,
    PATH_CELL_ICON_ERROR, PATH_CELL_ICON_OK, PATH_MAIN_BLE_DL_PROGRESS, EV_GPS_HW_ERROR,
    PATH_MAIN_GPS_HW_ERROR, STR_EV_BLE_DL_OK, ddh_config_get_language_index,
)
import datetime
import os
import shlex
import redis
import time
import shutil
from math import ceil
from ddh.db.db_his import DbHis
from ddh.graph_draw import graph_process_n_draw
from ddh.preferences import (
    preferences_get_brightness_clicks,
    preferences_get_models_index, preferences_set_brightness_clicks
)
from ddh.utils_models import gui_populate_models_tab
from ddh.emolt import ddh_this_box_has_grouped_s3_uplink
from ddh.timecache import is_it_time_to
import subprocess as sp
import pyqtgraph as pg
from utils.ddh_common import (
    ddh_get_path_to_folder_gui_res,
    ddh_get_path_to_db_history_file,
    ddh_does_do_not_rerun_file_flag_exist,
    ddh_get_path_to_root_application_folder,
    ddh_get_local_software_version,
)
from ddh_log import lg_gui as lg




# ==============================================
# ddh_gui
# ==============================================


r = redis.Redis('localhost', port=6379)
_g_ts_gui_boot = time.perf_counter()
g_app_uptime = time.perf_counter()
d_process_states = {
    QProcess.ProcessState.NotRunning: 'Not running',
    QProcess.ProcessState.Starting: 'Starting',
    QProcess.ProcessState.Running: 'Running',
}
d_processes = {
    NAME_EXE_LOG: None,
    NAME_EXE_AWS: None,
    NAME_EXE_BLE: None,
    NAME_EXE_CNV: None,
    NAME_EXE_GPS: None,
    NAME_EXE_NET: None,
    NAME_EXE_SQS: None,
}




def gui_kill_all_processes():
    lg.a(f'killing all processes')
    # ensure process log finds this
    time.sleep(1.1)
    for p in d_processes.keys():
        sp.run(f'killall {p}', shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        sp.run(f'kill -9 $(pidof {p})', shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    time.sleep(.1)



def gui_check_all_processes():
    for p in d_processes.keys():
        if not linux_is_process_running_strict(p):
            lg.a(f'warning, process {p} not present')



def cb_when_ddh_receives_ctrl_c(signal_num, _):
    lg.a(f'captured signal ctrl + c ({signal_num})')
    gui_kill_all_processes()
    # so DDH GUI is the last to be in OS
    time.sleep(1)
    sys.exit(0)



def cb_when_ddh_receives_kill_signal(signal_num, _):
    lg.a(f'captured kill signal ({signal_num})')
    gui_kill_all_processes()
    # so DDH GUI is the last to be in OS
    time.sleep(1)
    sys.exit(0)




class ButtonPressEvent:
    def __init__(self, code):
        self.code = code

    def key(self):
        return self.code



def _calc_app_uptime():
    return int(time.perf_counter() - g_app_uptime)



def gui_init_redis():
    for k in (
        RD_DDH_GUI_PLOT_REASON,
        RD_DDH_GUI_PLOT_FOLDER,
        RD_DDH_BLE_SEMAPHORE,
        RD_DDH_GUI_STATE_EVENT_ICON_LOCK,
        RD_DDH_AWS_SYNC_REQUEST,
        RD_DDH_GUI_MODELS_UPDATE
    ):
        r.delete(k)




def gui_check_config_file_is_ok():
    rv = ddh_config_check_file_is_ok()
    if rv:
        app_state_set(EV_CONF_BAD, t_str(STR_EV_CONF_BAD))
        while 1:
            time.sleep(1)



def gui_setup_side_buttons_box():
    ddh_create_thread_buttons()




def gui_setup_view(my_win):

    a = my_win
    a.setupUi(a)
    a.setWindowTitle("Lowell Instruments' Deck Data Hub")
    a.tabs.setTabIcon(0, QIcon("ddh/gui/res/icon_info.png"))
    a.tabs.setTabIcon(1, QIcon("ddh/gui/res/icon_setup.png"))
    a.tabs.setTabIcon(2, QIcon("ddh/gui/res/icon_exclamation.png"))
    a.tabs.setTabIcon(3, QIcon("ddh/gui/res/icon_history.ico"))
    a.tabs.setTabIcon(4, QIcon("ddh/gui/res/icon_tweak.png"))
    a.tabs.setTabIcon(5, QIcon("ddh/gui/res/icon_graph.ico"))
    a.tabs.setTabIcon(6, QIcon("ddh/gui/res/icon_waves.png"))
    a.setWindowIcon(QIcon("ddh/gui/res/icon_lowell.ico"))

    # new icons
    a.lbl_boat_img.setPixmap(QPixmap("ddh/gui/res/new_icon_boat.png"))
    a.lbl_date_img.setPixmap(QPixmap("ddh/gui/res/calendar.png"))
    a.lbl_brightness_img.setPixmap(QPixmap("ddh/gui/res/new_icon_brightness.png"))
    a.lbl_gps_antenna_img.setPixmap(QPixmap(PATH_GPS_ANTENNA_ICON_START))
    a.lbl_ble_antenna_img.setPixmap(QPixmap(PATH_BLE_ANTENNA_ICON_START))
    a.lbl_cell_wifi_img.setPixmap(QPixmap("ddh/gui/res/new_icon_cell_wifi.png"))
    a.lbl_cloud_img.setPixmap(QPixmap("ddh/gui/res/new_icon_cloud.png"))
    a.lbl_boat_txt.setText(ddh_config_get_vessel_name())
    a.lbl_gps.setText('-\n-')
    a.lbl_box_sn.setText('DDH ' + ddh_config_get_box_sn())
    a.lbl_cloud_txt.setText("-")
    a.bar_dl.setVisible(False)
    a.btn_load_current.animateClick()



    a.setCentralWidget(a.tabs)
    a.tabs.setCurrentIndex(0)
    a.bar_dl.setValue(0)
    if os.path.exists(DEV_SHM_DL_PROGRESS):
        os.unlink(DEV_SHM_DL_PROGRESS)


    # load git commit display or version
    # dc = "version: {}".format(get_ddh_commit())
    dc = f"v. {ddh_get_local_software_version()}"
    a.lbl_commit.setText(dc)

    # checkboxes rerun flag
    do_not_rerun_flag = ddh_does_do_not_rerun_file_flag_exist()
    if do_not_rerun_flag:
        a.chk_rerun.setChecked(False)
    else:
        a.chk_rerun.setChecked(True)

    # test mode
    a.lbl_testmode.setVisible(False)
    if ddh_config_does_flag_file_download_test_mode_exist():
        a.lbl_testmode.setVisible(True)


    # dl statistics
    a.lbl_summary_dl.setVisible(False)


    # edit tab language dropdown
    a.combo_language.addItems(["en", "pt", "fr", "ca", "pl", "sp"])


    # edit tab configuration dropdowns
    a.cb_s3_uplink_type.addItems(["raw", "group"])
    a.cb_skip_in_port.addItems(["False", "True"])

    if ddh_this_box_has_grouped_s3_uplink():
        a.cb_s3_uplink_type.setCurrentIndex(1)
    if ddh_config_is_skip_in_port_enabled():
        a.cb_skip_in_port.setCurrentIndex(1)

    # advanced tab SCF dropdown
    a.cbox_scf.addItems(['none', 'slow', 'mid', 'fast', 'fixed5min'])

    # advanced tab graphs include out of water data
    if os.path.exists(LI_PATH_PLT_ONLY_INSIDE_WATER):
        a.chk_ow.setChecked(False)
    else:
        a.chk_ow.setChecked(True)

    return a



def gui_setup_center_window(my_app):
    """on RPi, DDH app uses full screen"""
    a = my_app

    if linux_is_rpi():
        # rpi is 800 x 480
        a.showFullScreen()
        return

    center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
    geo = a.frameGeometry()
    geo.moveCenter(center)
    a.move(geo.topLeft())

    # cp = QDesktopWidget().availableGeometry().center()
    # qr.moveCenter(cp)
    # a.move(300, 200)
    # a.setFixedWidth(1024)
    # a.setFixedHeight(768)




def gui_setup_manage_graph_test_demo_files():
    a = str(ddh_get_path_to_root_application_folder())
    d0 = a + '/dl_files/00-00-00-00-00-00'
    d1 = a + '/dl_files/11-22-33-44-55-66'
    d2 = a + '/dl_files/99-99-99-99-99-99'
    d3 = a + '/dl_files/55-55-55-55-55-55'
    d4 = a + '/dl_files/33-33-33-33-33-33'
    t0 = a + '/tests/00-00-00-00-00-00'
    t1 = a + '/tests/11-22-33-44-55-66'
    t2 = a + '/tests/99-99-99-99-99-99'
    t3 = a + '/tests/55-55-55-55-55-55'
    t4 = a + '/tests/33-33-33-33-33-33'
    shutil.rmtree(d0, ignore_errors=True)
    shutil.rmtree(d1, ignore_errors=True)
    shutil.rmtree(d2, ignore_errors=True)
    shutil.rmtree(d3, ignore_errors=True)
    shutil.rmtree(d4, ignore_errors=True)
    if ddh_config_does_flag_file_graph_test_mode_exist():
        shutil.copytree(t0, d0)
        shutil.copytree(t1, d1)
        shutil.copytree(t2, d2)
        shutil.copytree(t3, d3)
        shutil.copytree(t4, d4)
        lg.a('copied logger graph test folders')



def gui_tabs_populate_history(my_app):
    """
    fills history table on history tab
    """

    # clear the table
    a = my_app
    a.tbl_his.clear()
    a.tbl_his.tableWidget = None
    a.tbl_his.tableWidget = QTableWidget()
    a.tbl_his.tableWidget.setRowCount(25)
    a.tbl_his.tableWidget.setColumnCount(3)
    a.tbl_his.tableWidget.setSortingEnabled(0)


    # get the history database and order by most recent first
    db = DbHis(ddh_get_path_to_db_history_file())
    rows = db.get_all().values()
    rows = sorted(rows, key=lambda x: x["ep_loc"], reverse=True)


    # we will show just one entry per mac
    fil_r = []
    already = []
    for i, h in enumerate(rows):
        if h['mac'] not in already:
            already.append(h['mac'])
            fil_r.append(h)


    # we only have one, the newest, history entry per mac
    for i, h in enumerate(fil_r):
        e = h["e"]
        e = "success" if e == "ok" else e
        try:
            a.tbl_his.setItem(i, 0, QTableWidgetItem(str(h["SN"])))
            lat = "{:+6.4f}".format(float(h["lat"]))
            lon = "{:+6.4f}".format(float(h["lon"]))
            dt = datetime.datetime.fromtimestamp(int(h["ep_loc"]))
            t = dt.strftime("%b %d %H:%M")
            a.tbl_his.setItem(i, 1, QTableWidgetItem(f"{e} {t} at {lat}, {lon}"))
            a.tbl_his.setItem(i, 2, QTableWidgetItem(str(h['rerun'])))

        except (Exception,) as ex:
            lg.a(f"error, history frame {h} -> {ex}")


    # redistribute columns width
    a.tbl_his.horizontalHeader().resizeSection(0, 150)
    a.tbl_his.horizontalHeader().resizeSection(1, 300)
    a.tbl_his.horizontalHeader().setStretchLastSection(True)

    # columns' title labels
    labels = ["logger", "result", "rerun"]
    a.tbl_his.setHorizontalHeaderLabels(labels)

    # show row numbers
    a.tbl_his.verticalHeader().setVisible(True)



def gui_tabs_populate_note_dropdown(my_app):
    """fills dropdown list in note tab"""

    a = my_app
    a.lst_macs_note_tab.clear()

    j = ddh_config_get_list_of_monitored_serial_numbers()
    for each in j:
        a.lst_macs_note_tab.addItem(each)



def gui_tabs_populate_graph_dropdown_sn(my_app):
    """fills logger serial number dropdown list in graph tab"""

    a = my_app
    a.cb_g_sn.clear()

    if ddh_config_does_flag_file_graph_test_mode_exist():
        a.cb_g_sn.addItem('SNtest000')
        a.cb_g_sn.addItem('SNtest111')
        a.cb_g_sn.addItem('SNtest999')
        a.cb_g_sn.addItem('SNtest555')
        a.cb_g_sn.addItem('SNtest333')
        return

    # from HISTORY database, grab serial numbers, most recent first
    db = DbHis(ddh_get_path_to_db_history_file())
    rows = db.get_all().values()
    rows = sorted(rows, key=lambda x: x["ep_loc"], reverse=True)
    h_sn = []
    for h in rows:
        if not h['SN']:
            continue
        if h['SN'] not in h_sn:
            h_sn.append(h['SN'].lower())


    # from CONFIGURATION file, grab serial numbers
    c_sn = ddh_config_get_list_of_monitored_serial_numbers()
    c_sn = [i.upper() for i in c_sn]


    # add first HISTORY ones, next CONFIGURATION ones
    for i in h_sn:
        a.cb_g_sn.addItem(i)
    for i in c_sn:
        if i not in h_sn:
            a.cb_g_sn.addItem(i)



def gui_setup_buttons(my_app):
    """link buttons and labels clicks and signals"""
    a = my_app

    # hidden buttons
    if not linux_is_rpi():
        a.btn_sms.setEnabled(True)

    # LABEL clicks
    a.lbl_cloud_img.mousePressEvent = a.click_lbl_cloud_img
    a.lbl_brightness_img.mousePressEvent = a.click_lbl_brightness
    a.lbl_brightness_txt.mousePressEvent = a.click_lbl_brightness
    a.lbl_map.mousePressEvent = a.click_lbl_map_pressed


    # BUTTON clicks
    a.btn_expand.clicked.connect(a.click_btn_expand)
    a.btn_known_clear.clicked.connect(a.click_btn_clear_known_mac_list)
    a.btn_see_all.clicked.connect(a.click_btn_see_all_macs)
    # see current macs
    a.btn_see_cur.clicked.connect(a.click_btn_see_monitored_macs)
    a.btn_arrow.clicked.connect(a.click_btn_arrow_move_entries)
    # save configuration
    a.btn_setup_apply.clicked.connect(a.click_btn_edit_tab_save_config)
    a.btn_close_wo_save.clicked.connect(a.click_btn_edit_tab_close_wo_save)
    a.btn_dl_purge.clicked.connect(a.click_btn_purge_dl_folder)
    a.btn_his_purge.clicked.connect(a.click_btn_purge_his_db)
    a.btn_adv_purge_lo.clicked.connect(a.click_btn_adv_purge_lo)
    # load current settings
    a.btn_load_current.clicked.connect(a.click_btn_load_current_json_file)
    a.btn_note_yes.clicked.connect(a.click_btn_note_yes)
    a.btn_note_no.clicked.connect(a.click_btn_note_no)
    a.btn_note_yes_specific.clicked.connect(a.click_btn_note_yes_specific)
    a.chk_rerun.toggled.connect(a.click_chk_rerun)
    a.cb_s3_uplink_type.activated.connect(a.click_chk_s3_uplink_type)
    a.btn_sms.clicked.connect(a.click_btn_sms)
    a.btn_map_next.clicked.connect(a.click_btn_map_next)
    a.chk_ow.toggled.connect(a.click_chk_ow)
    a.btn_shortcuts.clicked.connect(a.click_btn_shortcuts)


    # graph stuff
    a.btn_g_reset.clicked.connect(a.click_graph_btn_reset)
    a.btn_g_next_haul.clicked.connect(a.click_graph_btn_next_haul)
    a.cb_g_sn.activated.connect(a.click_graph_listview_logger_sn)
    a.cb_g_cycle_haul.activated.connect(a.click_graph_lbl_haul_types)
    a.cb_g_switch_tp.activated.connect(a.click_graph_cb_switch_tp)


    # advanced stuff
    a.cbox_scf.activated.connect(a.click_chk_scf)
    a.line_sn.textChanged.connect(a.cb_line_sn_text_changed)




def gui_tabs_hide_settings(ui):
    # find tab ID, index and keep ref
    w = ui.tabs.findChild(QWidget, "tab_setup")
    i = ui.tabs.indexOf(w)
    ui.tab_edit_wgt_ref = ui.tabs.widget(i)
    ui.tabs.removeTab(i)



def gui_show_edit_tab(ui):
    icon = QIcon("ddh/gui/res/icon_setup.png")
    ui.tabs.addTab(ui.tab_edit_wgt_ref, icon, " Setup")
    w = ui.tabs.findChild(QWidget, "tab_setup")
    i = ui.tabs.indexOf(w)
    ui.tabs.setCurrentIndex(i)




def gui_tabs_hide_map(ui):
    w = ui.tabs.findChild(QWidget, "tab_map")
    i = ui.tabs.indexOf(w)
    ui.tab_map_wgt_ref = ui.tabs.widget(i)
    ui.tabs.removeTab(i)



def gui_tabs_hide_models_next_btn(ui):
    ui.btn_map_next.setVisible(False)



def gui_tabs_hide_advanced(ui):
    # find tab ID, index and keep ref
    w = ui.tabs.findChild(QWidget, "tab_advanced")
    i = ui.tabs.indexOf(w)
    ui.tab_advanced_wgt_ref = ui.tabs.widget(i)
    ui.tabs.removeTab(i)



def gui_hide_graph_tab(ui):
    if not linux_is_rpi():
        return
    if os.path.exists('/home/pi/li/.ddh_graph_enabler.json'):
        return
    # find tab ID, index and keep ref
    w = ui.tabs.findChild(QWidget, "tab_graph")
    i = ui.tabs.indexOf(w)
    ui.tab_graph_wgt_ref = ui.tabs.widget(i)
    ui.tabs.removeTab(i)



def gui_show_graph_tab(ui):
    icon = QIcon("ddh/gui/res/icon_graph.ico")
    ui.tabs.addTab(ui.tab_graph_wgt_ref, icon, " Graphs")
    w = ui.tabs.findChild(QWidget, "tab_graph")
    i = ui.tabs.indexOf(w)
    ui.tabs.setCurrentIndex(i)



def gui_show_advanced_tab(ui):
    icon = QIcon("ddh/gui/res/icon_tweak.png")
    ui.tabs.addTab(ui.tab_advanced_wgt_ref, icon, " Advanced")
    w = ui.tabs.findChild(QWidget, "tab_advanced")
    i = ui.tabs.indexOf(w)
    ui.tabs.setCurrentIndex(i)



def gui_show_models_tab(ui):
    icon = QIcon("ddh/gui/res/icon_waves.png")
    ui.tabs.addTab(ui.tab_map_wgt_ref, icon, "  Models")
    w = ui.tabs.findChild(QWidget, "tab_map")
    i = ui.tabs.indexOf(w)
    ui.tabs.setCurrentIndex(i)



def gui_tabs_hide_note(ui):
    w = ui.tabs.findChild(QWidget, "tab_note")
    i = ui.tabs.indexOf(w)
    ui.tab_note_wgt_ref = ui.tabs.widget(i)
    ui.tabs.removeTab(i)



def gui_show_note_tab_delete_black_macs(ui):
    icon = QIcon("ddh/gui/res/icon_exclamation.png")
    ui.tabs.addTab(ui.tab_note_wgt_ref, icon, " Note")
    ui.lbl_note.setText(STR_NOTE_PURGE_BLACKLIST)
    w = ui.tabs.findChild(QWidget, "tab_note")
    i = ui.tabs.indexOf(w)
    ui.tabs.setCurrentIndex(i)



def gui_dict_from_list_view(l_v):
    """grab listview entries 'name mac' and build a dict"""
    d = dict()
    n = l_v.count()
    for _ in range(n):
        it = l_v.item(_)
        pair = it.text().split()
        d[pair[0]] = pair[1]
    return d



def gui_add_to_history_database(mac, e, lat, lon, ep_loc, ep_utc, rerun, u, info):
    # info: 'DO2_AAA'
    info = info.split('_')[0]
    if info == 'DO2':
        info = 'DO-2'
    sn = ddh_config_get_logger_sn_from_mac(mac)
    db = DbHis(ddh_get_path_to_db_history_file())
    e = e + ' ' + info
    db.add(mac, sn, e, lat, lon, ep_loc, ep_utc, rerun, u)



def gui_confirm_by_user(s):
    """ask user to press OK or CANCEL"""
    m = QMessageBox()
    m.setIcon(QMessageBox.Icon.Information)
    m.setWindowTitle("warning")
    m.setText(s)
    choices = QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
    m.setStandardButtons(choices)
    return m.exec() == QMessageBox.StandardButton.Ok




def gui_get_cfg_forget_time_secs():
    t = ddh_config_get_forget_time_seconds()
    assert t >= 600
    return t




def gui_ddh_set_key3_brightness(a, v):
    if not linux_is_rpi():
        lg.a("not raspberry, not setting brightness control via key3_idx")
        return

    b1 = '/sys/class/backlight/rpi_backlight/brightness"'
    b2 = '/sys/class/backlight/10-0045/brightness"'
    # requires root or $ chmod 777 /sys/class.../backlight
    s1 = f'bash -c "echo {str(v)} > {b1}'
    s2 = f'bash -c "echo {str(v)} > {b2}'
    o = sp.DEVNULL
    sp.run(shlex.split(s1), stdout=o, stderr=o)
    sp.run(shlex.split(s2), stdout=o, stderr=o)
    xc = str(ceil(100 * v / 255))
    a.lbl_brightness_txt.setText(xc + "%")
    lg.a(f"setting backlight brightness to {v} ({xc}%), via key3 index")




def gui_setup_brightness(a):
    if not linux_is_rpi():
        lg.a("not raspberry, not setting brightness control")
        a.lbl_brightness_txt.setText('-')
        return

    # key: num_clicks_brightness
    # value: backlight Linux value
    d = {
        0: 12.75, 18: 12.75,
        1: 25.5 * 2, 17: 25.5 * 2,
        2: 25.5 * 3, 16: 25.5 * 3,
        3: 25.5 * 4, 15: 25.5 * 4,
        4: 25.5 * 5, 14: 25.5 * 5,
        5: 25.5 * 6, 13: 25.5 * 6,
        6: 25.5 * 7, 12: 25.5 * 7,
        7: 25.5 * 8, 11: 25.5 * 8,
        8: 25.5 * 9, 10: 25.5 * 9,
        9: 25.5 * 10
    }
    c = int(a.num_clicks_brightness)
    v = int(d[c])
    preferences_set_brightness_clicks(c)
    b1 = '/sys/class/backlight/rpi_backlight/brightness"'
    b2 = '/sys/class/backlight/10-0045/brightness"'
    # requires root or $ chmod 777 /sys/class.../backlight
    s1 = f'bash -c "echo {str(v)} > {b1}'
    s2 = f'bash -c "echo {str(v)} > {b2}'
    o = sp.DEVNULL
    sp.run(shlex.split(s1), stdout=o, stderr=o)
    sp.run(shlex.split(s2), stdout=o, stderr=o)
    xc = str(ceil(100 * v / 255))
    a.lbl_brightness_txt.setText(xc + "%")
    lg.a(f"setting backlight brightness to {v} ({xc}%), index {c}")




def gui_get_my_current_wlan_ssid() -> str:
    """gets connected wi-fi network name, if any"""

    if linux_is_rpi():
        c = "/usr/sbin/iwgetid -r"
        s = sp.run(c, shell=True, stdout=sp.PIPE)
        return s.stdout.decode().rstrip("\n")

    # when developing
    c = "nmcli -t -f name connection show --active"
    rv = sp.run(c, shell=True, stdout=sp.PIPE)
    if rv.returncode == 0:
        # rv.stdout: b'Candy_Corn\nwg0\n'
        return rv.stdout.decode().split("\n")[0]

    # this may return a command not found error
    c = "iwgetid -r"
    rv = sp.run(c, shell=True, stdout=sp.PIPE)
    if rv.returncode == 0:
        wifi_name = rv.stdout.decode().rstrip("\n")
        wifi_name = wifi_name.replace('Auto ', '')
        return wifi_name
    return ""





class DDH(QMainWindow, d_m.Ui_MainWindow):

    # ------------------------------------------------------
    # this function handles the print() from subprocesses
    # we don't have one for standardError because we never
    # use print("<err_blahblah>", file=sys.stderr)
    # ------------------------------------------------------

    @staticmethod
    def _ho(bb):
        s = bytes(bb).decode()
        print(s, end='', flush=True)


    def handle_stdout_aws(self):
        self._ho(self.d_processes[NAME_EXE_AWS].readAllStandardOutput())


    def handle_stdout_ble(self):
        self._ho(self.d_processes[NAME_EXE_BLE].readAllStandardOutput())


    def handle_stdout_cnv(self):
        self._ho(self.d_processes[NAME_EXE_CNV].readAllStandardOutput())


    def handle_stdout_gps(self):
        self._ho(self.d_processes[NAME_EXE_GPS].readAllStandardOutput())


    def handle_stdout_log(self):
        self._ho(self.d_processes[NAME_EXE_LOG].readAllStandardOutput())


    def handle_stdout_net(self):
        self._ho(self.d_processes[NAME_EXE_NET].readAllStandardOutput())


    def handle_stdout_sqs(self):
        self._ho(self.d_processes[NAME_EXE_SQS].readAllStandardOutput())


    def handle_state_ble(self, state):
        self.process_state_ble = d_process_states[state]


    def _cb_timer_six_hours(self):
        g = ddh_gps_get()
        if g:
            notify_ddh_alive(g)
            self.timer_six_hours.start(3600 * 6 * 1000)
        else:
            self.timer_six_hours.start(3600 * 1 * 1000)


    def _cb_timer_plot(self):
        p_r = r.get(RD_DDH_GUI_PLOT_REASON)
        if p_r:
            # p_r: 'ble', 'user', 'hauls_next', 'hauls_labels'
            # BLE needs a FOLDER path written on another redis key
            p_r = p_r.decode()
            lg.a(f"received plot request, reason = {p_r}")
            graph_process_n_draw(self, reason=p_r)
            r.delete(RD_DDH_GUI_PLOT_REASON)



    def _cb_timer_cpu_temperature(self):
        m = psutil.virtual_memory()
        if int(m.percent) > 75:
            ma = m.available / 1e9
            s = "statistics, {:.2f}% GB of RAM used, {:.2f} GB available"
            lg.a(s.format(m.percent, ma))

        # measure temperature of DDH box, tell when too high
        self.timer_cpu_hot.stop()
        c = "/usr/bin/vcgencmd measure_temp"
        rv = sp.run(c, shell=True, stderr=sp.PIPE, stdout=sp.PIPE)

        try:
            ans = rv.stdout
            if ans:
                # ans: b'temp=30.1'C'
                ans = ans.replace(b"\n", b"")
                ans = ans.replace(b"'C", b"")
                ans = ans.replace(b"temp=", b"")
                ans = float(ans.decode())
                if ans > 80:
                    lg.a(f"debug, box temperature {ans} degrees Celsius")

        except (Exception,) as ex:
            lg.a(f"error, getting vcgencmd -> {ex}")

        # 600 seconds = 10 minutes
        self.timer_cpu_hot.start(600000)



    def click_btn_clear_known_mac_list(self):
        self.lst_mac_org.clear()
        self.lst_mac_dst.clear()


    def click_btn_expand(self):
        self.frame_2of2_expanded = not self.frame_2of2_expanded
        ls_controls_disappear = (
            self.lbl_gps_antenna_img,
            self.lbl_gps_antenna_txt,
            self.lbl_ble_antenna_img,
            self.lbl_ble_antenna_txt,
            self.lbl_cell_wifi_img,
            self.lbl_cell_wifi_txt
        )
        for i in ls_controls_disappear:
            i.setVisible(self.frame_2of2_expanded)
        s = '↑' if self.frame_2of2_expanded else '↓'
        self.btn_expand.setText(s)




    def click_btn_see_all_macs(self):
        """ loads (mac, name) pairs from all macs config section """
        self.lst_mac_org.clear()
        pp = ddh_get_contents_of_config_file_all_macs()
        for m, n in pp.items():
            s = f"{m}  {n}"
            self.lst_mac_org.addItem(s)



    def click_btn_see_monitored_macs(self):
        """ loads (mac, name) pairs from config file """
        self.lst_mac_org.clear()
        pp = ddh_config_get_monitored_pairs()
        for m, n in pp.items():
            s = f"{m}  {n}"
            self.lst_mac_org.addItem(s)


    def click_btn_arrow_move_entries(self):
        """ move items in upper box to lower box """
        ls = self.lst_mac_org.selectedItems()
        o = dict()
        for i in ls:
            pair = i.text().split()
            o[pair[0]] = pair[1]

        # dict from all items in lower box
        b = self.lst_mac_dst
        d_b = gui_dict_from_list_view(b)
        d_b.update(o)

        # update lower box
        self.lst_mac_dst.clear()
        for m, n in d_b.items():
            if '-' in m:
                s = f'MAC {m} is wrong'
                gui_confirm_by_user(s)
                continue
            s = f"{m}  {n}"
            self.lst_mac_dst.addItem(s)



    def click_btn_edit_tab_close_wo_save(self):
        lg.a('edit tab: pressed the close without save button')
        self.tab_edit_hide = not self.tab_edit_hide
        gui_tabs_hide_settings(self)
        self.tabs.setCurrentIndex(0)



    def click_btn_edit_tab_save_config(self):
        """SAVES a config file"""

        l_v = self.lst_mac_dst
        if not l_v:
            ans_mb = QMessageBox.question(
                self,
                'Question',
                "Do you want to save an empty logger list?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if ans_mb == QMessageBox.StandardButton.No:
                return
            lg.a('warning, saved a config without macs after confirmation')

        # pairs: {'11:22:33:44:55:66': '1234567'}
        pairs = gui_dict_from_list_view(l_v)

        # input: forget_time
        try:
            t = int(self.lne_forget.text())
        except ValueError:
            t = 0
        self.lne_forget.setText(str(t))

        # vessel name before saving config
        ves = self.lne_vessel.text()
        if not ves:
            self.lbl_setup_result.setText("bad empty vessel name")
            return
        if '&' in ves:
            self.lbl_setup_result.setText("bad vessel name contains &")
            return


        lang = self.combo_language.currentIndex()

        # skip in port
        sk = self.cb_skip_in_port.currentIndex()

        # do not allow to save a bad forget time
        if t < 600:
            self.lbl_setup_result.setText("bad forget_time")
            return


        save_cfg = ddh_config_load_file()
        save_cfg['behavior']["forget_time"] = t
        save_cfg['behavior']['ship_name'] = ves
        save_cfg['behavior']['language'] = lang
        save_cfg['monitored_macs'] = pairs
        save_cfg['flags']['skip_dl_in_port_en'] = sk
        ddh_config_save_to_file(save_cfg)


        # we seem good to go
        s = "restarting DDH..."
        self.lbl_setup_result.setText(s)
        lg.a("closing GUI by save config button")

        # show the previous thing
        QCoreApplication.processEvents()
        time.sleep(1)

        # also kill the DDH API so crontab restarts it
        lg.a("kill API by save config button")
        c = f'killall {NAME_EXE_API}'
        sp.run(c, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)

        # bye, bye DDH
        self.close_my_ddh()




    def click_lbl_brightness(self, _):
        # no shift key, adjust DDH brightness
        # 5,20,30,40,50,60,70,80,90,100,90,80,70,60,50,40,30,20
        if not linux_is_rpi():
            lg.a('clicked brightness icon on development computer')
            return
        self.num_clicks_brightness = (self.num_clicks_brightness + 1) % 18
        gui_setup_brightness(self)



    @staticmethod
    def click_btn_purge_dl_folder():
        """deletes contents in 'download files' folder"""

        d = str(ddh_get_path_to_folder_dl_files())
        lg.a("pressed btn_purge_dl_folder")
        s = "sure to delete dl_files folder?"
        if not gui_confirm_by_user(s):
            return

        try:
            if "dl_files" not in str(d):
                return
            shutil.rmtree(str(d), ignore_errors=True)
        except OSError as e:
            lg.a(f"error {d} : {e}")



    def click_btn_adv_purge_lo(self):
        gui_show_note_tab_delete_black_macs(self)



    def click_btn_sms(self):
        s: str
        if is_it_time_to('sms', 3600):
            s = 'sending'
            notify_via_sms('sms')
        else:
            s = 'already sent'
        self.btn_sms.setText(s)
        QCoreApplication.processEvents()
        time.sleep(2)
        self.btn_sms.setText("tech support")



    def click_btn_purge_his_db(self):
        """ deletes contents in history database """

        s = "sure to purge history?"
        if gui_confirm_by_user(s):
            p = ddh_get_path_to_db_history_file()
            db = DbHis(p)
            lg.a(f"pressed btn_purge_dl_folder, path = {p}")
            db.delete_all()
        gui_tabs_populate_history(self)



    def click_btn_load_current_json_file(self):
        """ updates EDIT tab from current config file """
        ves = ddh_config_get_vessel_name()
        f_t = gui_get_cfg_forget_time_secs()
        lang = ddh_config_get_language_index()
        self.lne_vessel.setText(ves)
        self.lne_forget.setText(str(f_t))
        self.combo_language.setCurrentIndex(lang)
        # set index of TDO SCF profiling
        scf_index = 0
        for i, v in enumerate(('slow', 'mid', 'fast', )):
            pdf = f'{ddh_get_path_to_folder_scripts()}/../.decided_scf_{v}.toml'
            if os.path.exists(pdf):
                scf_index = i + 1
        self.cbox_scf.setCurrentIndex(scf_index)



    def click_btn_note_yes_specific(self):
        s = self.lbl_note.text()

        # only affects purge_macs note, not BLE GPS one
        if s == STR_NOTE_PURGE_BLACKLIST:
            try:
                path_fol = ddh_get_path_to_folder_macs_black()
                n = self.lst_macs_note_tab.count()

                for i in range(n):
                    if not self.lst_macs_note_tab.item(i).isSelected():
                        continue

                    sn = self.lst_macs_note_tab.item(i).text()
                    mac = ddh_config_get_logger_mac_from_sn(sn)
                    lg.a(f'smart lock-out, user removed mac {mac}')
                    slo_delete(mac)
                    if mac:
                        mac = mac.replace(":", "-")
                        mask = f"{path_fol}/{mac}@*"
                        ff = glob.glob(mask)
                        for f in ff:
                            os.unlink(f)
                            lg.a(f"cleared lock-out selective for {f}")
                    else:
                        lg.a("warning, could not clear lock-out selective")

            except (OSError, Exception) as ex:
                lg.a(f"error, {ex}")
                return

        lg.a("pressed note button 'OK'")
        flag = ddh_get_path_to_app_override_flag_file()
        pathlib.Path(flag).touch()
        lg.a("BLE op conditions override set as 1")
        gui_tabs_hide_note(self)
        self.tabs.setCurrentIndex(0)

        # for forcing HBW command to work
        self._create_hbw_flags()



    @staticmethod
    def _create_hbw_flags():
        for m in ddh_config_get_list_of_monitored_macs():
            path = ddh_get_template_of_path_of_hbw_flag_file().format(m)
            # path: /tmp/ddh_hbw_d0:2e:ab:d9:30:66.flag
            pathlib.Path(path).touch()



    def click_btn_note_yes(self):
        s = self.lbl_note.text()

        # only affects purge_macs note, not BLE GPS one
        if s == STR_NOTE_PURGE_BLACKLIST:
            try:
                lg.a(f'smart lock-out, user removed ALL macs')
                slo_delete_all()
                path_fol = ddh_get_path_to_folder_macs_black()
                mask = f"{path_fol}/*"
                ff = glob.glob(mask)
                for f in ff:
                    os.unlink(f)
                    bn = os.path.basename(f)
                    lg.a(f"warning, clicked purge lock-out for {bn}")

            except (OSError, Exception) as ex:
                lg.a(f"error click_btn_note_yes -> {ex}")
                return

        lg.a("pressed note button specific 'OK'")
        flag = ddh_get_path_to_app_override_flag_file()
        pathlib.Path(flag).touch()
        lg.a("BLE op conditions override set as 1")
        gui_tabs_hide_note(self)
        self.tabs.setCurrentIndex(0)

        # for forcing HBW command to work
        self._create_hbw_flags()



    def click_btn_note_no(self):
        gui_tabs_hide_note(self)
        self.tabs.setCurrentIndex(0)
        lg.a("pressed note button 'CANCEL'")



    @staticmethod
    def close_my_ddh():
        lg.a("closed by upper-right X in OS window or context_menu or saving config")
        sys.stderr.close()
        gui_kill_all_processes()
        # so DDH GUI is the last to be in OS
        time.sleep(1)
        os._exit(0)



    def closeEvent(self, ev):
        ev.accept()
        self.close_my_ddh()




    def keyPressEvent(self, ev):
        known_keys = (
            Qt.Key.Key_1,
            Qt.Key.Key_2,
            Qt.Key.Key_3,
        )
        if ev.key() not in known_keys:
            lg.a(f"warning, unknown keypress {ev.key()}")
            return

        # identify KEYBOARD key pressed, although we simulate side box keys
        if ev.key() == Qt.Key.Key_1:
            lg.a("user pressed box side button 1")
            self.num_clicks_brightness = (self.num_clicks_brightness + 1) % 18
            gui_setup_brightness(self)

        elif ev.key() == Qt.Key.Key_2:
            lg.a("user pressed box side button 2")
            gui_show_note_tab_delete_black_macs(self)

        elif ev.key() == Qt.Key.Key_3:
            lg.a("user pressed box side button 3")
            # they decided 0 but, long ago, minimum was 12
            gui_ddh_set_key3_brightness(self, 0)



    def click_lbl_map_pressed(self, ev):
        h = self.lbl_map.height()
        w = self.lbl_map.width()
        path_map_file = self.filename_model
        x = ev.pos().x()
        y = ev.pos().y()
        # x starts left, y starts top
        print('click', h, w, path_map_file, x, y)
        if path_map_file and '_dtm' in path_map_file:
            if (.3 * w <= x <= .6 * w and
                    .3 * h <= y <= .6 * h):
                print('click dtm central area')



    def click_chk_s3_uplink_type(self, _):
        i = self.cb_s3_uplink_type.currentIndex()
        flag_file = LI_PATH_GROUPED_S3_FILE_FLAG
        if i == 0:
            # raw
            os.unlink(flag_file)
        else:
            # grouped
            Path(flag_file).touch(exist_ok=True)



    def click_lbl_cloud_img(self, _):
        self.lbl_cloud_txt.setText("checking")
        r.delete(RD_DDH_AWS_SYNC_REQUEST)
        lg.a("user clicked cloud icon")



    def click_chk_rerun(self, _):
        if self.chk_rerun.isChecked():
            # checked = run -> clear "do_not_rerun" flag
            ddh_clear_do_not_rerun_file_flag()
        else:
            ddh_create_do_not_rerun_file_flag()



    def click_chk_ow(self, _):
        path = LI_PATH_PLT_ONLY_INSIDE_WATER
        if self.chk_ow.isChecked():
            lg.a('user selected graphs INCLUDE out-of-water data')
            if os.path.exists(path):
                os.unlink(path)
        else:
            lg.a('user selected graphs SKIP out-of-water data')
            pathlib.Path(path).touch()


    def click_btn_shortcuts(self, _):
        bp = self.btn_shortcuts.mapToGlobal(QtCore.QPoint(0, 0))
        x = bp.x() - 50
        y = bp.y() - 50
        p = QPoint(x, y)
        self.context_menu.exec(p)


    def gui_show_edit_tab(self, _):
        gui_show_edit_tab(self)


    def gui_show_advanced_tab(self, _):
        gui_show_advanced_tab(self)


    def click_btn_map_next(self, _):
        fol = str(ddh_get_path_to_folder_gui_res())
        self.i_good_models = (self.i_good_models + 1) % self.n_good_models
        lg.a(f'showing map #{self.i_good_models}')
        now = str(datetime.datetime.now().strftime('%Y%m%d'))
        d = {
            0: f"{fol}/{now}_F_dtm.gif",
            1: f"{fol}/{now}_F_gom.gif",
            2: f"{fol}/{now}_F_mab.gif"
        }

        try:
            m = d[self.i_good_models]
            if not os.path.exists(m):
                m = f"{fol}/error_models.gif"
            else:
                preferences_set_models_index(self.i_good_models)
        except (Exception, ) as ex:
            lg.a(f'error, when next map => {ex}')
            m = f"{fol}/error_models.gif"

        self.gif_map = QMovie(m)
        self.lbl_map.setMovie(self.gif_map)
        self.gif_map.start()
        self.filename_model = m



    def cb_line_sn_text_changed(self):
        v = self.line_sn.text()
        if v == "":
            return
        self.lst_mac_org.clear()
        pp = ddh_get_contents_of_config_file_all_macs()
        for m, sn in pp.items():
            if str(sn).startswith(v):
                s = f"{m}  {sn}"
                self.lst_mac_org.addItem(s)



    def click_chk_scf(self):
        j = self.cbox_scf.currentIndex()
        d = {
            0: 'none',
            1: 'slow',
            2: 'mid',
            3: 'fast',
            4: 'fixed5min'
        }
        v = d[j]
        fol = ddh_get_path_to_folder_scripts()
        fol_ddh = f'{fol}/..'

        # delete the decided file
        if v == 'none':
            for i in ('slow', 'mid', 'fast', 'fixed5min'):
                pdf = f'{fol_ddh}/.decided_scf_{i}.toml'
                if os.path.exists(pdf):
                    os.unlink(pdf)
            return

        # decide the origin file
        org_scf_file = f'{fol}/script_logger_tdo_deploy_cfg_{v}.toml'
        if not os.path.exists(org_scf_file):
            lg.a(f'error, cannot find {org_scf_file}')
            return

        # copy the origin file as decided file
        c = f'cp {org_scf_file} {fol_ddh}/.decided_scf_{v}.toml'
        rv = sp.run(c, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        if rv.returncode:
            lg.a(f'error: copying SCF files {rv.stderr}')
            return

        lg.a(f'set .decided_scf_{v}.toml as SCF file')



    def click_graph_btn_reset(self):
        self.g.getPlotItem().enableAutoRange()
        graph_request(reason='user')


    @staticmethod
    def click_graph_listview_logger_sn( _):
        graph_request(reason='user')


    @staticmethod
    def click_graph_btn_next_haul():
        graph_request(reason='hauls_next')


    @staticmethod
    def click_graph_lbl_haul_types(_):
        graph_request(reason='hauls_labels')



    @staticmethod
    def click_graph_cb_switch_tp(_):
        # todo: is this working?
        graph_request(reason='user')



    def _cb_timer_gui_one_second(self):

        # update DATE and UPTIME fields, also a COUNTER for incremental stuff
        self.lbl_date_txt.setText(datetime.datetime.now().strftime("%b %d %H:%M:%S"))
        _up = datetime.timedelta(seconds=time.perf_counter() - _g_ts_gui_boot)
        self.lbl_uptime.setText("uptime " + str(_up).split(".")[0])
        i = int(time.time()) % 4


        # force GUI normally show FIRST tab
        if self.tabs.currentIndex() != 0 and int(time.perf_counter()) % 1800 == 0:
            self.tabs.setCurrentIndex(0)


        # update MODELS tab, prevent freeze at boot
        if _calc_app_uptime() > 10 and not r.exists(RD_DDH_GUI_MODELS_UPDATE):
            gui_populate_models_tab(self)
            r.setex(RD_DDH_GUI_MODELS_UPDATE, 3600, 1)



        # show if any process is not there
        k = RD_DDH_GUI_REFRESH_PROCESSES_PRESENT
        if not r.exists(k):
            gui_check_all_processes()
            r.setex(k, 10, 1)



        # refresh TEXT in main tab left column
        ls_fields_to_refresh = {
            RD_DDH_GUI_REFRESH_HISTORY_TABLE: None,
            RD_DDH_BLE_ANTENNA: self.lbl_ble_antenna_txt,
            RD_DDH_GPS_ANTENNA: self.lbl_gps_antenna_txt,
            RD_DDH_AWS_PROCESS_STATE: self.lbl_cloud_txt,
            RD_DDH_NET_PROCESS_OUTPUT: self.lbl_cell_wifi_txt,
        }
        for rd_key, field in ls_fields_to_refresh.items():
            v = r.get(rd_key)
            v = v.decode() if v else ''

            # pre-processing
            if rd_key == RD_DDH_GUI_REFRESH_HISTORY_TABLE:
                if v:
                    gui_tabs_populate_history(self)
                    gui_tabs_populate_graph_dropdown_sn(self)
                    r.delete(RD_DDH_GUI_REFRESH_HISTORY_TABLE)
                continue

            field.setText(v)

            # post-processing
            if rd_key == RD_DDH_NET_PROCESS_OUTPUT:
                if v in ("wifi", "wi-fi"):
                    ssid = gui_get_my_current_wlan_ssid()
                    self.lbl_cell_wifi_txt.setText(ssid)




        # update GPS field in "Details" tab
        g = ddh_gps_get()
        if g:
            lat, lon, dt, speed = g
            lat = '{:+6.4f}'.format(float(lat))
            lon = '{:+6.4f}'.format(float(lon))
            self.lbl_gps.setText(f'{lat}\n{lon}')
        else:
            self.lbl_gps.setText("-\n-")
            self.lbl_gps_sat.setText("-")
            self.lbl_gps_antenna_txt.setText('searching')



        # refresh ICON GPS in main tab left column
        k = RD_DDH_GUI_REFRESH_GPS_ICON_AUTO
        if not r.exists(k):
            p = PATH_GPS_ANTENNA_ICON_OK if g else PATH_GPS_ANTENNA_ICON_ERROR
            self.lbl_gps_antenna_img.setPixmap(QPixmap(p))
            r.setex(k, 10, 1)


        # refresh ICON BLE in main tab left column
        k = RD_DDH_GUI_REFRESH_BLE_ICON_AUTO
        if not r.exists(k):
            b = self.lbl_ble_antenna_txt.text()
            p = PATH_BLE_ANTENNA_ICON_OK
            if 'error' in b:
                p = PATH_BLE_ANTENNA_ICON_ERROR
            if self.process_state_ble == 'Not running':
                p = PATH_BLE_ANTENNA_ICON_ERROR
            self.lbl_ble_antenna_img.setPixmap(QPixmap(p))
            r.setex(k, 10, 1)


        # refresh icon cell-wifi in main tab left column
        k = RD_DDH_GUI_REFRESH_CELL_WIFI_ICON_AUTO
        if not r.exists(k):
            via = r.get(RD_DDH_NET_PROCESS_OUTPUT)
            p = PATH_CELL_ICON_ERROR if via == 'none' else PATH_CELL_ICON_OK
            self.lbl_cell_wifi_img.setPixmap(QPixmap(p))
            r.setex(k, 10, 1)


        # refresh DDH side box buttons
        if r.exists(RD_DDH_GUI_BOX_SIDE_BUTTON_TOP):
            self.keyPressEvent(ButtonPressEvent(Qt.Key.Key_1))
            r.delete(RD_DDH_GUI_BOX_SIDE_BUTTON_TOP)
        if r.exists(RD_DDH_GUI_BOX_SIDE_BUTTON_MID):
            self.keyPressEvent(ButtonPressEvent(Qt.Key.Key_2))
            r.delete(RD_DDH_GUI_BOX_SIDE_BUTTON_MID)
        if r.exists(RD_DDH_GUI_BOX_SIDE_BUTTON_LOW):
            self.keyPressEvent(ButtonPressEvent(Qt.Key.Key_3))
            r.delete(RD_DDH_GUI_BOX_SIDE_BUTTON_LOW)



        # update MAIN icon
        code, text = app_state_get()
        code = code.decode() if code else ''
        text = text.decode() if text else ''
        self.bar_dl.setVisible(False)


        # debug
        # print(f'code {code} \n text {text}')
        pi = ''
        if code in (EV_GUI_BOOT, ):
            pi = PATH_MAIN_BOOT
        elif code in (EV_CONF_BAD, ):
            pi = PATH_MAIN_CONF_BAD
        elif code in (EV_NO_ASSIGNED_LOGGERS,):
            pi = PATH_MAIN_NO_LOGGERS_ASSIGNED
        elif code in (EV_GPS_IN_PORT, ):
            pi = PATH_MAIN_IN_PORT
        elif code in (EV_GPS_WAITING_BOOT, ):
            pi = PATH_TEMPLATE_MAIN_GPS_BOOT_IMG.format(i)
            t = r.ttl(RD_DDH_GPS_COUNTDOWN_FOR_FIX_AT_BOOT) or 0
            text = f'{t_str(STR_EV_GPS_WAITING_BOOT)} {t} secs'
        elif code in (EV_GPS_SYNC_CLOCK, ):
            pi = PATH_TEMPLATE_MAIN_GPS_CLOCK_IMG
        elif code in (EV_BLE_CONNECTING, ):
            # todo: does this one icon appear?
            pi = PATH_MAIN_BLE_CONNECTING
        elif code in (EV_BLE_DL_OK, ):
            pi = PATH_MAIN_BLE_DL_OK
        elif code in (EV_BLE_DL_OK_NO_RERUN,):
            pi = PATH_MAIN_BLE_DL_OK_NO_RERUN
        elif code in (EV_BLE_DL_ERROR,):
            pi = PATH_MAIN_BLE_DL_ERROR
        elif code in (EV_BLE_DL_NO_NEED,):
            pi = PATH_MAIN_BLE_DL_NO_NEED
        elif code in (EV_BLE_LOW_BATTERY, ):
            pi = PATH_MAIN_BLE_DL_LOW_BATTERY
        elif code in (EV_BLE_DL_RETRY, ):
            pi = PATH_MAIN_BLE_DL_RETRY
        elif code in (EV_BLE_DL_PROGRESS, ):
            pi = PATH_MAIN_BLE_DL_PROGRESS
            self.bar_dl.setVisible(True)
            try:
                with open(DEV_SHM_DL_PROGRESS, 'r') as f:
                    v = f.read()
                    v = int(float(v))
                    self.bar_dl.setValue(v)
            except (Exception,):
                pass
        elif code in (EV_GPS_HW_ERROR, ):
            pi = PATH_MAIN_GPS_HW_ERROR
        elif code in (EV_BLE_SCAN, ):
            pi = PATH_TEMPLATE_MAIN_BLE_SCAN_IMG.format(i)
        else:
            print('*1* unknown state code', code)
            print('*1* unknown state text', text)



        # update main icon or not
        k = RD_DDH_GUI_STATE_EVENT_ICON_LOCK
        lock_icon = 0 if not r.exists(k) else r.ttl(k)
        if code in (EV_BLE_SCAN, ) and lock_icon:
            pass
        else:
            self.lbl_main_txt.setText(text)
            if pi:
                self.lbl_main_img.setPixmap(QPixmap(pi))
            else:
                print('*2* unknown state code', code)
                print('*2* unknown state text', text)


        # show or not the statistics box
        if t_str(STR_EV_BLE_DL_OK) in self.lbl_main_txt.text():
            s = r.get(RD_DDH_GUI_GRAPH_STATISTICS)
            s = s.decode() if s else ''
            s = s.replace('mg_l', 'mg/l')
            self.lbl_summary_dl.setText(s)
            self.lbl_summary_dl.setVisible(True)
        else:
            self.lbl_summary_dl.setVisible(False)




    # =============
    # DDH GUI boot
    # =============

    def __init__(self):

        super(DDH, self).__init__()
        gui_init_redis()
        gui_check_config_file_is_ok()
        app_state_set(EV_GUI_BOOT, t_str(STR_EV_GUI_BOOT))


        # we want new processes
        self.d_processes = {}
        gui_kill_all_processes()
        self.d_processes[NAME_EXE_LOG] = QProcess()
        self.d_processes[NAME_EXE_AWS] = QProcess()
        self.d_processes[NAME_EXE_BLE] = QProcess()
        self.d_processes[NAME_EXE_CNV] = QProcess()
        self.d_processes[NAME_EXE_GPS] = QProcess()
        self.d_processes[NAME_EXE_NET] = QProcess()
        self.d_processes[NAME_EXE_SQS] = QProcess()

        # prints of subprocesses are handled by pyqt
        self.d_processes[NAME_EXE_LOG].readyReadStandardOutput.connect(self.handle_stdout_log)
        self.d_processes[NAME_EXE_AWS].readyReadStandardOutput.connect(self.handle_stdout_aws)
        self.d_processes[NAME_EXE_BLE].readyReadStandardOutput.connect(self.handle_stdout_ble)
        self.d_processes[NAME_EXE_CNV].readyReadStandardOutput.connect(self.handle_stdout_cnv)
        self.d_processes[NAME_EXE_GPS].readyReadStandardOutput.connect(self.handle_stdout_gps)
        self.d_processes[NAME_EXE_NET].readyReadStandardOutput.connect(self.handle_stdout_net)
        self.d_processes[NAME_EXE_SQS].readyReadStandardOutput.connect(self.handle_stdout_sqs)
        self.d_processes[NAME_EXE_BLE].stateChanged.connect(self.handle_state_ble)
        self.d_processes[NAME_EXE_LOG].start('python3', [f'{NAME_EXE_LOG}.py'])
        self.d_processes[NAME_EXE_AWS].start('python3', [f'{NAME_EXE_AWS}.py'])
        self.d_processes[NAME_EXE_BLE].start('python3', [f'{NAME_EXE_BLE}.py'])
        self.d_processes[NAME_EXE_CNV].start('python3', [f'{NAME_EXE_CNV}.py'])
        self.d_processes[NAME_EXE_GPS].start('python3', [f'{NAME_EXE_GPS}.py'])
        self.d_processes[NAME_EXE_NET].start('python3', [f'{NAME_EXE_NET}.py'])
        self.d_processes[NAME_EXE_SQS].start('python3', [f'{NAME_EXE_SQS}.py'])


        # create variables
        self.process_state_ble = ''
        self.bright_idx = 2
        self.tab_edit_hide = True
        self.tab_advanced_hide = True
        self.tab_edit_wgt_ref = None
        self.tab_map_wgt_ref = None
        self.tab_note_wgt_ref = None
        self.tab_advanced_wgt_ref = None
        self.tab_graph_wgt_ref = None
        # brightness 9 is index for 100%
        self.num_clicks_brightness = preferences_get_brightness_clicks()
        self.i_good_models = preferences_get_models_index()
        self.gif_map = None
        self.n_good_models = 0
        self.filename_model = None


        gui_setup_view(self)
        gui_setup_center_window(self)
        gui_setup_buttons(self)
        gui_setup_brightness(self)
        gui_setup_side_buttons_box()


        # tabs
        gui_tabs_hide_settings(self)
        gui_tabs_hide_advanced(self)
        gui_tabs_hide_note(self)
        gui_tabs_populate_history(self)
        gui_tabs_hide_models_next_btn(self)
        gui_tabs_populate_note_dropdown(self)
        gui_tabs_populate_graph_dropdown_sn(self)



        # graphing tab
        self.g = pg.PlotWidget(axisItems={'bottom': pg.DateAxisItem()})
        self.lay_g_h2.addWidget(self.g)
        self.g.setBackground('w')
        self.btn_g_next_haul.setEnabled(False)
        self.btn_g_next_haul.setVisible(False)
        self.lbl_graph_busy.setVisible(False)
        self.cb_g_switch_tp.setVisible(False)
        gui_setup_manage_graph_test_demo_files()


        # GUI timers
        self.timer_gui_one_second = QTimer()
        self.timer_six_hours = QTimer()
        self.timer_cpu_hot = QTimer()
        self.timer_plot = QTimer()
        self.timer_gui_one_second.timeout.connect(self._cb_timer_gui_one_second)
        self.timer_six_hours.timeout.connect(self._cb_timer_six_hours)
        self.timer_cpu_hot.timeout.connect(self._cb_timer_cpu_temperature)
        self.timer_plot.timeout.connect(self._cb_timer_plot)
        self.timer_gui_one_second.start(1 * 1000)
        # well, the first will be less than 6 hours, more like 10 seconds
        self.timer_six_hours.start(10 * 1000)
        self.timer_plot.start(1000)
        if linux_is_rpi():
            self.timer_cpu_hot.start(1000)


        # build context menu shortcuts
        self.context_menu = QMenu(self)
        cm_action_minimize = self.context_menu.addAction("minimize")
        cm_action_quit = self.context_menu.addAction("quit")
        cm_action_edit_tab = self.context_menu.addAction("edit tab")
        cm_action_advanced_tab = self.context_menu.addAction("advanced tab")
        cm_action_minimize.triggered.connect(self.showMinimized)
        cm_action_quit.triggered.connect(self.close_my_ddh)
        cm_action_edit_tab.triggered.connect(self.gui_show_edit_tab)
        cm_action_advanced_tab.triggered.connect(self.gui_show_advanced_tab)


        # left panel
        geo = self.frameGeometry()
        _w = geo.width()
        self.left_frame.setMinimumWidth(int(_w * .25))
        self.left_frame.setMaximumWidth(int(_w * .25))
        self.frame_2of2_expanded = False
        ls_controls_disappear = (
            self.lbl_gps_antenna_img,
            self.lbl_gps_antenna_txt,
            self.lbl_ble_antenna_img,
            self.lbl_ble_antenna_txt,
            self.lbl_cell_wifi_img,
            self.lbl_cell_wifi_txt
        )
        for i in ls_controls_disappear:
            i.setVisible(False)
        self.btn_expand.setText('↓')


        lg.a("OK, finished booting graphical user interface")




def main_ddh_gui():
    if linux_is_process_running_strict(NAME_EXE_BRT):
        print('error: BRT running, DDH should not')
        return

    if linux_is_process_running_strict(NAME_EXE_DDH):
        print('error: DDH myself already running, leaving')
        return

    setproctitle.setproctitle(NAME_EXE_DDH)

    app = QApplication(sys.argv)
    ex = DDH()
    ex.show()
    rv = app.exec()

    # see DDH is doing well
    k = RD_DDH_GUI_RV
    if rv:
        r.setex(f'{k}_{int(time.time())}', 600, 1)
    ls = list(r.scan_iter(f'{k}_*', count=6))
    if len(ls) >= 5:
        notify_error_sw_crash()
    if rv == 0 or len(ls) >= 5:
        for i in ls:
            r.delete(i)

    sys.exit(app.exec())




if __name__ == "__main__":
    assert sys.version_info >= (3, 9)
    signal.signal(signal.SIGINT, cb_when_ddh_receives_ctrl_c)
    signal.signal(signal.SIGTERM, cb_when_ddh_receives_kill_signal)
    main_ddh_gui()

