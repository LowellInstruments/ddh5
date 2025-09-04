from gps.gps_quectel import gps_hat_detect_list_of_usb_ports



def main_qus():
    ls = gps_hat_detect_list_of_usb_ports()
    port_ctrl = ""
    if not ls:
        print(f'\nwarning: QUS -> port_GPS = "", port_CTL = ""')
    else:
        port_nmea = ls[1]
        port_ctrl = ls[-2]
        # print(f'\nQUS -> port_GPS {port_nmea}, port_CTL: {port_ctrl}')
    with open("/tmp/usb_quectel_ctl", 'w') as f:
        f.write(port_ctrl)



if __name__ == '__main__':
    main_qus()
