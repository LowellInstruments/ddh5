import time
from rd_ctt.ddh import RD_DDH_CRASH_TS_TEMPLATE
import redis


r = redis.Redis('localhost', 6379)


def main():
    k = RD_DDH_CRASH_TS_TEMPLATE + str(int(time.time()))
    r.setex(k, 6, 1)

    iterator = r.scan_iter(f'{RD_DDH_CRASH_TS_TEMPLATE}*', count=10)
    n = len(list(iterator))
    print('n', n)
    if n >= 6:
        for key in iterator:
            print(key)
            r.delete(key)

    print(f'application exited {n} times last hour')



if __name__ == '__main__':
    main()
