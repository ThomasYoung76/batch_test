#!/usr/bin/env python3
"""
Created on 

@author: yangshifu
@mail: yangshifu@sensetime.com
"""
import os
import re
import shutil
from pathlib import Path
from datetime import datetime
import argparse

desc = """
    文件时间间隔小于3.1秒的文件当作一个序列，放在一个新的目录下
"""


parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument(dest='data_path', action='store', help='数据集目录或者数据集的绝对路径')

args = parser.parse_args()


p = Path(args.data_path)

sequence = {}
for f in p.rglob('*.yuv'):
    par = str(f.parent)
    if par not in sequence.keys():
        sequence[par] = []
    sequence[par].append(str(f))

seq = []
for item, value in sequence.items():
    pattern = "(\d{8}-\d{2}-\d{2}-\d{2}-\d{3})\.yuv"
    time_value = map(lambda x: re.search(pattern, x).group(1), value)
    gap_value = list(map(lambda x: datetime.strptime(x, '%Y%m%d-%H-%M-%S-%f'), time_value))
    sub_seq = [value[0]]
    for i in range(1, len(gap_value)):
        gap = (gap_value[i] - gap_value[i - 1]).seconds + (gap_value[i] - gap_value[i - 1]).microseconds / 1000000
        if gap < 3.1:
            sub_seq.append(value[i])

        else:
            # 将sub_seq里的文件移到新建的子层目录下
            new_dir_name = re.search('(\d{8}-\d{2}-\d{2}-\d{2})-\d{3}\.yuv', sub_seq[0]).group(1)
            new_dir = str(Path(sub_seq[0]).parent) + os.sep + new_dir_name
            print(new_dir)
            if not os.path.isdir(new_dir):
                os.mkdir(new_dir)
            for s in sub_seq:
                shutil.move(s, new_dir)
            # 重置sub_seq
            sub_seq = [value[i]]

    # 处理最后一个序列
    new_dir_name = re.search('(\d{8}-\d{2}-\d{2}-\d{2})-\d{3}\.yuv', sub_seq[0]).group(1)
    new_dir = str(Path(sub_seq[0]).parent) + os.sep + new_dir_name
    print(new_dir)
    if not os.path.isdir(new_dir):
        os.mkdir(new_dir)
    for s in sub_seq:
        shutil.move(s, new_dir)
    # 重置sub_seq
    sub_seq = [value[i]]
