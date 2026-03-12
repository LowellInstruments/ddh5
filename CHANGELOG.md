# Changelog


5.0.01  10/22/25

    first spin of new version, based on multiprocesses and redis

5.0.02  10/23/25

    fixed timer sending alive notifications too often

5.0.03  10/24/25

    fixed bug not deleting history
    fixed bug not deleting dl_files

5.0.04  11/03/25

    refactor to understand processes output

5.0.05  11/06/25

    improved smart lock-out with katrina

5.0.06  11/10/25

    getting rid of ble.py

5.0.07  01/28/26

    plots: added units toggle metric / imperial
    plots: added bottom temperature

5.0.08  02/01/26

    now GUI detects running redis
    now GUI detects running power shield

5.0.09  02/08/26

    removed expandable left section

5.0.10  02/10/26

    maps tab: proof-of-concept

5.0.11  02/11/26

    fixed GUI alignment

5.0.12  02/11/26

    fixed GUI alignment
    redis constants names refactor
    added comments here and there

5.0.13  02/18/26

    fixed summary box units

5.0.14  02/20/26

    integrated GPS hat power-cycle in ddh_gps.py

5.0.15  03/03/26

    removed the double frame in statistics summary box

5.0.16  03/03/26

    summary statistics box appears and disappears

5.0.17  03/06/26

    added portuguese translation
    added spanish translation
    to set it, config.toml 
    [behavior] 
    language = 0 -> English
    language = 1 -> Portuguese
    language = 2 -> Spanish

5.0.18  03/09/26

    DDC fixed /boot/issues and cell firmware to detect 2025

5.0.19  03/09/26

    started testing API
    bumped API version to 2.0.0
    API -> fixed GPS interface names, alive DDH processes names

5.0.20  03/10/26

    changed frequency of low-satellites notification


5.0.21  03/12/26

    option to disable smart lock-out by config.toml [experimenta] skip_slo = 1
    option to disable color macs by config.toml [experimental] override_ft = 1
