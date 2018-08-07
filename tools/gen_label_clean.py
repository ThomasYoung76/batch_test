# -*- coding: utf-8 -*-
"""
Created on 2018/7/7

@author: yangshifu
@mail: yangshifu@sensetime.com
"""
import os
import re
import argparse
from pathlib import Path

input_dir = r"D:\doc\test_detect_rate\tongyong100"


def list2file(result, file_name, first_row=None):
    with open(file_name, 'w') as f:
        if first_row is not None:
            f.write('{}\n'.format(first_row))
        for row in result:
            f.write('{}\n'.format(row))

def get_files(src, file_type="jpg", is_abs=False, filter_=''):
    """
    获取文件列表
    :param src: 数据集目录
    :param file_type: 文件类型
    :param is_abs: 是否获取文件的绝对路径
    :param filter_: 路径过滤的正则表达式
    :param is_multi_frame: 测试集是否采用多帧策略
    :return: 文件路径组成的列表
    """
    p = Path(src)
    files = []
    for file_name in p.rglob("*.{}".format(file_type)):
        if not is_abs:
            file_name = file_name.relative_to(src)
        else:
            file_name = file_name.absolute()

        # 按filter_过滤
        if filter_:
            if ':' in filter_:
                filters = filter_.split(':')
                new_filter = r'|'.join(filters)
                ret = re.search(new_filter, str(file_name))
                if not ret:
                    continue
                else:
                    files.append(str(file_name))
            else:
                ret = re.search(filter_, str(file_name))
                if ret:
                    files.append(str(file_name))
                else:
                    continue
        else:
            files.append(str(file_name))

    return files


def get_labels_for_clean(files, level=1):
    """获取用于清洗的labels，适用于工具
    http://gitlab.bj.sensetime.com/face-recognition/testsets_autoclean"""
    labels = []
    for f in files:
        f_dir = f.split('/')
        labels.append('/'.join(f_dir[:level]))
    return labels


def get_labels_for_pc(files, flag='hack'):
    """
    获取文件列表对应的labels
    :param files: 文件列表
    :param flag: 假人标志
    :return:
    """
    labels = []
    for f in files:
        if flag.lower() in f.lower():
            labels.append(1)
        else:
            labels.append(0)
    return labels


if __name__ == "__main__":
    desc = """生成数据集的db_testset.txt和db_testset.label，
    用于工具（http://gitlab.bj.sensetime.com/face-recognition/testsets_autoclean）
    来清洗数据集
    eg:
    python3 gen_label_clean.py -i base_China500 -l -t jpg"""
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', '--input_dir', action='store', default=input_dir,
                        help='数据集目录')
    parser.add_argument('-l', '--label', action='store_true', default=False, help="生成的label用于清洗还是跑批处理, 默认跑pc批处理")
    parser.add_argument('-t', '--type', action='store', default='jpg', help='文件类型')
    parser.add_argument('-a', '--is_abs', action='store', default=False, help="生成的文件列表是否为绝对路径")
    parser.add_argument('-f', '--filter_word', action='store', default='', help="过滤表达式")
    parser.add_argument('-v', '--level', action='store', type=int, help="label中目录的层级")
    args = parser.parse_args()

    files = get_files(args.input_dir, file_type=args.type, is_abs=args.is_abs, filter_=args.filter_word)
    if args.label:
        labels = get_labels_for_clean(files, level=args.level)
        list2file(labels, 'db_testset.label', first_row=str(len(labels)))
    else:
        labels = get_labels_for_pc(files, 'hack')
        list2file(labels, 'db_testset.label')

    list2file(files, 'db_testset.txt')

