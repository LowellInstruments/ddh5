import json
import requests
from ddh.notifications_v2 import notify_ddh_in_port
from ddh.timecache import is_it_time_to
from ddh_log import lg_gps as lg
from utils.ddh_common import ddh_config_is_skip_in_port_enabled




d_gps_n = {}



def ddh_ask_in_port_to_ddn(
        _g,
        notify=True
) -> int:

    if ddh_config_is_skip_in_port_enabled() == 0:
        # the skip-when-in-port feature is disabled
        # so we return "NOT in port" to force a download
        return 0



    # build the query to API
    lat, lon, tg, speed = _g
    if not lat:
        # NOT in port on error 'lat'
        return 0
    
    

    # ---------------------------------------------------------------
    # maybe we know the answer locally
    # 2 GPS decimals: ~1.11 km ~ a town or large village
    # ---------------------------------------------------------------
    global d_gps_n
    try:
        lat_n = f'{float(lat):.2f}'
        lon_n = f'{float(lon):.2f}'
        k = f'{lat_n},{lon_n}'
        if k in d_gps_n.keys():
            # great! otherwise, continue the rest of this function
            return 1
    except (Exception, ) as e_in_port:
        print(f'error, in new cache for in_port -> {e_in_port}')

    
    
    
    # send IN_PORT query to DDN
    addr_ddn_api = 'ddn.lowellinstruments.com'
    port_ddn_api = 9000
    ep = 'gps_in_port'
    url = f'http://{addr_ddn_api}:{port_ddn_api}/{ep}?lat={lat}&lon={lon}'
    try:
        rsp = requests.get(url, timeout=3)
        rsp.raise_for_status()
        j = json.loads(rsp.content.decode())
        # j: {'in_port': True}
        in_port = int(j['in_port'])
        if in_port and notify:
            if is_it_time_to('notify_we_in_port', 43200):
                notify_ddh_in_port(_g)
            # -------------------------------------------
            # add to OUR small DATABASE of in_port ones
            # -------------------------------------------
            lat_n = f'{float(lat):.2f}'
            lon_n = f'{float(lon):.2f}'
            k = f'{lat_n},{lon_n}'
            d_gps_n[k] = 1
        return in_port

    except (Exception,) as err:
        lg.a(f'error, querying DDN API about lat {lat}, lon {lon} -> {err}')
        lg.a('warning, no API response, consider NOT in port')
        return 0




# ------
# test
# ------
if __name__ == '__main__':

    # NO PORT
    g = (-9, -9, None, 1)
    #
    # ROTARY PORT
    # g = (41.609441, -70.608651, None, 1)

    # new bedford port
    # g = (41.63, -70.91, None, 1)

    # sandwich port
    # g = (41.771048, -70.503473, None, 1)

    # error
    # g = (41.6101, -70.6093, None, 1)
