import toml
from utils.ddh_common import ddh_get_path_to_folder_tweak
from ddh_log import lg_gui as lg



FILE_SAVED_PREFERENCES = f'{ddh_get_path_to_folder_tweak()}/.saved_preferences.toml'



def _write(k, v):
    # first read any existing dictionary
    try:
        with open(FILE_SAVED_PREFERENCES, 'r') as f:
            d = toml.load(f)
    except (FileNotFoundError, ):
        lg.a(f'preferences file, initializing new dictionary')
        d = {}

    # update dictionary with new value
    d[k] = v

    # write dictionary to file
    try:
        with open(FILE_SAVED_PREFERENCES, 'w') as f:
            toml.dump(d, f)
            v = d[k]
            lg.a(f'preferences file, write {k} = {v}')
    except (Exception, ) as ex:
        lg.a(f'warning, write {k} to preferences file -> {ex}')


def _read(k, def_rv):
    try:
        with open(FILE_SAVED_PREFERENCES, 'r') as f:
            d = toml.load(f)
            v = d[k]
            lg.a(f'preferences file, read {k} = {v}')
            return v
    except (Exception, ) as ex:
        lg.a(f'warning, fixing read {k} from preferences file -> {ex}')
        _write(k, def_rv)
        return def_rv



def preferences_get_brightness_clicks():
    return _read('brightness', 9)



def preferences_get_models_index():
    return _read('models_index', 0)



def preferences_set_brightness_clicks(v):
    return _write('brightness', v)



def preferences_set_models_index(v):
    return _write('models_index', v)


