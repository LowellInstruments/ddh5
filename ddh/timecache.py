import redis
from rd_ctt.ddh import RD_DDH_SLO_LS



r = redis.Redis('localhost', port=6379)
PRE = 'ddh:timecache:'



def _pre(k):
    if k.startswith(PRE):
        return k
    return f'{PRE}{k}'



def annotate_time_this_occurred(k, t):
    if t <= 0:
        return
    k = _pre(k)
    r.set(k, 1)
    r.expire(k, t)



def is_it_time_to(k, t):
    k = _pre(k)
    if r.exists(k):
        # not enough time passed since last occurrence
        return False

    annotate_time_this_occurred(k, t)
    return True


# todo: maybe remove all this file and use REDIS


def query_is_it_time_to(k):
    return not r.exists(_pre(k))



if __name__ == '__main__':
    mask = RD_DDH_SLO_LS + '*'
    print(mask)
    ls_slo_keys = r.keys(mask)
    print(ls_slo_keys)
