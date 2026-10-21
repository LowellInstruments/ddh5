import os
import glob
from functools import lru_cache

import pandas as pd
import redis
from PyQt6.QtCore import QCoreApplication, Qt
import pyqtgraph as pg
from utils.redis import (
    RD_DDH_GUI_PLOT_REASON_SONDES,
)
from utils.ddh_common import (
    ddh_get_path_local_folder_dl_files_sondes
)
from ddh_log import lg_gra as lg




# to be able to zoom in RPi
pg.setConfigOption('leftButtonPan', False)
# so pandas dataframes don't show scientific notation
pd.set_option('display.float_format', lambda x: '%.5f' % x)




# plot objects
pw_it = None
pw_vb = None



r = redis.Redis('localhost', port=6379)



class GraphException(Exception):
    pass



@lru_cache
def _cache_read_csv(filename_csv):
    return pd.read_csv(filename_csv)



def _get_df_from_csv_files(p_csv, data):

    # filename_csv: /Users/...dl_files_sondes/sonde1_SENS_1_1_ATLAS.csv
    df = _cache_read_csv(p_csv)


    # read file li_gps.csv containing GPS timestamp to be added to data
    when = '_'.join(p_csv.split('_SENS_')[1].split('_')[0:2])
    who = p_csv.split('_SENS_')[0].split('/')[-1]
    mask_gps_li = f'{who}*{when}_gps_li.csv'
    ls = glob.glob(f'{os.path.dirname(p_csv)}/{mask_gps_li}')
    if not ls:
        raise FileNotFoundError(f'error, cannot find GPS file {mask_gps_li}')
    with open(ls[0], 'r') as f:
        start_gps_ts = float(f.readline())

    # timestamp in SENS.dat files is in tens of ns
    df['timestamp_adjusted'] = (df['timestamp'] * 1e-8) + start_gps_ts



    # build DICTIONARY of data
    bn = os.path.basename(p_csv)
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
        df_cond = df[df['sensor_type'] == 0]
        # email: conductivity to salinity in PSU = multiply by 0.54/1000
        df_cond = df_cond * (.54/1000)
        data['df_cond'] = df_cond





def sondes_graph_request(reason='user'):
    lg.a(f"note, requesting PLOT_SONDES to GUI with reason = {reason}")
    r.set(RD_DDH_GUI_PLOT_REASON_SONDES, reason)





