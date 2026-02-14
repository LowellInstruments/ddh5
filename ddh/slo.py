import redis
from utils.redis import RD_DDH_SLO_LS



r = redis.Redis('localhost', port=6379)



def slo_add(mac):
    # these cases ADD to smart lock-out:
    #       - refreshed slo
    #       - just purged from black macs list
    #       - downloaded OK
    #       - HBW told us no need to download
    #       - too many errors
    k = f"{RD_DDH_SLO_LS}{mac}"
    r.setex(k, 120, 1)



def slo_delete(mac):
    k = f"{RD_DDH_SLO_LS}{mac}"
    r.delete(k)



def slo_contains(mac):
    k = f"{RD_DDH_SLO_LS}{mac}"
    return r.exists(k)



def slo_get_all():
    b = RD_DDH_SLO_LS.encode()
    ls = [i.decode() for i in r.keys() if i.startswith(b)]
    # ls: ['ddh:slo:ls:<MAC1>', 'ddh:slo:ls:<MAC2>']
    return [i.replace(RD_DDH_SLO_LS, '') for i in ls]



def slo_print_all_ttl():
    b = RD_DDH_SLO_LS.encode()
    return [(i, r.ttl(i)) for i in r.keys() if i.startswith(b)]



def slo_delete_all():
    # old was with keys, test it new
    # ls_slo_keys = r.keys(RD_DDH_SLO_LS + '*')
    ls_slo_keys = list(r.scan_iter(f'{RD_DDH_SLO_LS}*'))
    for k in ls_slo_keys:
        r.delete(k.decode())



if __name__ == '__main__':
    print(slo_contains('11'))


