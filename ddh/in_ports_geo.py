import json
import requests
from ddh.notifications_v2 import notify_ddh_in_port
from ddh.timecache import annotate_time_this_occurred, is_it_time_to, query_is_it_time_to
from ddh_log import lg_gps as lg
from utils.ddh_common import ddh_config_is_skip_in_port_enabled



g_last_in_port = False
TIMEOUT_CACHE_IN_PORT_SECS = 300
d_gps_n = {}



def ddh_ask_in_port_to_ddn(_g, notify=True, tc=TIMEOUT_CACHE_IN_PORT_SECS):

    if ddh_config_is_skip_in_port_enabled() == 0:
        # the skip-when-in-port feature is disabled
        # so we return "NOT in port" to force a download
        return 0

    global g_last_in_port
    s = 'tell_we_in_port'
    if not query_is_it_time_to(s):
        # use our cache to avoid repeated queries
        return g_last_in_port



    # build the query to API
    lat, lon, tg, speed = _g
    if not lat:
        # NOT in port on error 'lat'
        return 0
    
    
    
    # cache expired but maybe we already know the answer
    global d_gps_n
    try:
        lat_n = f'{float(lat):.2f}')
        lon_n = f'{float(lon):.2f}')
        k = f'{lat_n},{lon_n}'
        if k in d_gps_n.keys():
            annotate_time_this_occurred(s, tc)
            g_last_in_port = 1
            return g_last_in_port
    except (Exception, ):
        pass

    
    
    
    addr_ddn_api = 'ddn.lowellinstruments.com'
    port_ddn_api = 9000
    ep = 'gps_in_port'
    url = f'http://{addr_ddn_api}:{port_ddn_api}/{ep}?lat={lat}&lon={lon}'

    # send the query
    try:
        annotate_time_this_occurred(s, tc)
        rsp = requests.get(url, timeout=3)
        rsp.raise_for_status()
        j = json.loads(rsp.content.decode())
        # j: {'in_port': True}
        g_last_in_port = int(j['in_port'])
        if g_last_in_port and notify:
            if is_it_time_to('notify_we_in_port', 43200):
                notify_ddh_in_port(_g)
            # add to our small database
            lat_n = f'{float(lat):.2f}')
            lon_n = f'{float(lon):.2f}')
            k = f'{lat_n},{lon_n}'
            d_gps_n[k] = 1
        return g_last_in_port

    except (Exception,) as err:
        g_last_in_port = 0
        lg.a(f'error, querying DDN API about lat {lat}, lon {lon} -> {err}')
        lg.a('warning, no API response, consider NOT in port')




def ddh_ask_in_port_to_local_db(_g, notify=True, tc=TIMEOUT_CACHE_IN_PORT_SECS):

    # ---------------------------------
    # this DOES NOT work on raspberry
    # and it crashes it
    # ---------------------------------
    pass

    # if ddh_config_is_skip_in_port_enabled() == 0:
    #     # the skip-when-in-port feature is disabled
    #     # so we return "NOT in port" to force a download
    #     return 0
    #
    #
    # global g_last_in_port
    # s = 'tell_we_in_port'
    # if not query_is_it_time_to(s):
    #     # use cache to avoid repeated queries
    #     return g_last_in_port
    #
    #
    # lat, lon, tg, speed = _g
    # if not lat:
    #     # NOT in port on error 'lat'
    #     return 0
    #
    #
    # annotate_time_this_occurred(s, tc)
    # try:
    #     g_last_in_port = is_land(lat, lon)
    #     if g_last_in_port and notify:
    #         if is_it_time_to('notify_we_in_port', 43200):
    #             notify_ddh_in_port(_g)
    #     return g_last_in_port
    #
    # except (Exception,) as err:
    #     g_last_in_port = 0
    #     lg.a(f'error, in function ddh_ask_in_port_to_local_db lat {lat}, lon {lon} -> {err}')




# ------
# test
# ------
if __name__ == '__main__':

    # NO PORT
    g = (-9, -9, None, 1)
    # rv = 'in_port_no', ddh_ask_in_port_to_ddn(g, notify=False, tc=1)
    # print(rv)
    #
    # # simulate to expire cache
    # time.sleep(1.1)
    #
    # # ROTARY PORT
    # g = (41.609441, -70.608651, None, 1)
    # rv = 'in_port_ro', ddh_ask_in_port_to_ddn(g, notify=False, tc=0)
    # print(rv)
    #
    # # new bedford port
    # g = (41.63, -70.91, None, 1)
    # rv = 'in_port_nb', ddh_ask_in_port_to_ddn(g, notify=False, tc=0)
    # print(rv)
    #
    # # sandwich port
    # g = (41.771048, -70.503473, None, 1)
    # rv = 'in_port_sw', ddh_ask_in_port_to_ddn(g, notify=False, tc=0)
    # print(rv)
    #
    # # error
    # g = (41.6101, -70.6093, None, 1)
    # rv = 'in_port_er', ddh_ask_in_port_to_ddn(g, notify=False, tc=0)
    # print(rv)
