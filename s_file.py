# -*- coding: utf-8 -*-
"""
Created on 2018/7/9

@author: yangshifu
@mail: yangshifu@sensetime.com
"""
import os
import time
import shutil
from pathlib import Path

import pandas as pd


def list2file(result, file_name, first_row=None):
    """ 将列表存入文件 """
    with open(file_name, 'w') as f:
        if first_row is not None:
            f.write('{}\n'.format(first_row))
        for row in result:
            f.write('{}\n'.format(row))


def get_files(src, file_type="jpg", is_abs=False):
    """
    获取文件列表
    :param src: 数据集目录
    :param file_type: 文件类型
    :param is_abs: 是否获取文件的绝对路径
    :return: 文件路径组成的列表
    """
    p = Path(src)
    files = []
    for file_name in p.rglob("*.{}".format(file_type)):
        if not is_abs:
            file_name = file_name.relative_to(src)
        else:
            file_name = file_name.absolute()
        files.append(str(file_name))
    return files


def get_labels_for_clean(files):
    """获取用于清洗的labels，适用于工具
    http://gitlab.bj.sensetime.com/face-recognition/testsets_autoclean"""
    labels = []
    for f in files:
        labels.append(f.split(os.sep)[0])
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


def check_directory(name):
    if Path(name).exists():
        print("{0} Exists，Now Delete it!".format(name))
        try:
            shutil.rmtree(name)
            time.sleep(0.5)
        except Exception as info:
            print('Error: shutil.rmtree {}'.format(name))
            print(info)
            import traceback
            traceback.print_exc()
            print('Please close file and directories and continue...')

    print("mkdir {0} .".format(name))
    Path(name).mkdir(parents=True, exist_ok=True)


def get_live_frr_far(df, colomn1, score, colomn2):
    total = len(df)
    # print(df.head())
    unknow = len(df[df[colomn1] == -1])
    df = df[df[colomn1] != -1]
    real_number = len(df[df[colomn2] == 0])
    photo_number = len(df[df[colomn2] == 1])
    num_2d = len(df.loc[df['filename'].str.contains('/2D_photo/')])
    num_3d = len(df.loc[df['filename'].str.contains('/3D_photo/')])
    num_3d_high = len(df.loc[df['filename'].str.contains('/3D_Highcost/')])
    num_3d_low = len(df.loc[df['filename'].str.contains('/3D_Lowcost/')])

    # 真人识别为假人
    frr_number = len(df.loc[((df[colomn1] > score) & (df[colomn2] == 0))])
    # 假人识别为真人
    far_number = len(df.loc[((df[colomn1] < score) & (df[colomn2] == 1))])
    # 2d假人识别为真人

    far_number_2d = far_number_3d = 0
    far_number_2d = len(df.loc[((df[colomn1] < score) & (df[colomn2] == 1) &
                                df['filename'].str.contains('/2D_photo/', regex=False))])
    ## 3d假人识别为真人
    far_number_3d = len(df.loc[((df[colomn1] < score) & (df[colomn2] == 1) &
                                df['filename'].str.contains('/3D_photo/', regex=False))])
    far_number_3d_high = len(df.loc[((df[colomn1] < score) & (df[colomn2] == 1) &
                                     df['filename'].str.contains('/3D_Highcost/', regex=False))])
    far_number_3d_low = len(df.loc[((df[colomn1] < score) & (df[colomn2] == 1) &
                                    df['filename'].str.contains('/3D_Lowcost/', regex=False))])
    frr = 0 if not real_number else frr_number / float(real_number)
    far2d = 0 if not num_2d else far_number_2d / float(num_2d)
    far3d = 0 if not num_3d else far_number_3d / float(num_3d)
    far3d_high = 0 if not num_3d_high else far_number_3d_high / float(num_3d_high)
    far3d_low = 0 if not num_3d_low else far_number_3d_low / float(num_3d_low)
    far = 0 if not photo_number else far_number / float(photo_number)
    return (far, frr, total, real_number, frr_number, photo_number, far_number,
            unknow, unknow / float(total),
            num_2d, far_number_2d, far2d, num_3d, far_number_3d, far3d,
            num_3d_high, far_number_3d_high, far3d_high,
            num_3d_low, far_number_3d_low, far3d_low)


def get_liveness_server_result(scores, files, labels, score=0.95,
                               replace='/home/andrew/code/data/tof/base_test_data/vivo-liveness/',
                               error_name="live_error.xlsx", type_=''):
    cases = {
        "01": "注册",
        "02": "全脸-稳定拍摄",
        "03": "全脸-晃动拍摄",
        "04": "半脸-鼻子以下超出画面",
        "05": "半脸-眉毛以上超出画面",
        "06": "遮挡大部分五官",
        "07": "遮挡部分五官",
        "08": "手机平放桌面",
        "09": "一睁一闭",
        "10": "闭眼(戴墨镜、裸眼、普通眼镜) ",
        "11": "闭眼(戴墨镜、普通眼镜下滑挡住眼睛) ",
        "12": "闭眼(手机晃动)",
        "13": "注视",
        "14": "非注视",
        "15": "侧躺、平躺"}

    def rename(name):
        type_ = os.path.dirname(name.replace(replace, "").split()[-1])
        last = type_.split('/')[-1]
        if last in cases and replace:
            type_ = type_.replace(last, cases[last])
        return type_

    df_score = pd.read_csv(scores, header=None, names=['score'], engine='c',
                           na_filter=False, low_memory=False)
    df_file = pd.read_csv(files, header=None, names=['filename'])
    df_label = pd.read_csv(labels, header=None, names=['label'], engine='c',
                           na_filter=False, low_memory=False)

    df = pd.concat([df_label, df_score, df_file], axis=1)
    df['type'] = df['filename'].apply(rename)
    # print(df.head())

    results = []

    for name, group in df.groupby('type'):
        result = get_live_frr_far(group, 'score', score, 'label')
        results.append([name, *result[:9]])

    for name, group in df.groupby('label'):
        result = get_live_frr_far(group, 'score', score, 'label')
        results.append([name, *result[:9]])

        # 真人识别为假人
    df1 = df.loc[((df['score'] > score) & (df['label'] == 0))]
    # 假人识别为真人
    df2 = df.loc[((df['score'] < score) & (df['label'] == 1))]
    result = get_live_frr_far(df, 'score', score, 'label')
    results.append(["All", *result[:9]])
    writer = pd.ExcelWriter(error_name)
    df1.to_excel(writer, sheet_name='真人识别为假人', index=False)
    df2.to_excel(writer, sheet_name='假人识别为真人', index=False)

    # print(results)
    df3 = pd.DataFrame(results, columns=[
        "类别", "far", "frr", "总数", "真人总数", "真人识别为假人", "假人总数",
        "假人识别为真人", "未识别数", "未识别率"])
    df3.to_excel(writer, sheet_name='分类统计', index=False)

    results = []
    values = [0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99, 0.999]
    for value in values:
        result = get_live_frr_far(df, 'score', value, 'label')
        results.append([value, *result])

    columns = ["Threshold", "FAR", "FRR", "total",
               "real_num", "frr_num", "photo_num", "far_num", "unknow", "unknow_rate",
               'num_2d', 'far_number_2d', 'far2d',
               'num_3d', 'far_number_3d', 'far3d',
               'num_3d_high', 'far_number_3d_high', 'far3d_high',
               'num_3d_low', 'far_number_3d_low', 'far3d_low']

    df4 = pd.DataFrame(results, columns=columns)
    df4.to_excel(writer, sheet_name='FAR_FRR', index=False)
    writer.save()
    return df1, df2, df3, df4


