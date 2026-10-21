import pathlib



h = pathlib.Path.home()



def get_start_unix_time_from_gps_file(fn_gps) -> float:
    with open(fn_gps, 'r') as f:
        ll = f.readlines()
    start_unix_secs = 0
    for i, s in enumerate(ll[1:]):
        try:
            s = s.split(',')
            unix_ts = float(s[-1].replace('\n', ''))
            ts_ten_ns = int(s[1])
            ts_secs = ts_ten_ns * 10 / 1e9
            start_unix_secs = unix_ts - ts_secs
            break
        except (Exception, ) as e:
            pass
    if start_unix_secs == 0:
        print('error, cannot find unix time in file')
    return start_unix_secs




def main():
    # p = f'{h}/Downloads/SENS_32_25_gps.csv'
    p = '/Users/kaz/PycharmProjects/ddh/dl_files_sondes/sonde1_SENS_32_25_gps.csv'
    ut = get_start_unix_time_from_gps_file(p)
    print('started at unix_secs', ut)




if __name__ == '__main__':
    main()
