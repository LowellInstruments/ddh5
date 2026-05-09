from gps.gps_quectel import gps_hat_detect_list_of_usb_ports



PATH_FILE_PORT_CTRL = '/tmp/usb_quectel_ctl'



def main_qus():
    ls = gps_hat_detect_list_of_usb_ports()
    if not ls:
        print(f'\nwarning, QUS did NOT find USB ports')
        return

    port_nmea = ls[1]
    port_ctrl = ls[-2]
    # print(f'\nQUS -> NMEA: {port_nmea}, CTRL: {port_ctrl}')
    with open(PATH_FILE_PORT_CTRL, 'w') as f:
        f.write(port_ctrl)



if __name__ == '__main__':
    main_qus()
