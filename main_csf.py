import glob
import os
import pathlib

from lix.lix import _parse_lid_v2_data_file_and_newer
from utils.ddh_common import ddh_get_path_to_folder_dl_files




def main_csf():
    fol = str(ddh_get_path_to_folder_dl_files())
    path_need_csf = f'{fol}/.flag_need_csf'
    ls_lid = glob.glob(f'{fol}/**/*.lid', recursive=True)
    n = len(ls_lid)
    if not os.path.exists(path_need_csf):
        print(f'CSF conversion: detected {n} LID files')
        for i, p in enumerate(ls_lid):
            bn = os.path.basename(p)
            try:
                print(f'\tfile {i + 1} / {n}: {bn} in progress')
                _parse_lid_v2_data_file_and_newer(p, True)
            except (Exception, ) as ex:
                print(f'\terror, cannot convert {bn} to CSF -> {ex}')
    pathlib.Path(path_need_csf).touch(exist_ok=True)



if __name__ == '__main__':
    main_csf()
