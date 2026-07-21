# Changelog


5.0.01      10/22/25

    first spin of new version, based on multiprocesses and redis

5.0.02      10/23/25

    fixed timer sending alive notifications too often

5.0.03      10/24/25

    fixed bug not deleting history
    fixed bug not deleting dl_files

5.0.04      11/03/25

    refactor to understand processes output

5.0.05      11/06/25

    improved smart lock-out with katrina

5.0.06      11/10/25

    getting rid of ble.py

5.0.07      01/28/26

    plots: added units toggle metric / imperial
    plots: added bottom temperature

5.0.08      02/01/26

    now GUI detects running redis
    now GUI detects running power shield

5.0.09      02/08/26

    removed expandable left section

5.0.10      02/10/26

    maps tab: proof-of-concept

5.0.11      02/11/26

    fixed GUI alignment

5.0.12      02/11/26

    fixed GUI alignment
    redis constants names refactor
    added comments here and there

5.0.13      02/18/26

    fixed summary box units

5.0.14      02/20/26

    integrated GPS hat power-cycle in ddh_gps.py

5.0.15      03/03/26

    removed the double frame in statistics summary box

5.0.16      03/03/26

    summary statistics box appears and disappears

5.0.17      03/06/26

    added portuguese translation
    added spanish translation
    to set it, config.toml 
    [behavior] 
    language = 0 -> English
    language = 1 -> Portuguese
    language = 2 -> Spanish

5.0.18      03/09/26

    DDC fixed /boot/issues and cell firmware to detect 2025

5.0.19      03/09/26

    started testing API
    bumped API version to 2.0.0
    API -> fixed GPS interface names, alive DDH processes names

5.0.20      03/10/26

    changed frequency of low-satellites notification


5.0.2       03/12/26

    option to disable smart lock-out by config.toml [experimenta] skip_slo = 1
    option to disable color macs by config.toml [experimental] override_ft = 1

5.0.22      03/17/26

    added DDH power hat icon

5.0.23      03/20/26

    fixed file for BLE download progress bars


5.0.24      03/25/26

    slightly faster TDO downloads with full_query mechanism

5.0.25      04/08/26

    whe    GPS is dummy, don't power-cycle GPS sixfab hat

5.0.26      04/09/26

    GUI, removed 2 one-second timers
    GUI, removed minimize conflictive button
    GUI, made maps only download every day instead of every hour

5.0.27      04/14/26

    GUI, added a celsius monitor for CPU in raspberry

5.0.28      04/16/26

    GPS test in main_ddc now updates slower, every 6 seconds instead of 3

5.0.29      04/27/26

    we do again cell firmware shield being written to /li/.fw_cell_ver

5.0.30      05/04/26

    label cell/wifi in left column fixed

5.0.31      05/04/26

    better get_hat_cell_firmware_version and DDC report on cell fw year

5.0.32      05/05/26

    display summary of experimental features
    GPS automatic port selection works better

5.0.33      05/06/26

    added redis key "ddh:ble:last_ok_dl_for_mac_"

5.0.34      05/09/26

    added port re-enumeration on ddh_gps.py after some hat errors

5.0.35      05/11/26

    added caching on webview

5.0.36      05/11/26

    use global-land-mask

5.0.37      05/12/26

    simpler GPS
    minimize button is back

5.0.38      05/12/26

    fixes touch screen bug shift after minimizing

5.0.39      05/16/26

    caching for GPS positions in land in file in_ports_geo.py

5.0.40      05/18/26

    indicate to a file-system flag the GUI has GPS error
    be able to close advanced tab

5.0.41      05/19/26

    fixed graph error messages

5.0.42      05/20/26

    fixed scott bug in plots autoSIPrefixScale = 1

5.0.43      05/21/26

    less AWS logs
    plot reason BLE converted to user reason --> better auto-plotting upon download

5.0.44      05/27/26

    improved ddh_ble.py function _ble_logger_is_do1_or_do2()

5.0.45      05/28/26

    support for DO-1 is in BETA

5.0.46      06/04/26

    not critical, clearer logs and keys() redis calls removed

5.0.47      06/12/26

    relaxed requirements for has-been-in-water

5.0.48      06/15/26

    smart lock-out deletes expired keys upon boot

5.0.49      06/15/26

    added atcom timer but disabled

5.0.50      07/02/26

    enabled atcom timer
    better ICCID on run_ddh.sh

5.0.51      07/02/26

    diabled atcom timer because BUG

5.0.52      07/13/25

    added ddh_ble.py ) or info.startswith("DO-")

5.0.53      07/21/25

    less demanding ddh_net constants


