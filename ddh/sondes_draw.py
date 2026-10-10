import os
import glob
from functools import lru_cache

import pandas as pd
import redis
import math
import time
from datetime import datetime
from PyQt6.QtCore import QCoreApplication, Qt
from math import ceil
import numpy as np
import pyqtgraph as pg
from pyqtgraph import LinearRegionItem
from pyqtgraph.Qt import QtGui

from ddh.graph_utils import (
    utils_graph_get_abs_fol_list,
    utils_graph_fetch_csv_data,
)
from utils.redis import (
    RD_DDH_GUI_PLOT_REASON_SONDES,
    RD_DDH_GUI_PLOT_FOLDER,
    RD_DDH_GUI_DISPLAY_BOX_GRAPH_STATISTICS
)
from utils.ddh_common import (
    calculate_path_to_folder_within_dl_files_from_mac_address,
    ddh_config_get_logger_mac_from_sn, linux_is_rpi,
    STR_ERROR_GRAPH_SN_NOT_IN_CONFIG, t_str,
    calculate_mac_address_from_folder_within_dl_files,
    ddh_config_get_logger_sn_from_mac, ddh_do_we_graph_out_of_water_data, ddh_get_path_to_folder_dl_files_sondes
)
from ddh_log import lg_gra as lg



# to be able to zoom in RPi
pg.setConfigOption('leftButtonPan', False)


# plot objects
pw_it = None
pw_vb = None



r = redis.Redis('localhost', port=6379)



class GraphException(Exception):
    pass



def _axis_room(v: list):
    return .1 * np.nanmax(v)



def _sty(color):
    return {"color": color, "font-size": "20px", "font-weight": "bold"}



def _graph_sondes_get_color_by_label(lbl):
    # google for SVG 1.0 color names
    # if 'Temperature' in lbl:
    #     return 'red'
    # if 'Pressure' in lbl:
    #     return 'blue'
    # if 'Depth' in lbl:
    #     return 'blue'
    # if 'DO Concentration' in lbl:
    #     return 'blue'
    # if 'Ax' in lbl:
    #     return 'limegreen'
    # if 'Conductivity' in lbl:
    #     return 'green'
    # if 'pH' in lbl:
    #     return 'green'
    return 'green'




class LimitsTypeError(Exception):
    def __init__(self, err='Limits type must be type int or tuple of ints', *args, **kwargs):
        super().__init__(self, err, *args, **kwargs)




class FiniteLinearRegionItem(LinearRegionItem):
    def __init__(self, limits=None, *args, **kwargs):
        super(FiniteLinearRegionItem, self).__init__(*args, **kwargs)
        """Create a new LinearRegionItem.

            Now you can define the shading area. Enjoy!

        ==============  =====================================================================
        **Arguments:**
        limits          A tuple containing the upper and lower bounds prependicular to the orientation.
                        Or a int/float containing the lower bounds prependicular to the orientation.
                        The default value is None.
        ==============  =====================================================================
        """
        self.limit = limits

    def boundingRect(self):
        br = self.viewRect()
        rng = self.getRegion()

        # Infinite with one end close
        if isinstance(self.limit, int):
            if self.orientation in ('vertical', LinearRegionItem.Vertical):
                br.setLeft(rng[0])
                br.setRight(rng[1])
                length = br.height()
                br.setBottom(self.limit)
                br.setTop(br.top() + length * self.span[0])
            else:
                br.setTop(rng[0])
                br.setBottom(rng[1])
                length = br.width()
                br.setRight(br.left() + length * self.span[1])
                br.setLeft(self.limit)
        # Finite
        elif isinstance(self.limit, tuple):
            if self.orientation in ('vertical', LinearRegionItem.Vertical):
                br.setLeft(rng[0])
                br.setRight(rng[1])
                length = br.height()
                br.setBottom(self.limit[0])
                br.setTop(self.limit[1])
            else:
                br.setTop(rng[0])
                br.setBottom(rng[1])
                length = br.width()
                br.setRight(self.limit[1])
                br.setLeft(self.limit[0])
        elif self.limit is None:
            if self.orientation in ('vertical', LinearRegionItem.Vertical):
                br.setLeft(rng[0])
                br.setRight(rng[1])
                length = br.height()
                br.setBottom(br.top() + length * self.span[1])
                br.setTop(br.top() + length * self.span[0])
            else:
                br.setTop(rng[0])
                br.setBottom(rng[1])
                length = br.width()
                br.setRight(br.left() + length * self.span[1])
                br.setLeft(br.left() + length * self.span[0])
        else:
            raise LimitsTypeError

        br = br.normalized()
        return br




def _graph_sondes_update_views():
    # used when resizing
    global pw_it, pw_vb
    # for the second line
    pw_vb.setGeometry(pw_it.vb.sceneBoundingRect())
    pw_vb.linkedViewChanged(pw_it.vb, pw_vb.XAxis)



