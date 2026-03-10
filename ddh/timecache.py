import redis
from utils.redis import RD_DDH_SLO_LS



r = redis.Redis('localhost', port=6379)
PRE = 'ddh:timecache:'



def _add_prefix(k):
    if k.startswith(PRE):
        return k
    return f'{PRE}{k}'



def annotate_time_this_occurred(k, t):
    if t <= 0:
        return
    k = _add_prefix(k)
    r.setex(k, t, 1)



def is_it_time_to(k, t):
    k = _add_prefix(k)
    if r.exists(k):
        # not enough time passed since last occurrence
        return False

    annotate_time_this_occurred(k, t)
    return True




def query_is_it_time_to(k):
    return not r.exists(_add_prefix(k))



if __name__ == '__main__':
    mask = RD_DDH_SLO_LS + '*'
    print(mask)
    ls_slo_keys = r.keys(mask)
    print(ls_slo_keys)
