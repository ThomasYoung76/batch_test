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

desc = """
1.将后缀为”_depth.raw”文件名改为 “当前目录名称.depth”，
将后缀为”_nir.raw”文件名改为 “当前目录名称.ir”，并放入目的路径中
    usage： python3 copy_file.py ./ ./bak -u
    用法： python3 copy_file.py 数据源目录 数据输出目录
2.将后缀为'.xls'的文件名改为'当前目录名称.abc',并放入目的路径中
    usage: python3 copy_file.py ./ ./bak -s '.xls' -d '.abc'
    用法：python3 copy_file.py 数据源目录 数据输出目录 -s 待替换的源后缀 -d 目标后缀
3.拷贝文件时仅修改后缀
    usage: python3 copy_file.py ./ 20180601bak  -s "_2.gray16" -d ".ir" 
"""

parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('src_dir', action="store", help='数据源目录')
parser.add_argument('dst_dir', action="store", help='数据输出目录')
parser.add_argument('-s', action="store", dest='src_suf', help='待替换的源后缀', default='')
parser.add_argument('-d', action="store", dest='dst_suf', help='目标后缀', default='')
parser.add_argument('-u', "--upward", action="store_true", default=False, help="文件路径向上移一层")
parser.add_argument('-o', '--only_suffer', action='store_true', default=False, help="是否仅更改后缀名")

options = parser.parse_args()


def bak_file(src, dst, src_suf, dst_suf, is_upward=False, is_suf=False):
    """
    按指定方式批量更改文件名并拷贝文件
    :param src: 源路径
    :param dst: 目的路径
    :param src_suf: 待替换的后缀
    :param dst_suf: 目标后缀
    :param is_upward: 目录是否向上移一层
    :return:
    """
    for root, dirs, files in os.walk(src):
        for file_name in files:
            file_path = os.path.join(root, file_name)   # 文件路径
            dir_path = os.path.dirname(file_path)       # 目录路径
            dir_name = os.path.basename(dir_path)   # 最后一级目录名
            if file_path.endswith(src_suf):
                if is_suf:
                    new_name = file_name.replace(src_suf, dst_suf)
                    dir_gap = os.path.relpath(dir_path, src)
                else:
                    new_name = dir_name + dst_suf   # 拷贝的文件名为上级目录+目标后缀
                    # 从源目录src开始计算dir_path的上层目录的相对路径
                    dir_gap = os.path.relpath(os.path.dirname(dir_path), src)
                if is_upward:
                    dir_gap = os.path.dirname(dir_gap)
                new_dir = os.path.join(dst, dir_gap)
                if not os.path.isdir(new_dir):
                    os.makedirs(new_dir)
                shutil.copy(file_path, os.path.join(new_dir, new_name))

if not os.path.isdir(options.src_dir):
    print("Error. source diretory({}) is not exist".format(options.src_dir))
    sys.exit(1)

if not os.path.isdir(options.dst_dir):
    os.makedirs(options.dst_dir)

if not options.src_suf and not options.dst_suf:
    bak_file(options.src_dir, options.dst_dir, '_depth.raw', '.depth', options.upward)
    bak_file(options.src_dir, options.dst_dir, '_nir.raw', '.ir', options.upward)
else:
    bak_file(options.src_dir, options.dst_dir, options.src_suf, options.dst_suf, options.upward, is_suf=options.only_suffer)
print("Success. the copy files is in {}".format(os.path.abspath(options.dst_dir)))


