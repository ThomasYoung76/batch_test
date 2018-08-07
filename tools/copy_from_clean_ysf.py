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
注：清洗的文件列表路径必须是绝对路径
python3 copy_from_clean_ysf.py -c dataclean#RGB_foreigner_250_clean#0.55_0.7#/db_aligned.txt -t RGB_foreigner_250_clean
"""
parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-c', dest='clean_file', action='store', help='清洗文件所在路径')
parser.add_argument('-t', dest='testset', action='store', help="数据集目录名")
parser.add_argument('-h', dest='is_hack', action='store', default=False, help='是否需要拷贝假人Hack目录')
args = parser.parse_args()

hack_flag = 'Hack'
gooddata = [line.strip() for line in open(args.clean_file)]

for line in gooddata:
    dst_image = line.replace(args.testset + '/', args.testset + 'V0' + '/')
    dst_image_dir = os.path.dirname(dst_image)
    if not os.path.isdir(dst_image_dir):
        os.makedirs(dst_image_dir)
    yuv_line = line.strip().rstrip('.jpg') + '.yuv'
    shutil.copy2(yuv_line, dst_image_dir)
    shutil.copy2(line, dst_image_dir)

    # 拷贝假人数据
    src_hack_dir = os.path.join(os.path.dirname(os.path.dirname(line)), 'Hack')        # 假人源目录
    dst_hack_dir = os.path.join(os.path.dirname(dst_image_dir), 'Hack')   # 假人拷贝目的路径
    try:
        shutil.copytree(src_hack_dir, dst_hack_dir)
    except FileExistsError as fee:
        continue
    except FileNotFoundError as fnfe:
        continue
