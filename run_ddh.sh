#!/usr/bin/env bash



source /home/pi/li/ddh/scripts/utils.sh



clear


# for crontab to detect already running
check_already_running "ddh_main"



echo



# check we need a reboot
if [ -f "$LI_DDH_NEEDS_REBOOT_POST_INSTALL" ]; then
    _pr "DDH was just installed, please reboot"
    exit 0
fi



_pb "==============="
_pb " Deck Data Hub"
_pb "==============="
echo


_pb " LINUX - rfkill + bluetooth services, cache and interfaces"
sudo rfkill unblock bluetooth
sudo rfkill unblock wlan
sudo systemctl restart bluetooth
systemctl --user stop wireplumber
sudo sed -i '/#Cache = always/c\Cache = no' /etc/bluetooth/main.conf
LS_HCI_MACS=$(hciconfig -a | grep "BD Address" | cut -d " " -f 3)
for HM in $LS_HCI_MACS; do
  sudo rm "/var/lib/bluetooth/$HM"/cache/* 2> /dev/null
done
sleep 1



#_pb "    HCICONFIG - reset BLE HCI interfaces"
sudo hciconfig hci0 reset 2> /dev/null ||  _py "    cannot reset hci0"
sudo hciconfig hci0 up 2> /dev/null ||     _py "    cannot UP hci0"
sudo hciconfig hci1 reset 2> /dev/null ||  _py "    cannot reset hci1"
sudo hciconfig hci1 up 2> /dev/null ||     _py "    cannot UP hci1"
(hciconfig hci0 | grep RUNNING) &> /dev/null; rv0=$?
(hciconfig hci1 | grep RUNNING) &> /dev/null; rv1=$?
#if [ $rv0 -eq 0 ]; then
#  _pg "    hci0 is up"
#fi
#if [ $rv1 -eq 0 ]; then
#  _pg "    hci1 is up"
#fi
if [ $rv0 -ne 0 ] && [ $rv1 -ne 0 ]; then
    _pr "error: needs at least 1 Bluetooth interface"
    exit 1
fi

# _pb "    KERNEL - set BLE connection supervision timeout"
# this is in units of 10 ms
echo '300' | sudo tee /sys/kernel/debug/bluetooth/hci0/supervision_timeout 2> /dev/null
echo '300' | sudo tee /sys/kernel/debug/bluetooth/hci1/supervision_timeout 2> /dev/null



_pb " LINUX - permissions 'date' and 'ifmetric' + auto-detect USB ports"
sudo setcap CAP_SYS_TIME+ep /bin/date
sudo setcap 'cap_net_raw,cap_net_admin+eip' /usr/sbin/ifmetric
cd "$FOL_DDH" && "$FOL_VEN"/bin/python main_qus.py



_pb " DDH - sim card file"
QUC=$(cat /tmp/usb_quectel_ctl)
if [ "${QUC}" ]; then
    # the file size is zero
    if [ ! -s "$LI_FILE_ICCID" ]; then
          _py " DDH - sim card file removed because size = 0"
          rm "$LI_FILE_ICCID" > /dev/null 2>&1
    fi
    WC_ID=$(wc -c < "$LI_FILE_ICCID")
    RV=$?
    if [[ $RV -ne 0 || $WC_ID -ne 31 ]]; then
        # the file size is NOT Ok
        for idx_iccid in {1..10}
        do
            _py " DDH - sim card query #$idx_iccid on $QUC"
            echo -ne "AT+QCCID\r" > "$QUC"
            sleep 0.1
            timeout 1 cat -v < "$QUC" | grep QCCID > "$LI_FILE_ICCID"
            WC_ID=$(wc -c < "$LI_FILE_ICCID")
            RV=$?
            if [[ $RV -eq 0 && $WC_ID -eq 31 ]]; then
                break
            fi
        done
    else
        _pb " DDH - sim card file seems OK from the start"
    fi
fi
WC_ID=$(wc -c < "$LI_FILE_ICCID")
RV=$?
if [[ $RV -ne 0 || $WC_ID -ne 31 ]]; then
    _py " DDH - sim card file NOT OK"
fi



#_pb "    DDH - set XAUTHORITY, DISPLAY linux environment variables"
_pb " DDH - running GUI"
export XAUTHORITY=/home/pi/.Xauthority
export DISPLAY=:0



echo && echo



echo
sudo chown -R pi:pi "$FOL_LI"
source "$FOL_VEN"/bin/activate
cd "$FOL_DDH" && "$FOL_VEN"/bin/python main_ddh.py
