#!/usr/bin/env python3
"""
Created on 2018/11/22

@author: yangshifu
@mail: yangshifu@sensetime.com
"""

import os
import shutil
import argparse
import cv2
import traceback
from pathlib import Path
import numpy as np


# 配置信息，可修改
input_dir = r'D:\doc\samsung\20181122-三星3D测试集数据外包采集第一批-yangshifu'
height = 180
width = 240


def find_files_by_type(src, filetype="ir"):
    files = []
    for file_name in Path(src).rglob('*.{0}'.format(filetype)):
        files.append(str(file_name))
    return files


def raw2jpg(filename, src_dir='', dst_dir='', height=height, width=width):
    try:
        img = np.fromfile(filename, dtype=np.uint16)
        img = img.reshape((height, width))
        img.astype(np.float)
        img = np.sqrt(img)
        img = img * (255 / img.max())
        #img.astype(np.uint8)
        if src_dir:
            jpg_filename = filename.replace(src_dir, dst_dir) + '.jpg'
            Path(jpg_filename).parent.mkdir(parents=True, exist_ok=True)
        else:
            jpg_filename = filename + '.jpg'
        cv2.imwrite(jpg_filename, img)
    except Exception as info:
        print('Error: s {}'.format(filename))
        print(info)
        traceback.print_exc()
        print('Please close file and directories and continue...')
        return False
    return True


def copy_files_by_type(src, filetype="jpg"):
    files = []
    for file_name in Path(src).rglob('*.{0}'.format(filetype)):
        if src.endswith(os.sep):
            src = src.rstrip(os.sep)
        jpg_filename = str(file_name).replace(src, src + '_jpg')
        jpg_dir = Path(jpg_filename).parent
        jpg_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(file_name), str(jpg_dir))
        files.append(str(file_name))
    return files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="raw图转jpg", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', '--input_dir', default=input_dir, action="store", help=u'输入目录')
    parser.add_argument('-m', '--is_not_move', default=True, action="store_false", help="是否将转换好的jpg移到新的输出目录下，默认移走")
    parser.add_argument('-d', '--is_convert_depth', default=False, action="store_true", help="是否转换depth图, 默认不转")
    options = parser.parse_args()
    input_dir = options.input_dir
    output_dir = input_dir.rstrip(os.sep) + '_jpg'
    ir_files = find_files_by_type(input_dir, filetype="ir")
    count = 0
    total = len(ir_files)
    for ir in ir_files:
        raw2jpg(ir)
        count += 1
        print("处理进度： {} / {}. 当前文件：{}".format(count, total, ir), end='\r')

    if options.is_convert_depth:
        print('\n')
        depth_files = find_files_by_type(input_dir, filetype="depth")
        count_depth = 0
        for depth in depth_files:
            raw2jpg(depth)
            count_depth += 1
            print("处理进度： {} / {}. 当前文件：{}".format(count_depth, total, depth), end='\r')

    print("\nSuccess convert ir to jpg. ")
    print("---------------------------")
    if options.is_not_move:
        print("Start to move jpg. waiting ...")
        copy_files_by_type(input_dir)
        print("Success move jpg file to {}".format(output_dir))
    else:
        print("Done. See jpg file in {}".format(input_dir))
