import datetime
import os


def main(p):
    bn = os.path.basename(p)
    ts = datetime.datetime.now().strftime('%Y%m%d')
    path_out_sl = f'/tmp/sl_aws_{ts}.log'
    with open(path_out_sl, 'a') as f_out_sl:
        f_out_sl.write(f'{bn},{os.path.getsize(p)}\n')



if __name__ == '__main__':
    main('/home/kaz/PycharmProjects/bix/main_bix.py')
