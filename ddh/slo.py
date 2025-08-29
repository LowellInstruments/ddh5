import redis
from rd_ctt.ddh import RD_DDH_SLO_LS



r = redis.Redis('localhost', port=6379)



def slo_add(mac):
    k = f"{RD_DDH_SLO_LS}{mac.replace(':', '')}"
    r.set(k, 1)
    r.expire(k, 120)



def slo_delete(mac):
    k = f"{RD_DDH_SLO_LS}{mac.replace(':', '')}"
    r.delete(k)



def slo_contains(mac):
    k = f"{RD_DDH_SLO_LS}{mac.replace(':', '')}"
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
    ls_slo_keys = r.keys(RD_DDH_SLO_LS + '*')
    for k in ls_slo_keys:
        r.delete(k.decode())



if __name__ == '__main__':
    print(slo_contains('11'))