def _graph_sondes_clear():
    global pw_it
    global pw_vb
    if pw_it:
        pw_it.getAxis('right').setVisible(False)
        pw_it.getAxis('left').setVisible(False)
        pw_it.getAxis('bottom').setVisible(False)
        pw_it.clear()
    if pw_vb:
        pw_vb.clear()



@lru_cache
def sonde_get_df_from_csv_files(filename_csv):
    df = pd.read_csv(filename_csv)
    metric = ''
    df_dot = None
    df_doc = None
    if 'RDO' in filename_csv:
        metric = 'RDO'
        # head = index   timestamp  serial_id  modbus_id  param       value  quality  units
        df_dot = df[df['units'] == 1]
        df_doc = df[df['units'] == 117]
        print(df_dot.head())
        print(df_doc.head())


    # build output dictionary to graph
    return {
        'metric': metric,
        'DOC': df_doc,
        'DOT': df_dot,
        'error': ''
    }



def _graph_sondes_process_n_draw(
        a):

    print('PLOTTING SONDE')

    # CLEAR graph LAYOUT of any plot widget
    for i in reversed(range(a.lay_g_h2_5.count())):
        a.lay_g_h2_5.itemAt(i).widget().setParent(None)



    # get graph from passed app
    pw = a.pw_sondes
    start_ts = time.perf_counter()




    # build the sonde file CSV to plot
    # who = a.cb_g_sondes_who.currentText()
    # if not who:
    #     e = 'error, no one asked for SONDES graph?'
    #     lg.a(e)
    #     raise GraphException(e)
    # fol = f'{ddh_get_path_to_folder_dl_files_sondes()}/{who}'
    # what = a.cb_g_sondes_what.currentText()
    # mask = f'{who}/{what}.csv'
    # ls = glob.glob(f'{fol}/{mask}')
    # if not ls:
    #     lg.a(f'note, no SONDE files for sonde {who} and metric {what}')
    #     raise GraphException(f'error, no SONDE files for sonde {who} and metric {what}')
    # lg.a(f'selected dropdown sonde {who}')



    # add the plot widget to the layout
    a.lay_g_h2_5.addWidget(pw)
    pw.setBackground('w')





    # ----------------------------------------
    # CLEAR graph and start from scratch
    # ----------------------------------------
    global pw_it
    global pw_vb
    if pw_it:
        pw_it.clear()
    if pw_vb:
        pw_vb.clear()
    pw_it = pw.plotItem



    # this prevents weird things in units when setting axis titles
    pw_it.getAxis('left').enableAutoSIPrefix(enable=False)
    pw_it.getAxis('left').autoSIPrefixScale = 1
    pw_it.getAxis('right').enableAutoSIPrefix(enable=False)
    pw_it.getAxis('right').autoSIPrefixScale = 1


    # patch for bottom ticks, x are floats meaning timestamps
    # solves the problem of the x-axis ticks changing
    # pw.setAxisItems({"bottom": pg.DateAxisItem()})

    # grid or not
    pw.showGrid(x=True, y=True)



    # ---------------------
    # 2nd line in the plot
    # ---------------------
    pw_vb = pg.ViewBox(enableMenu=True)
    pw_it.showAxis('right')
    pw_it.scene().addItem(pw_vb)
    pw_it.getAxis('right').linkToView(pw_vb)
    pw_vb.setXLink(pw_it)



    # connect thing when resizing
    _graph_sondes_update_views()
    pw_it.vb.sigResized.connect(_graph_sondes_update_views)


    # font: TICKS TEXT
    font = QtGui.QFont()
    font.setPixelSize(16)
    font.setBold(True)
    pw_it.getAxis("bottom").setStyle(tickFont=font)
    pw_it.getAxis("left").setStyle(tickFont=font)
    pw_it.getAxis("right").setStyle(tickFont=font)



    # ==========================
    # PROCESS folder's CSV data
    # ==========================
    csv_sonde_file = '/Users/kaz/PycharmProjects/ddh/dl_files_sondes/SENS_1_1_RDO.csv'
    data = sonde_get_df_from_csv_files(csv_sonde_file)
    bn = os.path.basename(csv_sonde_file)
    if not data:
        lg.a(f'warning, no SONDES data to plot in file {bn}')
        raise GraphException(f'no data to plot')
    if data['error']:
        e = data['error']
        lg.a(f'error, plotting SONDEs in file {bn} -> {e}')
        raise GraphException(f'plot error {e}')


    # x: time
    x_doc = list(data['DOC']['timestamp'])
    x_dot = list(data['DOT']['timestamp'])
    y_doc = list(data['DOC']['value'])
    y_dot = list(data['DOT']['value'])


    # time in ms -> time in seconds (I think)
    # todo: ask this
    x_doc = [i / 1000000 for i in x_doc]
    x_dot = [i / 1000000 for i in x_dot]



    # ----------
    # colors
    # ----------
    clr_0 = 'blue'
    clr_1 = 'red'
    pen0 = pg.mkPen(color=clr_0, width=2)
    pen1 = pg.mkPen(color=clr_1, width=2, style=Qt.PenStyle.DotLine)
    pw_it.getAxis('left').setTextPen(clr_0)
    pw_it.getAxis('right').setTextPen(clr_1)
    pw_it.getAxis('bottom').setTextPen('black')

    # avoids small glitch when re-zooming
    pw.getPlotItem().enableAutoRange()



    # -------------------
    # graph DOX loggers
    # -------------------
    if data['metric'] == 'RDO':
        # draw DO (y1) and T (y2) lines
        pw_it.setLabel("left", 'mg/l', **_sty(clr_0))
        pw_it.getAxis('right').setLabel('celsius', **_sty(clr_1))
        pw_it.plot(x_doc, y_doc, pen=pen0, hoverable=True)
        pw_vb.addItem(pg.PlotCurveItem(x_dot, y_dot, pen=pen1, hoverable=True, connect='finite'))

        # dynamic upper top of DOX graphs
        upper_top_do = 10
        if np.nanmax(y_dot) > upper_top_do:
            upper_top_do = np.nanmax(y_dot) + 1
        upper_top_do = int(ceil(upper_top_do))


        # y-axis DOX ranges, bottom-axis label
        pw_it.setYRange(0, upper_top_do, padding=0)
        pw_vb.setYRange(np.nanmin(y_dot), np.nanmax(y_dot), padding=0)
        pw_it.getAxis('bottom').setLabel('my title', **_sty('black'))

        # alpha, for zones, the lower, the more transparent
        alpha = 85
        pw.addItem(FiniteLinearRegionItem(values=(0, 2),
                                         limits=4,
                                         orientation="horizontal",
                                         brush=(255, 0, 0, alpha),
                                         movable=False))
        pw.addItem(FiniteLinearRegionItem(values=(2, 4),
                                         limits=4,
                                         orientation="horizontal",
                                         brush=(255, 170, 6, alpha),
                                         movable=False))
        pw.addItem(FiniteLinearRegionItem(values=(4, 6),
                                         limits=4,
                                         orientation="horizontal",
                                         brush=(255, 255, 66, alpha),
                                         movable=False))
        pw.addItem(FiniteLinearRegionItem(values=(6, upper_top_do),
                                         limits=4,
                                         orientation="horizontal",
                                         brush=(176, 255, 66, alpha),
                                         movable=False))

    # if met == 'PH':
    #     a.cb_g_switch_tp.setVisible(False)
    #
    #     # draw pH (y1) and T (y2) lines
    #     pw_it.setLabel("left", lbl1, **_sty(clr_1))
    #     pw_it.getAxis('right').setLabel(lbl2, **_sty(clr_2))
    #     pw_it.plot(x, y1, pen=pen1, hoverable=True)
    #     pw_vb.addItem(pg.PlotCurveItem(x, y2, pen=pen2, hoverable=True, connect='finite'))
    #
    #     # dynamic upper top of PH graphs
    #     upper_top_ph = 12
    #
    #     # y-axis DOX ranges, bottom-axis label
    #     pw_it.setYRange(0, upper_top_ph, padding=0)
    #     pw_vb.setYRange(np.nanmin(y2), np.nanmax(y2), padding=0)
    #     pw_it.getAxis('bottom').setLabel(title, **_sty('black'))


    # statistics: benchmark and number of points
    end_ts = time.perf_counter()
    el_ts = int((end_ts - start_ts) * 1000)
    lg.a(f"took {el_ts} ms to DISPLAY {len(data)} {data['metric']} data points")





