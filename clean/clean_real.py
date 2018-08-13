#!/usr/bin/env python3
"""
Created on 

@author: yangshifu
@mail: yangshifu@sensetime.com
"""
import argparse
import os
from pathlib import Path
import random


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
    # 真人
    files_real = list(f.glob('*.yuv'))
    count_real = len(files_real)
    # 假人
    files_hack = list(Path(str(f).replace('Real', 'Hack')).glob('*.yuv'))
    count_hack = len(files_hack)
    person = f.parent.name
    dict_real[person] = count_real
    print("Person: {}. count real: {}. count hack: {}".format(person, count_real, count_hack))

print("--------------------------------------------")
count_person = dict_real.values()

person_20 = list(filter(lambda x: x < 20, count_person))
person_200 = list(filter(lambda x: x > 200, count_person))

for item in dict_real:
    if dict_real[item] in person_20:
        print("{}: {}".format(item, dict_real[item]))
        # 删除真人数小于20张的人
        # os.removedirs()
    if dict_real[item] in person_200:
        print("{}: {}".format(item, dict_real[item]))
        # 真人数超过200时，随机删除到200张真人
        dir_person = next(data.rglob('{}'.format(item)))
        dir_person_real = dir_person / 'Real'
        person_real = list(map(str, dir_person_real.rglob('*.yuv')))       # 真人
        person_real_delete = random.choices(person_real, k=(dict_real[item]-200))      # 随机选取（总数-200）张图片
        for f in person_real_delete:
            os.remove(f)
            # 删除同名文件的jpg
            try:
                os.remove(f.strip('.yuv') + '.jpg')
            except FileNotFoundError:
                continue