def _sondes_plot(app):

    if app.lay_g_h2_5.count() > 0:
        # amazing way to remove previous plot_widgets
        app.lay_g_h2_5.itemAt(0).widget().setParent(None)

    date_axis = pg.DateAxisItem(orientation='bottom')
    app.pw_sondes = pg.PlotWidget(axisItems={'bottom': date_axis})
    date_axis.linkToView(app.pw_sondes.getViewBox())
    app.pw_sondes.setBackground('w')
    app.lay_g_h2_5.addWidget(app.pw_sondes)



    # build the dataframe
    data = dict()
    data['ls_metrics'] = []
    # who: 'sonde1'
    # when: '1_1'
    who = app.cb_g_sondes_who.currentText()
    when = app.cb_g_sondes_when.currentText()
    fol = ddh_get_path_local_folder_dl_files_sondes()
    ls_do = [i for i in glob.glob(f'{fol}/{who}_SENS_{when}_RDO.csv')]
    if ls_do:
        p = ls_do[0]
        _get_df_from_csv_files(p, data)
    ls_pts = [i for i in glob.glob(f'{fol}/{who}_SENS_{when}_External_PTS_Bar30.csv')]
    if ls_pts:
        p = ls_pts[0]
        _get_df_from_csv_files(p, data)
    ls_cond = [i for i in glob.glob(f'{fol}/{who}_SENS_{when}_ATLAS.csv')]
    if ls_cond:
        p = ls_cond[0]
        _get_df_from_csv_files(p, data)


    # variables
    pw = app.pw_sondes
    p1 = pw.plotItem



    # create legend
    legend = pw.addLegend(
        pen=pg.mkPen('black', width=2),
        labelTextSize='12pt',
        brush=(240, 240, 255, 150),
        # distance from right, top
        offset=(-10, -200)
    )


    # color names
    color1 = 'red'
    color2 = 'blue'
    color3 = 'green'
    color4 = 'orange'
    name1 = 'Temperature (C)'
    name2 = 'Pressure (bar)'
    name3 = 'DOC (mg/l)'
    name4 = 'pH'
    p1.getAxis('left').setLabel(name1, color=color1)



    # create a new ViewBox, link the right axis to its coordinate system
    p2 = pg.ViewBox()
    p1.showAxis('right')
    p1.scene().addItem(p2)
    p1.getAxis('right').linkToView(p2)
    p2.setXLink(p1)
    p1.getAxis('right').setLabel(name2, color=color2)



    # create third ViewBox, this time we need to create a new axis as well
    p3 = pg.ViewBox()
    ax3 = pg.AxisItem('right')
    p1.layout.addItem(ax3, 2, 3)
    p1.scene().addItem(p3)
    ax3.linkToView(p3)
    p3.setXLink(p1)
    ax3.setLabel(name3, color=color3)



    # create fourth ViewBox, this time we need to create a new axis as well
    p4 = pg.ViewBox()
    ax4 = pg.AxisItem('right')
    p1.layout.addItem(ax4, 2, 4)
    p1.scene().addItem(p4)
    ax4.linkToView(p4)
    p4.setXLink(p1)
    ax4.setLabel(name4, color=color4)




    # view has resized; update auxiliary views to match
    def updateViews():
        p2.setGeometry(p1.vb.sceneBoundingRect())
        p3.setGeometry(p1.vb.sceneBoundingRect())
        p4.setGeometry(p1.vb.sceneBoundingRect())
        p2.linkedViewChanged(p1.vb, p2.XAxis)
        p3.linkedViewChanged(p1.vb, p3.XAxis)
        p4.linkedViewChanged(p1.vb, p4.XAxis)
    updateViews()
    p1.vb.sigResized.connect(updateViews)



    # plot the data
    # TEMPERATURE expected to always be there get the sub_dataframes and plot
    d = data['df_pts_30'].reset_index(drop=True)
    p1.plot(
        list(d['timestamp_adjusted']),
        list(d['temperature_c']),
        symbol='o', pen=None, size=1, symbolPen=color1,
        symbolSize=5, symbolBrush=color1,
        name=name1
    )



    if 'PTS_Bar30' in data['ls_metrics']:
        d = data['df_pts_30'].reset_index(drop=True)
        p_di = pg.PlotDataItem(
            list(d['timestamp_adjusted']),
            list(d['pressure_bar']),
            symbol='o', pen=None, size=1, symbolPen=color2,
            symbolSize=5, symbolBrush=color2, name=name2
        )
        p2.addItem(p_di)
        legend.addItem(p_di, name=name2)



    if 'RDO' in data['ls_metrics']:
        # green pistaccio
        d = data['df_doc'].reset_index(drop=True)
        p_di = pg.PlotDataItem(
            list(d['timestamp_adjusted']),
            list(d['value']),
            symbol='o', pen=None, size=1, symbolPen=color3,
            symbolSize=5, symbolBrush=color3, name=name3
        )
        p3.addItem(p_di)
        legend.addItem(p_di, name=name3)


    if 'ph' in data['ls_metrics']:
        d = data['df_ph'].reset_index(drop=True)
        p_di = pg.PlotDataItem(
            list(d['timestamp_adjusted']),
            list(d['sensor_val']),
            symbol='o', pen=None, size=1, symbolPen=color4,
            symbolSize=5, symbolBrush=color4, name=name4
        )
        p4.addItem(p_di)
        legend.addItem(p_di, name=name4)






def sondes_serve_graph_request(
        app,
        plot_reason=''):
    try:
        app.lbl_graph_err_sondes.setVisible(False)
        app.lbl_graph_busy_sondes.setVisible(True)
        QCoreApplication.processEvents()
        _sondes_plot(app)


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

