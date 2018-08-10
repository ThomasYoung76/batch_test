#!/usr/bin/env python3
"""
Created on 

@author: yangshifu
@mail: yangshifu@sensetime.com
"""
import argparse
import os
from pathlib import Path


desc = """
控制每个人对应的照片数量
python3 clean_enroll.py -d RGB_foreigner_250_clean
"""
parser = argparse.ArgumentParser(description="test", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-d', dest='dataset', action="store", help="数据集路径")
args = parser.parse_args()


data = Path(args.dataset)
dict_real = {}
for f in data.rglob('*Real'):
    # 假人
    files_real = list(f.glob('*.yuv'))
    count_real = len(files_real)
    # 真人
    files_hack = list(Path(str(f).replace('Real', 'Hack')).glob('*.yuv'))
    count_hack = len(files_hack)
    person = f.parent.name
    dict_real[person] = count_real
    print("Person: {}. count real: {}. count hack: {}".format(person, count_real, count_hack))

print("--------------------------------------------")
count_person = dict_real.values()
