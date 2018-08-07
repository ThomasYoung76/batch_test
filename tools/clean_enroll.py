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
    files = f.glob('*.yuv')
    count = len(list(files))
    person = f.parent.name
    print("Person: {}. count: {}".format(person, count))
    if count == 0:
        print("Warning : count of {} is 0. requires 1 to 5".format(str(f)))
    elif count > 5:
        print("Warning : count of {} is more than 5. now delete to 5".format(str(f)))
        for fa in list(files)[5:]:
            os.remove(str(fa))
            # 删除同名文件的jpg
            try:
                os.remove(str(fa).strip('.yuv') + '.jpg')
            except:
                continue
