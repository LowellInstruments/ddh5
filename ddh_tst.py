import redis
import time
import setproctitle
from ddh_log import lg_tst as lg
from utils.ddh_common import ddh_summarize_csv_file_for_history_table
from utils.redis import RD_DDH_BLE_ALL_LAST_OK_DL



# =================================================
# ddh_tst
# used to debug, test and develop faster
# =================================================



r = redis.Redis('localhost', port=6379)



def _tst_serve():

    print('tst')
    lg.a('tst2')



def _ddh_tst(ignore_gui):

    # forever loop serving local SQS files, do not hog CPU
    while 1:
        time.sleep(1)



def main_ddh_tst(ignore_gui=False):
    while 1:
        try:
            _ddh_tst(ignore_gui)
        except (Exception,) as ex:
            print(f'error, tst, nope {ex}')




if __name__ == '__main__':

    # normal run
    # main_ddh_tst(ignore_gui=False)
    # s = ddh_summarize_csv_file_for_history_table(
    #     '/home/kaz/PycharmProjects/ddh/dl_files/f0-5e-cd-25-a0-3d/2699991_BIX_20260819_133724_DissolvedOxygen.csv',
    #     data_out_water=True
    # )
    # print(s)


    mac = '11:22:33:44:55:66'
    k = RD_DDH_BLE_ALL_LAST_OK_DL
    s = r.get(k)
    s = s.decode() if s else ''
    v = f'{mac}_holaquetal'
    # add or update (remove existing one first)
    if s:
        ls = s.split('&')
        ls = [i for i in ls if mac not in i]
        ls.insert(0, f'{v}')
        v = '&'.join(ls)
    r.set(k, v)

    print('v =', v)
