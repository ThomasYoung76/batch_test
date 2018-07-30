#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2018/5/29

@author: yangshifu
@mail: yangshifu@sensetime.com
"""

import os
import sys
import re
import shutil
import argparse
from pathlib import Path

desc = """
ir、depth回滚为原来的gray16文件，
"""

parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('src_dir', action="store", help='数据源目录')
parser.add_argument('dst_dir', action="store", help='数据输出目录')

options = parser.parse_args()


def convert_raw2gray16(src, dst):
    """
    按指定方式批量更改文件名并拷贝文件
    :param src: 源路径
    :param dst: 目的路径
    :return:
    """
    for f in Path(src).rglob("*.ir"):
        new_parent = f.stem
        new_f = f.name.replace('.ir', '_0.gray16')
        dir_gap = os.path.relpath(str(f.parent), src)
        new_dir = os.path.join(dst, dir_gap, new_parent)
        if not os.path.isdir(new_dir):
            os.makedirs(new_dir)
        shutil.copy(str(f), os.path.join(new_dir, new_f))

    for f in Path(src).rglob("*.depth"):
        new_parent = f.stem
        new_f = f.name.replace('.depth', '_1_depth.gray16')
        dir_gap = os.path.relpath(str(f.parent), src)
        new_dir = os.path.join(dst, dir_gap, new_parent)
        if not os.path.isdir(new_dir):
            os.makedirs(new_dir)
        shutil.copy(str(f), os.path.join(new_dir, new_f))


if __name__ == "__main__":
    convert_raw2gray16(options.src_dir, options.dst_dir)