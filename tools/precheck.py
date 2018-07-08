# -*- coding: utf-8 -*-
"""
Created on 2018/7/3

@author: yangshifu
@mail: yangshifu@sensetime.com
"""

"""
批处理前检查数据集
    1. 检查是否存在相同文件，即文件名相同，创建时间相同
"""
import os
from pprint import pprint
from pathlib import Path
import csv


input_dir = "./"
all_dup_file = []
def check_duplicate(input_path):
    suf = {}
    file_names = []     # 文件名
    file_paths = []        # 文件路径
    for root, dirs, files in os.walk(input_dir):
        for f in files:
            fi = Path(root) / f
            # 文件后缀对应的文件数
            suf[fi.suffix] = suf.get(fi.suffix, 0) + 1
            # 文件名和文件路径
            file_names.append(fi.name)
            file_paths.append(fi)

    for i, f in enumerate(file_names):
        dup_file = []
        if f is None:
            continue
        if file_names.count(f) > 1:
            while file_names.count(f) != 0:
                index = file_names.index(f)
                dup_file.append(file_paths[index])
                file_names[index] = None
        if dup_file:
            # 判断同名文件是否创建时间相同
            mtime = list(map(lambda x: os.path.getmtime(x), dup_file))
            if len(mtime) != len(set(mtime)):
                print('存在相同的拷贝文件：{}'.format(dup_file))
                all_dup_file.append(dup_file)
    with open("same_name.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(all_dup_file)
    return suf


if __name__ == "__main__":
    result = check_duplicate(input_dir)
    print("--------------------------")
    print("文件类型对应的个数： ")
    pprint(result)
