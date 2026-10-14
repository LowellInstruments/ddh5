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




@lru_cache
def _cache_read_csv(filename_csv):
    return pd.read_csv(filename_csv)



def sonde_get_df_from_csv_files(filename_csv, data):
    df = _cache_read_csv(filename_csv)
    bn = os.path.basename(filename_csv)
    if 'PTS_Bar30' in bn:
        data['df_pts_30'] = df
        data['ls_metrics'].append('PTS_Bar30')
    if 'RDO' in bn:
        data['df_dot'] = df[df['units'] == 1]
        data['df_doc'] = df[df['units'] == 117]
        data['ls_metrics'].append('RDO')
    if 'ATLAS' in bn:
        # C (0) / pH (1) / DO (2) / T (4)
        data['df_ph'] = df[df['sensor_type'] == 1]
        data['ls_metrics'].append('ph')



def sondes_graph_request(reason='user'):
    lg.a(f"note, requesting PLOT_SONDES to GUI with reason = {reason}")
    r.set(RD_DDH_GUI_PLOT_REASON_SONDES, reason)




def plot_sondes(app):

    # build the dataframe
    data = dict()
    data['ls_metrics'] = []
    # todo: grab WHEN from GUI dropdown and WHO too
    who = app.cb_g_sondes_who.currentText() or 'sonde1'
    when = app.cb_g_sondes_when.currentText() or '1_1'
    fol = ddh_get_path_to_folder_dl_files_sondes()
    ls_do = [i for i in glob.glob(f'{fol}/{who}_SENS_{when}_RDO.csv')]
    if ls_do:
        p = ls_do[0]
        sonde_get_df_from_csv_files(p, data)
    ls_pts = [i for i in glob.glob(f'{fol}/{who}_SENS_{when}_External_PTS_Bar30.csv')]
    if ls_pts:
        p = ls_pts[0]
        sonde_get_df_from_csv_files(p, data)
    ls_cond = [i for i in glob.glob(f'{fol}/{who}_SENS_{when}_ATLAS.csv')]
    if ls_cond:
        p = ls_cond[0]
        sonde_get_df_from_csv_files(p, data)



    # get plot layout, create MAIN plot item and main view_box
    p_l = pg.GraphicsLayout()
    pw = app.pw_sondes
    pw.setCentralWidget(p_l)
    p1 = pw.plotItem
    # row is 2 because 0 and 1 are plot labels
    # column is 1 because 0 is left-axis label
    p_l.addItem(p1, row=2, col=1, rowspan=1, colspan=1)
    vb_l1 = p1.vb



    # create additional y-axis and view_boxes
    ax_r1 = pg.AxisItem("right")
    ax_r2 = pg.AxisItem("right")
    ax_r3 = pg.AxisItem("right")
    vb_r1 = pg.ViewBox()
    vb_r2 = pg.ViewBox()
    vb_r3 = pg.ViewBox()
    # add view_boxes to layout
    p_l.scene().addItem(vb_r1)
    p_l.scene().addItem(vb_r2)
    p_l.scene().addItem(vb_r3)
    # link y-axis to view_boxes
    ax_r1.linkToView(vb_r1)
    ax_r2.linkToView(vb_r2)
    ax_r3.linkToView(vb_r3)
    # link x-axis of all of them
    vb_r1.setXLink(vb_l1)
    vb_r2.setXLink(vb_l1)
    vb_r3.setXLink(vb_l1)


    # re-plot
    def update_views():
        vb_r1.setGeometry(vb_l1.sceneBoundingRect())
        vb_r1.linkedViewChanged(p1.vb, vb_l1.XAxis)
        vb_r2.setGeometry(vb_l1.sceneBoundingRect())
        vb_r2.linkedViewChanged(p1.vb, vb_l1.XAxis)
        vb_r3.setGeometry(vb_l1.sceneBoundingRect())
        vb_r3.linkedViewChanged(p1.vb, vb_l1.XAxis)
    vb_l1.sigResized.connect(update_views)
    update_views()


    # create legend
    legend = pw.addLegend(
        pen=pg.mkPen('black', width=2),
        labelTextSize='12pt',
        brush=(240, 240, 255, 150),
        # distance from right, top
        offset=(-10, -200)
    )


    # TEMPERATURE expected to always be there get the sub_dataframes and plot
    d = data['df_pts_30'].reset_index(drop=True)
    p1.plot(
        list(d['timestamp']),
        list(d['temperature_c']),
        symbol='o', pen=None, size=1, symbolPen='red',
        symbolSize=5, symbolBrush='red',
        name='Temperature (C)'
    )
    p1.getAxis("left").setLabel('Temperature (C)', color='red')




    # # PRESSURE expected to always be there get the sub_dataframes and plot
    #         list(d['timestamp']),
    #         list(d['pressure_bar']),
    #         symbol='o', pen=None, size=1, symbolPen='blue',
    #         symbolSize=5, symbolBrush='blue', name='Pressure (bar)'
    #     )
    #     p1.getAxis("right").setLabel('Pressure (bar)', color='blue')


    # axes labels RIGHT, first label
    p1.showAxis('right')
    if 'PTS_Bar30' in data['ls_metrics']:
        d = data['df_pts_30'].reset_index(drop=True)
        p_di = pg.PlotDataItem(
            list(d['timestamp']),
            list(d['pressure_bar']),
            symbol='o', pen=None, size=1, symbolPen='blue',
            symbolSize=5, symbolBrush='blue', name='Pressure (bar)'
        )
        vb_r1.addItem(p_di)
        legend.addItem(p_di, name='Pressure (bar)')
        p1.getAxis('right').linkToView(vb_r1)
        p1.getAxis("right").setLabel('Pressure (bar)', color='blue')


    if 'RDO' in data['ls_metrics']:
        # green pistaccio
        color = '#a3c41b'
        d = data['df_doc'].reset_index(drop=True)
        p_di = pg.PlotDataItem(
            list(d['timestamp']),
            list(d['value']),
            symbol='o', pen=None, size=1, symbolPen=color,
            symbolSize=5, symbolBrush=color, name='DOC (mg/l)'
        )
        vb_r2.addItem(p_di)
        legend.addItem(p_di, name='DOC (mg/l)')
        ax_r2.linkToView(vb_r2)
        ax_r2.setLabel('DOC (mg/l)', color=color)
        # row 2, column 4
        p1.layout.addItem(ax_r2, 2, 4)


    if 'ph' in data['ls_metrics']:
        color = '#f1b929'
        d = data['df_ph'].reset_index(drop=True)
        p_di = pg.PlotDataItem(
            list(d['timestamp']),
            list(d['sensor_val']),
            symbol='o', pen=None, size=1, symbolPen=color,
            symbolSize=5, symbolBrush=color, name='pH'
        )
        vb_r3.addItem(p_di)
        legend.addItem(p_di, name='pH')
        ax_r3.linkToView(vb_r3)
        ax_r3.setLabel('pH', color=color)
        # row 2, column 5
        p1.layout.addItem(ax_r3, 2, 5)






def sondes_serve_graph_request(
        app,
        plot_reason=''):
    try:
        app.lbl_graph_err_sondes.setVisible(False)
        app.lbl_graph_busy_sondes.setVisible(True)
        QCoreApplication.processEvents()
        app.pw_sondes = pg.PlotWidget(axisItems={'bottom': pg.DateAxisItem()})
        app.pw_sondes.setBackground('w')
        if app.lay_g_h2_5.count() == 0:
            app.lay_g_h2_5.addWidget(app.pw_sondes)
        plot_sondes(app)


    except GraphException as e:
        # errors such as "no data files to graph"
        lg.a(f"graph_exception -> {str(e)}")
        app.lbl_graph_err_sondes.setText(str(e))
        app.lbl_graph_err_sondes.setVisible(True)


    except (Exception,) as ex:
        # not GraphException, but python errors such as IndexError
        lg.a(f"graph_generic_exception -> {str(ex)}")
        app.lbl_graph_err_sondes.setText('error graph_generic, see log')
        app.lbl_graph_err_sondes.setVisible(True)

    finally:
        app.lbl_graph_busy_sondes.setVisible(False)




