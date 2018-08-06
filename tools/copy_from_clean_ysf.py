#!/usr/bin/env python3
"""
Created on

@author: yangshifu
@mail: yangshifu@sensetime.com
"""
import os
import shutil
import argparse


desc = """
数据集清洗后，通过清洗后的文件列表获得清洗后的测试集
"""
parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-c', dest='clean_file', action='store', help='清洗文件所在路径')
parser.add_argument('-t', dest='testset', action='store', help="数据集目录名")
args = parser.parse_args()

gooddata = [line.strip() for line in open(args.clean_file)]

for line in gooddata:
    dst_image = line.replace(args.testset + '/', args.testset + 'clean' + '/')
    dst_image_dir = os.path.dirname(dst_image)
    if not os.path.isdir(dst_image_dir):
        os.makedirs(dst_image_dir)
    shutil.copy(line, dst_image_dir)
