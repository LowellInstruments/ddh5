import redis
from utils.ddh_common import exp_get_skip_slo
from utils.redis import RD_DDH_SLO_LS
from ddh_log import lg_ble as lg



DISABLE_SLO = exp_get_skip_slo() == 1
r = redis.Redis('localhost', port=6379)



def slo_add(mac):
    # these cases ADD to smart lock-out:
    #       - refreshed slo
    #       - just purged from black macs list
    #       - downloaded OK
    #       - HBW told us no need to download
    #       - too many errors
    if DISABLE_SLO:
        slo_delete_all()
        print(f'warning, SLO disabled in config.toml, not working with mac {mac}')
        return
    mac = mac.replace(':', '-')
    k = f"{RD_DDH_SLO_LS}{mac}"
    r.setex(k, 120, 1)



def slo_delete(mac):
    mac = mac.replace(':', '-')
    k = f"{RD_DDH_SLO_LS}{mac}"
    r.delete(k)



def slo_contains(mac):
    mac = mac.replace(':', '-')
    k = f"{RD_DDH_SLO_LS}{mac}"
    return r.exists(k)



def slo_get_all():
    ls = list(r.scan_iter(f'{RD_DDH_SLO_LS}*'))
    ls = [i.decode() for i in ls]
    # ls: ['ddh:slo:ls:<MAC1>', 'ddh:slo:ls:<MAC2>']
    return [i.replace(RD_DDH_SLO_LS, '') for i in ls]



def slo_print_all_ttl():
    ls = list(r.scan_iter(f'{RD_DDH_SLO_LS}*'))
    return [(i.decode(), r.ttl(i)) for i in ls]



def slo_delete_all():
    ls_slo_keys = list(r.scan_iter(f'{RD_DDH_SLO_LS}*'))
    for k in ls_slo_keys:
        r.delete(k.decode())



def slo_delete_expired_ones():
    ls_slo_keys = list(r.scan_iter(f'{RD_DDH_SLO_LS}*'))
    for k in ls_slo_keys:
        v = r.ttl(k.decode())
        if v and v == -2:
            r.delete(k.decode())



if __name__ == '__main__':
    slo_delete_expired_ones()


