import time
import setproctitle
from ddh_log import lg_tst as lg
from utils.ddh_common import ddh_summarize_csv_file_for_history_table

# =================================================
# ddh_tst
# used to debug, test and develop faster
# =================================================



p_name = 'TST'



def _tst_serve():

    print('tst')
    lg.a('tst2')



def _ddh_tst(ignore_gui):

    # prepare TST process
    setproctitle.setproctitle(p_name)


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
    s = ddh_summarize_csv_file_for_history_table(
        '/home/kaz/PycharmProjects/ddh/dl_files/f0-5e-cd-25-a0-3d/2699991_BIX_20260819_133724_DissolvedOxygen.csv',
        data_out_water=True
    )
    print(s)
