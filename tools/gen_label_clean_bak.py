# -*- coding: utf-8 -*-
"""
Created on 2018/7/7

@author: yangshifu
@mail: yangshifu@sensetime.com
"""
import os
import argparse

input_dir = "./"

desc = """生成数据集的db_testset.txt和db_testset.label，
用于工具（http://gitlab.bj.sensetime.com/face-recognition/testsets_autoclean）
来清洗数据集"""
parser = argparse.ArgumentParser(description=desc,
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-i', action='store', dest='input_dir', default=input_dir,
                    help='数据集目录')
args = parser.parse_args()


def list2file(result, file_name, first_row=None):
    with open(file_name, 'w') as f:
        if first_row is not None:
            f.write(first_row + '\n')
        for row in result:
            f.write(row + '\n')


result_path = []
result_label = []
for root, dirs, files in os.walk(args.input_dir):
    for file in files:
        if file.endswith('.jpg'):
            f_path = os.path.join(root, file)
            rel_f_path = os.path.relpath(f_path, args.input_dir)
            result_path.append(rel_f_path)
            label_path = rel_f_path.split(os.sep)[0]
            result_label.append(label_path)

list2file(result_label, 'db_testset.label', first_row=str(len(result_label)))
list2file(result_path, 'db_testset.txt')
