
p = 'ddh:gui:'
# main icon and main text management
RD_DDH_GUI_STATE_EVENT_CODE = p + 'state_gui_event_code'
RD_DDH_GUI_STATE_EVENT_TEXT = p + 'state_gui_event_text'
RD_DDH_GUI_STATE_EVENT_ICON_LOCK = p + 'state_gui_event_icon_lock'
# why are we plotting and which folder
RD_DDH_GUI_PLOT_REASON = p + 'plot_reason'
RD_DDH_GUI_PLOT_FOLDER = p + 'plot_folder'
# flags for hardware buttons outside DDH box
RD_DDH_GUI_NO_EXPIRES_BOX_SIDE_BUTTON_TOP = p + 'side_button_top'
RD_DDH_GUI_NO_EXPIRES_BOX_SIDE_BUTTON_MID = p + 'side_button_mid'
RD_DDH_GUI_NO_EXPIRES_BOX_SIDE_BUTTON_LOW = p + 'side_button_low'
# sensor summary box in main tab
RD_DDH_GUI_GRAPH_STATISTICS = p + 'graph_statistics'
# checked outside the ddh_main
RD_DDH_GUI_RV = p + 'rv'




p = 'ddh:gui:refresh:'
RD_DDH_GUI_NO_EXPIRES_PERIODIC_REFRESH_HISTORY_TABLE = p + 'history_table'
RD_DDH_GUI_PERIODIC_REFRESH_MODELS = p + 'models_update'
RD_DDH_GUI_PERIODIC_CHECK_PROCESSES_ARE_RUNNING = p + 'processes_present'
RD_DDH_GUI_PERIODIC_CHECK_ICON_BLE = p + 'ble_icon'
RD_DDH_GUI_PERIODIC_CHECK_ICON_GPS = p + 'gps_icon'
RD_DDH_GUI_PERIODIC_CHECK_ICON_NET = p + 'cell_wifi_icon'






p = 'ddh:ble:'
RD_DDH_BLE_NO_EXPIRES_RESET_REQ = p + 'linux_reset_req'
RD_DDH_BLE_SEMAPHORE = p + 'semaphore'
# antenna can be external or internal
RD_DDH_BLE_NO_EXPIRES_ANTENNA = p + 'antenna_ble'




p = 'ddh:gps:'
# contains a good GPS position
RD_DDH_GPS_FIX_POSITION = p + 'fix'
RD_DDH_GPS_COUNTDOWN_FOR_FIX_AT_BOOT = p + 'countdown_for_fix_at_boot'
RD_DDH_GPS_FIX_SPEED = p + 'speed'
RD_DDH_GPS_FIX_NUMBER_OF_SATELLITES = p + 'ns_view'
# firmware version of the hat
RD_DDH_GPS_NO_EXPIRES_HAT_GFV = p + 'hat_gfv'
# antenna can be hat, adafruit, puck or dummy
RD_DDH_GPS_NO_EXPIRES_ANTENNA = p + 'antenna_gps'
# too many GPS errors, we generate an alarm notification
RD_DDH_GPS_ERROR_NUMBER = p + 'error_number'



p = 'ddh:log:'
RD_DDH_LOG_QUEUE = p + 'queue'



p = 'ddh:cnv:'
RD_DDH_CNV_QUEUE = p + 'queue'



p = 'ddh:aws:'
RD_DDH_AWS_COPY_QUEUE = p + 'queue'
RD_DDH_AWS_NO_EXPIRES_SYNC_REQUEST = p + 'sync'
RD_DDH_AWS_NO_EXPIRES_PROCESS_STATE = p + 'process_state'
# counts the number of bad AWS interactions
RD_DDH_AWS_NO_EXPIRES_RV = p + 'rv'




p = 'ddh:net:'
RD_DDH_NET_PROCESS_OUTPUT = p + 'process_output'



p = 'ddh:slo:'
# for smart lock-out entries, followed by MAC addresses
RD_DDH_SLO_LS = p + 'ls:'
