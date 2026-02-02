import threading
import time
from signal import pause
from utils.redis import (
    RD_DDH_GUI_BOX_SIDE_BUTTON_TOP,
    RD_DDH_GUI_BOX_SIDE_BUTTON_MID,
    RD_DDH_GUI_BOX_SIDE_BUTTON_LOW
)
from utils.ddh_common import (
    exp_get_custom_side_buttons_debounce_time, linux_is_rpi,
)
import redis



r = redis.Redis('localhost')
TIME_DB_S = .001
TIME_LO_S = .5
g_last_t = 0
MS_100 = (1 / 10)
MS_10 = (1 / 100)
MS_1 = (1 / 1000)
PIN_BTN_1 = 16
PIN_BTN_2 = 20
PIN_BTN_3 = 21



def _th_gpio_box_buttons():

    from gpiozero import Button

    # custom debounce time
    cdt = exp_get_custom_side_buttons_debounce_time()
    if cdt == 1:
        cdt = .1
    elif cdt == 2:
        cdt = .01
    else:
        cdt = .001

    print(f'new buttons thread using cdt = {cdt}')
    b1 = Button(PIN_BTN_1, pull_up=True, bounce_time=cdt)
    b2 = Button(PIN_BTN_2, pull_up=True, bounce_time=cdt)
    b3 = Button(PIN_BTN_3, pull_up=True, bounce_time=cdt)

    def b1_cb_v1():
        time.sleep(MS_10)
        if b1.is_pressed:
            r.set(RD_DDH_GUI_BOX_SIDE_BUTTON_TOP,1)


    def b2_cb_v1():
        time.sleep(MS_10)
        if b2.is_pressed:
            r.set(RD_DDH_GUI_BOX_SIDE_BUTTON_MID,1)


    def b3_cb_v1():
        for i in range(50):
            # half second
            time.sleep(MS_10)
            if not b3.is_pressed:
                return
        r.set(RD_DDH_GUI_BOX_SIDE_BUTTON_LOW, 1)


    b1.when_pressed = b1_cb_v1
    b2.when_pressed = b2_cb_v1
    b3.when_pressed = b3_cb_v1

    pause()




def ddh_create_thread_buttons():
    if not linux_is_rpi():
        return
    print(f'GUI: creating buttons thread')
    bth = threading.Thread(target=_th_gpio_box_buttons)
    bth.start()
