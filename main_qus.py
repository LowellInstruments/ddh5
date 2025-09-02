from gps.gps_quectel import gps_hat_detect_list_of_usb_ports



def main_qus():
    ls = gps_hat_detect_list_of_usb_ports()
    if not ls:
        print(f'\nQUS -> port_GPS = "", port_CTL = ""')
        return
    port_nmea = ls[1]
    port_ctrl = ls[-2]
    print(f'\nQUS -> port_GPS {port_nmea}, port_CTL: {port_ctrl}')



if __name__ == '__main__':
    main_qus()
