import os
import numpy as np
import pandas as pd





def ddh_calc_stats_of_csv_file_for_history_table(
        path_csv
) -> str:

    bn_csv = os.path.basename(path_csv)
    stats = f''
    df = pd.read_csv(path_csv)


    # this will contain filtered values
    ls_t_filtered = []
    ls_p_filtered = []
    ls_dot_filtered = []
    ls_doc_filtered = []


    # ------------------------------------------
    # calculate stats ONLY for data IN-WATER
    # ------------------------------------------
    # TDO
    if '_TDO' in bn_csv:
        ls_t = list(df['Temperature (C)'])
        ls_p = list(df['Pressure (dbar)'])
        limit_80 = max(ls_p) * .80
        for i, pv in enumerate(ls_p):
            if pv >= limit_80:
                ls_t_filtered.append(ls_t[i])
                ls_p_filtered.append(ls_p[i])

    elif '_CTD' in bn_csv:
        stats = 'implement soon'

    elif '_DissolvedOxygen' in bn_csv:
        ls_dot = list(df['DO Temperature (C)'])
        ls_doc = list(df['Dissolved Oxygen (mg/l)'])
        if 'Water Detect (%)' in df.columns:
            ls_wat = list(df['Water Detect (%)'])
            for i, wv in enumerate(ls_wat):
                if float(wv) >= 50:
                    ls_dot_filtered.append(ls_dot[i])
                    ls_doc_filtered.append(ls_doc[i])
        else:
            # do nothing, keep all DO because we have no water sensor
            ls_dot_filtered = ls_dot
            ls_doc_filtered = ls_doc


    # build the summary statistics METRIC string for the table
    try:
        if ls_t_filtered:
            vt_filtered = np.nanmean(ls_t_filtered)
            stats += f'{vt_filtered:.2f} °C_'
        if ls_p_filtered:
            vp_filtered = np.nanmean(ls_p_filtered)
            stats += f'{vp_filtered:.2f} dbar'
        if ls_dot_filtered:
            vdot_filtered = np.nanmean(ls_dot_filtered)
            stats += f'{vdot_filtered:.2f} °C_'
        if ls_doc_filtered:
            vdoc_filtered = np.nanmean(ls_doc_filtered)
            stats += f'{vdoc_filtered:.2f} mg/l'
    except (Exception, ) as e:
        print(f'error generating data metric statistics -> {e}')
        stats = 'error stats M'

    # build the summary statistics IMPERIAL string for the table
    try:
        if ls_t_filtered:
            vt_filtered = np.nanmean(ls_t_filtered)
            vt_f = float(str((vt_filtered * 9/5) + 32))
            stats += f'${vt_f:.2f} °F_'
        if ls_p_filtered:
            vp_filtered = np.nanmean(ls_p_filtered)
            vp_f =  float(str(vp_filtered * 0.5468))
            stats += f'{vp_f:.2f} ftm'
        if ls_dot_filtered:
            vdot_filtered = np.nanmean(ls_dot_filtered)
            vt_f = float(str((vdot_filtered * 9/5) + 32))
            stats += f'${vt_f:.2f} °F_'
        if ls_doc_filtered:
            vdoc_filtered = np.nanmean(ls_doc_filtered)
            stats += f'{vdoc_filtered:.2f} mg/l'
    except (Exception, ) as e:
        print(f'error generating data imperial statistics -> {e}')
        stats = 'error stats I'



    if stats == "":
        stats = 'no data in-water'


    return stats