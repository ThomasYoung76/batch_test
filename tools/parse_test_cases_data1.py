#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:    xurongzhong#126.com wechat:pythontesting qq:37391319
# CreateDate: 2018-1-8
# parse_test_cases_data.py

'''
汇总测试用例生成的数据。

使用方法：

参数input_directory：为包含测试结果的目录。input_directory下面有测试人员的拼音名目录，
拼音名目录下有数字目录，比如01，对应测试用用例的序号。01目录下面有log.xls之类的测试记录
文件。

参数：output：为汇总测试的输出文件。
'''

import traceback
import shutil
import os
import argparse

import pandas

from data_common import produce_xls

input_directory = r"C:\Users\yangshifu\Downloads\支付宝\sensetime"
output = r"C:\Users\yangshifu\Documents\test\bak\output.xls"
is_format = False   # 是否输出标准格式的excel文件
results = {}


desc = """
    人脸解锁-测试用例数据结果统计
"""

parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-i', action="store", dest='input', default=input_directory, help='输入的测试数据目录')
parser.add_argument('-o', action="store", dest='output', default=output, help='输出的统计结果')
parser.add_argument('-f', action="store_true", dest='format', default=is_format, help="是否输出标准用例格式的excel")

options = parser.parse_args()

if not os.path.isdir(options.input):
    print("Error, cannot find input directory: {}".format(options.input))


def get_result(file_name):
    '''
    统计测试工具生成的用例。
    '''
    try:
        if '.xls' in file_name:
            records = pandas.read_excel(file_name)
        if '.csv' in file_name:
            records = pandas.read_csv(file_name)
        total = len(records)
        compare = len(records[records['比对'] == '通过'])
        live = len(records[records['活体'] == '通过'])
        success = len(records[records['结果'] == '通过'])
        test = len(records[records['当前尝试次数'] == 1])

    except Exception as info:
        print('Error in reading: {}'.format(file_name))
        print(info)
        traceback.print_exc()
        print('continue...')
        total = compare = live = success = test = 0

    return (total, compare, live, success, test)


# 遍历目录以统计测试工具生成的xls文件
for root, dirs, files in os.walk(options.input):

    for file_name in files:
        if file_name.endswith("csv"):
            seq = int(root.split(os.sep)[-1].lstrip('0'))
            result = get_result(u"{}{}{}".format(root, os.sep, file_name))
            if seq not in results:
                results[seq] = []
            results[seq].append(result)
            if str(seq) not in file_name:
                os.chdir(root)
                shutil.move(file_name, u"{}_{}".format(seq, file_name))

print(results)
produce_xls(results, output, number=22)

if options.format:
    from Alipay_53cases.format_testcase_reports import format_excel
    format_excel(input_file=output, output_file=output)
