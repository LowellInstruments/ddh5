import pathlib
from parser_gui import Parser, Parser_GUI_Tk




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
    pr = Parser()
    fol_dst = f'{h}/Downloads/temp'

    # fn_dat = f'{h}/Downloads/20260415_100954/D2/AC2_58.dat'
    # use_int = True
    # rv = pr.parse_ac_file(fn_dat, use_int=use_int, export=True, output_dir=fol_dst)
    # print('rv_ac = ', rv)

    fn_dat = f'{h}/Downloads/SENS_32_25.dat'
    parsed = {fn_dat: pr.parse_sense_file(fn_dat)}
    Parser_GUI_Tk.save_csv_callback(parsed, output_dir=fol_dst)


    # p = f'{h}/Downloads/SENS_32_25_gps.csv'
    # ut = get_start_unix_time_from_gps_file(p)
    # print('started at unix_secs', ut)




if __name__ == '__main__':
    main()
