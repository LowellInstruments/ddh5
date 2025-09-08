#!/usr/bin/env bash
source /home/pi/li/ddh/scripts/utils.sh



echo
clear
_pb "=============="
_pb " DDH - init"
_pb "=============="
echo



# check we need a reboot
if [ -f "$LI_DDH_NEEDS_REBOOT_POST_INSTALL" ]; then
    _pr "DDH was just installed, please reboot"
    exit 0
fi



_pb "    RFKILL - unblock and wlan"
sudo rfkill unblock bluetooth
sudo rfkill unblock wlan



_pb "    SYSTEMCTL - restarting bluetooth service"
sudo systemctl restart bluetooth
sleep 2



_pb "    CACHE - disable from /etc/bluetooth/main.conf"
sudo sed -i '/#Cache = always/c\Cache = no' /etc/bluetooth/main.conf
LS_HCI_MACS=$(hciconfig -a | grep "BD Address" | cut -d " " -f 3)
for HM in $LS_HCI_MACS; do
  sudo rm "/var/lib/bluetooth/$HM"/cache/* 2> /dev/null
done



_pb "    HCICONFIG - reset BLE HCI interfaces"
sudo hciconfig hci0 reset 2> /dev/null ||  _py "    cannot reset hci0"
sudo hciconfig hci0 up 2> /dev/null ||     _py "    cannot UP hci0"
sudo hciconfig hci1 reset 2> /dev/null ||  _py "    cannot reset hci1"
sudo hciconfig hci1 up 2> /dev/null ||     _py "    cannot UP hci1"
(hciconfig hci0 | grep RUNNING) &> /dev/null; rv0=$?
(hciconfig hci1 | grep RUNNING) &> /dev/null; rv1=$?
if [ $rv0 -eq 0 ]; then
  _pg "    hci0 is up"
fi
if [ $rv1 -eq 0 ]; then
  _pg "    hci1 is up"
fi
if [ $rv0 -ne 0 ] && [ $rv1 -ne 0 ]; then
    _pr "error: needs at least 1 Bluetooth interface"
    exit 1
fi



_pb "    KERNEL - set BLE connection supervision timeout"
echo '200' | sudo tee /sys/kernel/debug/bluetooth/hci0/supervision_timeout 2> /dev/null
echo '200' | sudo tee /sys/kernel/debug/bluetooth/hci1/supervision_timeout 2> /dev/null



_pb "    DDH - set permissions on linux binaries 'date' and 'ifmetric'"
sudo setcap CAP_SYS_TIME+ep /bin/date
sudo setcap 'cap_net_raw,cap_net_admin+eip' /usr/sbin/ifmetric



_pb "    DDH - run main_qus.py to auto-detect Quectel USB ports"
cd "$FOL_DDH" && "$FOL_VEN"/bin/python main_qus.py
QUC=$(cat /tmp/usb_quectel_ctl)
if [ "${QUC}" ]; then
    if [ ! -s "$LI_FILE_ICCID" ]; then
        # the file is zero
        rm "$LI_FILE_ICCID" > /dev/null 2>&1
    fi
    if [ ! -f "$LI_FILE_ICCID" ]; then
        # the file does not exist
        for idx_iccid in {1..5}
        do
            _pb "    DDH - query Quectel SIM ID on $QUC, attempt #$idx_iccid"
            echo -ne "AT+QCCID\r" > "$QUC"
            sleep 0.1
            timeout 1 cat -v < "$QUC" | grep QCCID > "$LI_FILE_ICCID"
            if [ -s "$LI_FILE_ICCID" ]; then
                # there is definitely something in the file :)
                break
            fi
        done
    fi
fi



_pb "    DDH - set XAUTHORITY, DISPLAY linux environment variables"
export XAUTHORITY=/home/pi/.Xauthority
export DISPLAY=:0



echo && echo
_pb "==============="
_pb "DDH - run GUI"
_pb "==============="


echo
sudo chown -R pi:pi "$FOL_LI"
source "$FOL_VEN"/bin/activate
cd "$FOL_DDH" && "$FOL_VEN"/bin/python main_ddh.py
