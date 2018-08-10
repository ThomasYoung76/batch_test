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
清理注册图片，每个人的注册数量控制在1到5张，超出部分直接删除
python3 clean_enroll.py -d RGB_foreigner_250_clean
"""
parser = argparse.ArgumentParser(description="test", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-d', dest='dataset', action="store", help="数据集路径")
args = parser.parse_args()

data = Path(args.dataset)

for f in data.rglob('*Enroll'):
    files = list(f.glob('*.yuv'))
    count = len(files)
    person = f.parent.name
    print("Person: {}. count: {}".format(person, count))
    if count == 0:
        print("Warning : count of {} is 0. requires 1 to 5".format(str(f)))
    elif count > 5:
        print("Warning : count of {} is more than 5. now delete to 5".format(str(f)))
        for fa in files[5:]:
            os.remove(str(fa))
            # 删除同名文件的jpg
            try:
                os.remove(str(fa).strip('.yuv') + '.jpg')
            except:
                continue


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
print(dict_real.values())

