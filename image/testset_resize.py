#!/usr/bin/env python3
"""
Created on 2018/12/2

@author: yangshifu
@mail: yangshifu@sensetime.com
"""
import os
import shutil
import argparse
from pathlib import  Path
import cv2

# 配置信息，可修改
input_dir = r'D:\gitlab\samsung'
height = 180
width = 240


def find_files_by_type(src, filetype="ir"):
    files = []
    for file_name in Path(src).rglob('*.{0}'.format(filetype)):
        files.append(str(file_name))
    return files


def resize_jpg(filename, height=height, width=width):
    image = cv2.imread(filename)
    res = cv2.resize(image, (width, height))
    aim_file = filename.rstrip('.jpg') + '_240.jpg'
    cv2.imwrite(aim_file, res)
    return aim_file


def copy_files_by_type(src, filetype="jpg"):
    for file_name in Path(src).rglob('*.{0}'.format(filetype)):
        try:
            aim_file = resize_jpg(str(file_name))
        except:
            print("Error occured in ", str(file_name))
            continue
        if src.endswith(os.sep):
            src = src.rstrip(os.sep)
        jpg_filename = str(file_name).replace(src, src + '_240_jpg')
        jpg_dir = Path(jpg_filename).parent
        jpg_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(aim_file), str(jpg_dir))


parser = argparse.ArgumentParser(prog="testset_resize.py", description="resize jpg 从640*480到240*180")
parser.add_argument('-i', '--input_dir', type=str, required=False, default=input_dir, help='测试集路径')
args = parser.parse_args()
copy_files_by_type(src=args.input_dir)