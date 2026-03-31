from pysondb import DB



class DbHis:

    def __init__(self, path_to_file):
        self.p = str(path_to_file)
        ls_keys = [
            "mac",
            "SN",
            "e",
            "lat",
            "lon",
            "ep_loc",
            "ep_utc",
            "rerun",
            "uuid_interaction"
        ]
        self.db = DB(keys=ls_keys)
        self.db.load(self.p)

        # big one
        self.p_big = self.p.replace('.json', '_big.json')
        self.db_big = DB(keys=ls_keys)
        self.db_big.load(self.p_big)



    def add(self, mac, sn, e, lat, lon, ep_loc, ep_utc, rerun, u):
        a = {
            # all of these are strings
            "mac": mac,
            "SN": sn,
            # e: string "ok", "error"
            "e": e,
            "lat": lat,
            "lon": lon,
            "ep_loc": ep_loc,
            "ep_utc": ep_utc,
            "rerun": str(rerun),
            "uuid_interaction": str(u)
        }

        # find unique UUID for this database key = mac
        rr_latest = self.get_all()
        id_found = None
        for k, v in rr_latest.items():
            if mac == v['mac']:
                id_found = k
                break

        # this is a small database with only latest result
        try:
            if id_found:
                print(f'id_found for e {e}')
                self.db.update_by_id(id_found, a)
            else:
                print(f'id_NOT_found for e {e}')
                self.db.add(a)
        except (IndexError, KeyError) as ex:
            print(f"error, add db_his -=> {ex}")
        self.db.commit(self.p)


        # do the big one, which contains all of them
        try:
            self.db_big.add(a)
        except (IndexError, KeyError) as ex:
            print(f"error, add db_big_his -=> {ex}")
        self.db_big.commit(self.p_big)



    def get_all(self) -> dict:
        # from small database with only latest values
        return self.db.get_all()


    # -----------------------------------------------
    # we don't use whole database anymore
    # but the following functions are useful for it
    # -----------------------------------------------

    def get_all_big_any(self):
        # from big database, all of them
        return self.db_big.get_all()


    def get_all_big_ok(self):
        # from big database, only OK
        d_big = self.db_big.get_all()
        d = dict()
        for k, v in d_big.items():
            if 'ok' in v['e'].lower():
                d[k] = v
        return d



    def get_all_big_er(self):
        # from big database, only error
        d_big = self.db_big.get_all()
        d = dict()
        for k, v in d_big.items():
            if 'ok' not in v['e'].lower():
                d[k] = v
        return d



    def delete_all(self):
        self.db.delete_all()
        self.db.commit(self.p)



if __name__ == "__main__":
    filename = 'db_his.json'
    db = DbHis(filename)
    # db.add(
    #     mac='D0:2E:AB:D9:30:66',
    #     sn='1234567',
    #     e='err DO-2',
    #     lat='+51.116300',
    #     lon='-114.038300',
    #     ep_loc=1774619218,
    #     ep_utc= 1774633618,
    #     rerun='True',
    #     u='de031c25-7ba4-4f20-beac-8e8263e5af60'
    # )
    rr = db.get_all_er()
    print(rr)

