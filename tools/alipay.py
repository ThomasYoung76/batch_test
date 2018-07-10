# -*- coding: utf-8 -*-
"""
Created on 2018/6/22

@author: yangshifu
@mail: yangshifu@sensetime.com
"""

desc = """  
实际情况：
enum ToygerResultCode {
    TOYGER_SUCCESS = 1,
    TOYGER_TEMPLATE_NOT_AVAILABLE,
    TOYGER_DETECT_FAIL,
    TOYGER_LIVENESS_FAIL,
    TOYGER_VERIFY_FAIL
};

对应文件名：
ENRO_***.jpg
AUTH_***R\d.jpg

测试总次数R：总照片数R
成功次数： R1
活体成功数： R1 + R5
比对成功数： R1 
比对通过率： R1 / (R1+R5)
活体成功率： (R1 + R5) / R
用户通过率： R1 / R
"""

import shutil
from pathlib import Path
import pandas as pd
import argparse



title = ["用例名", "比对成功次数", "活体成功次数", "成功次数", "测试总次数", "比对通过率", "活体通过率", "用户通过率"]

def copy_alidata(input, output):
    """
    规整支付宝测试工具产生的图片数据
    :param input: 输入目录
    :param output: 输出目录
    :return:
    """
    if not Path(output).is_dir():
        Path(output).mkdir()

    for case in Path(input).iterdir():
        if not case.is_dir():
            continue
        # print(case.name)
        dst_case = Path(output) / case.name
        if not dst_case.is_dir():
            dst_case.mkdir()

        enroll = dst_case / "Enroll"
        real = dst_case / "Real"
        if not enroll.is_dir():
            enroll.mkdir()
        if not real.is_dir():
            real.mkdir()
        for jpg in case.rglob("ENRO*.jpg"):
            shutil.copy2(jpg, enroll)
        for jpg in case.rglob("AUTH*.jpg"):
            shutil.copy2(jpg, real)


def class_jpg(input):
    """
    对输入的jpg数据进行分类
    :param input:
    :return:
    """
    result = []
    enro = []
    r1 = []     # 成功图片
    r4 = []     # 活体失败图片
    r5 = []     # 比对失败图片
    for case in Path(input).iterdir():
        if not case.is_dir():
            continue
        r1 = list(case.glob("*R1.jpg"))
        r4 = list(case.glob("*R4.jpg"))
        r5 = list(case.glob("*R5.jpg"))

        # for jpg in case.glob("*R4.jpg"):
        #     fi = jpg.name
        #     r4.append(fi)
        # for jpg in case.glob("*R5.jpg"):
        #     fi = jpg.name
        #     r5.append(fi)
        result.append([case.name, len(r1), len(r4), len(r5)])
    return result


def statics(result, log_file='log.xls', is_real=True):
    """
    汇总测试数据，result中的数据为[[case_name, count_enro, count_R1, count_R4, count_R5], [...], ...]
    真人：
    R1.jpg: 成功文件
    R4.jpg: 活体失败
    R5.jpg: 比对失败
    测试总次数: R = R1 + R4 + R5
    成功次数： R1
    比对成功数： R1
    活体成功数： R1 + R5
    比对通过率： R1 / (R1+R5)
    活体成功率： (R1 + R5) / R
    用户通过率： R1 / R
    假人：
    R1.jpg: 活体失败、比对成功
    R4.jpg: 活体成功(成功防住假人攻击）
    R5.jpg: 活体失败，比对失败
    测试总次数: R = R1 + R4 + R5
    成功hack次数： R1
    活体hack成功数： R1 + R5
    比对成功数： R1 (比对总数：R1+R5)
    比对通过率： R1 / (R1+R5)
    活体hack成功率： (R1 + R5) / R
    用户hack通过率: R1 / R
    :return:
    """
    names_real = {'case': "用例名",
            'verify': '比对成功次数',
            'liveness': '活体成功次数',
            'R1': '成功次数',
            'count': '测试总次数',
            'verify_rate': '比对通过率',
            'liveness_rate': '活体通过率',
            'pass_rate': '用户通过率'}
    names_photo = {'case': "用例名",
            'verify': '比对成功次数',
            'liveness': '活体hack成功数',
            'R1': '成功hack次数',
            'count': '测试总次数',
            'verify_rate': '比对通过率',
            'liveness_rate': '活体hack成功率',
            'pass_rate': '用户hack通过率'}
    df = pd.DataFrame(result, columns=['case', 'R1', 'R4', 'R5'])
    df['verify'] = df['R1']
    df['liveness'] = df['R1'] + df['R5']
    df['count'] = df['R1'] + df['R4'] + df['R5']
    df['verify_rate'] = df['R1'] / (df['R1'] + df['R5'])
    df['liveness_rate'] = (df['R1'] + df['R5']) / (df['R1'] + df['R4'] + df['R5'])
    df['pass_rate'] = df['R1'] / (df['R1'] + df['R4'] + df['R5'])
    df = df.drop(columns=['R4', 'R5'], axis=1, )
    df = df.sort_values(by=['case'])
    writer = pd.ExcelWriter(log_file)
    if is_real:
        df_real = df.rename(columns=names_real)
        df_real.to_excel(writer, sheet_name="真人", freeze_panes=(1, 0), index=False)
    else:
        df_photo = df.rename(columns=names_photo)
        df_photo.to_excel(writer, sheet_name="假人", freeze_panes=(1, 0), index=False)
    writer.save()


if __name__ == "__main__":
    parse = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawTextHelpFormatter)
    parse.add_argument("-i", "--input_dir", action="store", default="alipay", help="数据集输入目录")
    parse.add_argument("-o", "--output_dir", action="store", default="ali_data", help="数据集输出目录")
    parse.add_argument("-c", "--copy", action="store_true", help="是否仅拷贝数据整理，但不统计结果, 默认统计结果")
    parse.add_argument("-l", "--log", action="store", default='log.xls', help="汇总统计的log文件")
    option = parse.parse_args()

    input = option.input_dir
    output = option.output_dir
    is_copy = option.copy
    log_file = option.log
    if is_copy:
        # 结果整理
        copy_alidata(input, output)
        print("Copy raw data success. output directory is: {}".format(output))
    else:
        # 结果汇总
        result = class_jpg(input)
        statics(result, log_file, is_real=True)
        print("Statics success. log file is: {}".format(log_file))


# df = pd.DataFrame(result, columns=title[:6])