def sondes_graph_process_n_draw(
        app,
        plot_reason=''):
    try:
        app.lbl_graph_err_sondes.setVisible(False)
        app.lbl_graph_busy_sondes.setVisible(True)
        QCoreApplication.processEvents()
        _graph_sondes_process_n_draw(app)
        # remove any past error
        app.pw_sondes.setTitle('')


    except GraphException as e:
        # errors such as "no data files to graph"
        lg.a(f"graph_exception -> {str(e)}")
        app.lbl_graph_err_sondes.setText(str(e))
        app.lbl_graph_err_sondes.setVisible(True)
        app.pw_sondes.getAxis('bottom').setLabel("")
        _graph_sondes_clear()


    except (Exception,) as ex:
        # not GraphException, but python errors such as IndexError
        lg.a(f"graph_generic_exception -> {str(ex)}")
        app.lbl_graph_err_sondes.setText('error graph_generic, see log')
        app.lbl_graph_err_sondes.setVisible(True)
        app.pw_sondes.getAxis('bottom').setLabel("")
        _graph_sondes_clear()

    finally:
        app.lbl_graph_busy.setVisible(False)



def sondes_graph_request(reason='user'):
    lg.a(f"note, requesting PLOT_SONDES to GUI with reason = {reason}")
    r.set(RD_DDH_GUI_PLOT_REASON_SONDES, reason)
