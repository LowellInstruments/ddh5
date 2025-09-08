#!/usr/bin/env bash
source /home/pi/li/ddh/scripts/utils.sh


clear
echo


source "$FOL_VEN"/bin/activate
cd "$FOL_DDH" && "$FOL_VEN"/bin/python main_ddc.py
