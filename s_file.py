# -*- coding: utf-8 -*-
"""
Created on 2018/7/9

@author: yangshifu
@mail: yangshifu@sensetime.com
"""
import os
import sys
import re
import json
import time
import shutil
import csv
from pathlib import Path
import functools
import argparse

import numpy as np
import pandas as pd


def list2file(result, file_name, first_row=None):
    """ 将列表存入文件 """
    with open(file_name, 'w') as f:
        if first_row is not None:
            f.write('{}\n'.format(first_row))
        for row in result:
            f.write('{}\n'.format(row))


def concat_list(list1, list2, sep=' '):
    try:
        assert len(list1) == len(list2)
    except:
        sys.exit("length of {} is :{}, but length of {} is：{}. the length of two list must be same".format(
            list1, len(list1), list2, len(list2)
        ))
    result = []
    for i in range(len(list1)):
        result.append("{}{}{}".format(list1[i], sep, list2[i]))
    return result


def get_files(src, file_type="jpg", is_abs=True, filter_='', is_multi_frame=False, is_line_sep=False):
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
    for file_name in p.rglob("*{}".format(file_type)):
        if '/Enroll/' in str(file_name):
            continue
        if not is_abs:
            file_name = file_name.relative_to(src)
        else:
            file_name = file_name.absolute()

        # 增加判断文件大小是否为0的逻辑
        if not os.path.getsize(file_name):
            print("Warning: file's size is zero. file path: {}".format(file_name))
            continue

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

    # 如果连续两个文件不在同一目录，则用空格分开, (多帧策略要求）
    if is_multi_frame:
        dirs = list(map(lambda x: os.path.dirname(x), files))
        space_count = 0
        for i, d in enumerate(dirs):
            if i == 0:
                continue
            if dirs[i] != dirs[i-1]:
                files.insert(i+space_count, '')
                space_count += 1

    # 每行之间加空行，用多帧模型跑单帧策略时文件列表采用这种方式
    if is_line_sep:
        linenum = 1
        length_files = len(files)
        for i in range(length_files):
            files.insert(i + linenum, is_line_sep)
            linenum += 1
    return files


def get_labels_for_clean(files):
    """获取用于清洗的labels，适用于工具
    http://gitlab.bj.sensetime.com/face-recognition/testsets_autoclean"""
    labels = []
    for f in files:
        labels.append(f.split(os.sep)[0])
    return labels


def get_labels_for_pc(files, flag='human_test'):
    """
    获取文件列表对应的labels
    :param files: 文件列表
    :param flag: 活体真人标志， 睁闭眼假人标识
    :return:
    """
    labels = []
    for f in files:
        # 忽略空行
        if not f:
            continue
        if isinstance(flag, str):
            # 真人为0，假人为1, 睁闭眼里睁眼是1，闭眼是0
            if flag.lower() in f.lower():
                labels.append(0)
            else:
                labels.append(1)
        else:
            if any(list(filter(lambda x: x.lower() in f.lower(), flag))):
                labels.append(0)
            else:
                labels.append(1)
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
    Path(name).mkdir(parents=True, exist_ok=True)


def build_liveness_input(data_path, file_type, flag, file_name, label_name, filter_,
                         is_multi_frame=False, is_line_sep=False):
    if file_type == 'gray16':
        file_type = ('_\d\.gray16', '_depth.gray16')
    if file_type == 'ir':
        file_type = ('ir', 'depth')
    if isinstance(file_type, tuple):
        file_0 = get_files(data_path, file_type=file_type[0], is_abs=True, filter_=filter_)
        file_1 = get_files(data_path, file_type=file_type[1], is_abs=True, filter_=filter_)
        file_0.sort(key=lambda x: Path(x).name)
        file_1.sort(key=lambda x: Path(x).name)
        if file_1:
            files = concat_list(file_0, file_1, sep=' ')
        else:
            files = file_0
        labels = get_labels_for_pc(file_0, flag=flag)
    else:
        files = get_files(data_path, file_type=file_type, is_abs=True, filter_=filter_,
                          is_multi_frame=is_multi_frame, is_line_sep=is_line_sep)
        labels = get_labels_for_pc(files, flag=flag)
    list2file(files, file_name)
    list2file(labels, label_name)


def build_eyestate_input(data_path, file_type, flag, file_name, label_name, filter_,
                         is_multi_frame=False, is_line_sep=False):

    files = get_files(data_path, file_type=file_type, is_abs=True, filter_=filter_,
                      is_multi_frame=is_multi_frame, is_line_sep=is_line_sep)
    labels = get_labels_for_pc(files, flag=flag)
    list2file(files, file_name)
    list2file(labels, label_name)


def get_live_frr_far(df, colomn1, score, colomn2, column_filename='filename'):
    total = len(df)
    # print(df.head())
    unknow = len(df[df[colomn1] == -1])
    # df = df[df[colomn1] != -1]
    real_number = len(df[df[colomn2] == 0])
    photo_number = len(df[df[colomn2] == 1])

    # 真人识别为假人
    frr_number = len(df.loc[((df[colomn1] > score) | (df[colomn1] == -1)) & (df[colomn2] == 0) & (df[colomn1] <= 1)])
    # 假人识别为真人
    far_number = len(df.loc[(df[colomn1] < score) & (df[colomn1] > 0) & (df[colomn2] == 1)])

    frr = 0 if not real_number else frr_number / float(real_number)

    far = 0 if not photo_number else far_number / float(photo_number)
    return (far, frr, total, real_number, frr_number, photo_number, far_number,
            unknow, unknow / float(total))


def get_liveness_result(scores, files, labels, error_name, score_thres=0.95, version=''):
    def rename(name):
        type_ = os.path.dirname(name.split()[-1])
        return type_

    df_score = pd.read_csv(scores, header=None, names=['score'], engine='c',
                           na_filter=False, low_memory=False)
    df_file = pd.read_csv(files, header=None, names=['filename'])
    df_label = pd.read_csv(labels, header=None, names=['label'], engine='c',
                           na_filter=False, low_memory=False)

    df = pd.concat([df_label, df_score, df_file], axis=1)
    df['type'] = df['filename'].apply(rename)

    results = []

    for name, group in df.groupby('type'):
        result = get_live_frr_far(group, 'score', score_thres, 'label')
        results.append([name, *result[:9]])

    for name, group in df.groupby('label'):
        result = get_live_frr_far(group, 'score', score_thres, 'label')
        results.append([name, *result[:9]])

    # 真人识别为假人，包括真人中为检测到人脸的照片
    df1 = df.loc[((df['score'] > score_thres) | (df['score'] == -1)) & (df['label'] == 0)]
    # 假人识别为真人
    df2 = df.loc[((df['score'] > 0) & (df['score'] < score_thres) & (df['label'] == 1))]
    # 分数小于0的图片
    df_except = df.loc[df['score'] < 0]
    result = get_live_frr_far(df, 'score', score_thres, 'label')
    results.append(["All", *result[:9]])
    writer = pd.ExcelWriter(error_name)
    df1.to_excel(writer, sheet_name='真人识别为假人', index=False)
    df2.to_excel(writer, sheet_name='假人识别为真人', index=False)
    df_except.to_excel(writer, sheet_name="分数异常", index=False)

    # print(results)
    df3 = pd.DataFrame(results, columns=[
        "类别", "far", "frr", "总数", "真人总数", "真人识别为假人", "假人总数",
        "假人识别为真人", "未识别数", "未识别率"])
    df3.to_excel(writer, sheet_name='分类统计', index=False)

    results = []
    values = [0.84, 0.85, 0.86, 0.87, 0.88, 0.89, 0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99, 0.999]
    for value in values:
        result = get_live_frr_far(df, 'score', value, 'label')
        results.append([value, *result])

    columns = ["Threshold", "FAR-{}".format(version), "FRR-{}".format(version), "total",
               "real_num", "frr_num", "photo_num", "far_num", "unknow", "unknow_rate",]

    df4 = pd.DataFrame(results, columns=columns)
    df4.to_excel(writer, sheet_name='FAR_FRR', index=False)
    writer.save()
    return df1, df2, df3, df4


def get_liveness_result_for_multi_frame(scores, files, error_name='', flag='human_test', score_thres=0.95, version=''):
    results = []
    df_file = pd.read_csv(files, header=None, names=['filename'])
    df_file['path'] = df_file['filename'].apply(lambda x: os.path.dirname(x.split()[-1]))
    df_file.drop(labels=['filename'], axis=1, inplace=True)
    df_file.drop_duplicates(inplace=True)

    np_file = np.array(df_file['path'])
    df_file = pd.DataFrame(data=np_file, columns=['path'], index=np.arange(len(df_file)))

    # 重新生成labels
    labels = get_labels_for_pc(np_file, flag=flag)
    df_label = pd.DataFrame(data=labels, columns=['label'])

    final_scores = []  # 多帧逻辑时，每一个序列保存一个最低的score
    sequence = []  # 处理每次解锁的一个序列的score
    with open(scores, 'r') as csv_f:
        content = csv.reader(csv_f)
        for item in content:
            if item:
                if float(item[0]) < 0:
                    item[0] = 100
                sequence.append(item[0])
            else:
                final_scores.append(min(list(map(lambda x: float(x), sequence))))
                sequence = []
        if sequence:
            final_scores.append(min(list(map(lambda x: float(x), sequence))))

    rows = len(final_scores)        # 解锁次数
    df_score = pd.DataFrame(final_scores, columns=['score'])
    print(df_score.shape)

    df = pd.concat([df_score, df_file, df_label], axis=1)

    for name, group in df.groupby('path'):
        result = get_live_frr_far(group, 'score', score_thres, 'label', column_filename='path')
        results.append([name, *result[:9]])

    for name, group in df.groupby('label'):
        result = get_live_frr_far(group, 'score', score_thres, 'label', column_filename='path')
        results.append([name, *result[:9]])

   # 真人识别为假人
    df1 = df.loc[((df['score'] > score_thres) & (df['label'] == 0))]
    # 假人识别为真人
    df2 = df.loc[((df['score'] < score_thres) & (df['label'] == 1))]
    result = get_live_frr_far(df, 'score', score_thres, 'label', column_filename='path')
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
    values = [0.84, 0.85, 0.86, 0.87, 0.88, 0.89, 0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99, 0.999]
    for value in values:
        result = get_live_frr_far(df, 'score', value, 'label', column_filename='path')
        results.append([value, *result])

    columns = ["Threshold", "FAR-{}".format(version), "FRR-{}".format(version), "total",
               "real_num", "frr_num", "photo_num", "far_num", "unknow", "unknow_rate",
               'num_2d', 'far_number_2d', 'far2d',
               'num_3d', 'far_number_3d', 'far3d',
               'num_3d_high', 'far_number_3d_high', 'far3d_high',
               'num_3d_low', 'far_number_3d_low', 'far3d_low']

    df4 = pd.DataFrame(results, columns=columns)
    df4.to_excel(writer, sheet_name='FAR_FRR', index=False)
    writer.save()


def get_eye_result(scores, files, open_thres, valid_thres, open_flag='/open', close_flag='/close', error_name="eye_error.xlsx", version=''):
    """
    scores文件的分数：左眼open，左眼valid，右眼open，右眼valid，左眼状态，右眼状态（0是闭眼）。后两个仅在use_sequence时输出。
    :param scores:
    :param files:
    :param open_thres:
    :param valid_thres:
    :param error_name:
    :return:
    """
    df_score = pd.read_csv(scores, delimiter='\s+', engine='c',
                     names=['left_score', 'left_valid', 'right_score', 'right_valid'], header=None)
    df_file = pd.read_csv(files, names=['filename'], dtype=np.str)
    df = pd.concat([df_file, df_score], axis=1)

    df_undetect = df[df['left_score'] == -1]

    # df = df[df['left_score'] > -1 | df['right_score'] > -1]

    total_close = df[df['filename'].str.contains(close_flag)]

    total_open = df[df['filename'].str.contains(open_flag)]

    # 闭眼误认为睁眼
    close_error = df[df['filename'].str.contains(close_flag) & (
                      ((df['left_score'] > open_thres) & (df['left_valid'] > valid_thres)) |
                      ((df['right_score'] > open_thres) & (df['right_valid'] > valid_thres)))]
    # 睁眼误认为闭眼
    open_error = df[df['filename'].str.contains(open_flag) &
                     ((df['left_score'] < open_thres) | (df['left_valid'] < valid_thres)) &
                    ((df['right_score'] < open_thres) | (df['right_valid'] < valid_thres))]

    # 计算frr和far
    far_frr = [[open_thres, len(close_error) / len(total_close), len(open_error) / len(total_open), len(df),
                len(total_open), len(total_close), len(df_undetect), len(close_error), len(open_error)]]

    columns = ["Threshold", "FAR-{}".format(version), "FRR-{}".format(version), "total", "total_open", "total_close", "undetect",
               "far_num", "frr_num"]

    df_far_frr = pd.DataFrame(far_frr, columns=columns)

    writer = pd.ExcelWriter(error_name)
    df.to_excel(writer, sheet_name='图片汇总', index=False)
    df_undetect.to_excel(writer, sheet_name='未检测到人脸', index=False)
    close_error.to_excel(writer, sheet_name='闭眼识别为睁眼', index=False)
    open_error.to_excel(writer, sheet_name='睁眼识别为闭眼', index=False)
    df_far_frr.to_excel(writer, sheet_name='far-frr', index=False)
    writer.save()


def get_eye_result_for_multi_frame(scores, files, open_flag, close_flag, error_name, open_thres, valid_thres, version=''):
    results = []
    df_file = pd.read_csv(files, header=None, names=['filename'])
    df_file['path'] = df_file['filename'].apply(lambda x: os.path.dirname(x.split()[-1]))
    df_file.drop(labels=['filename'], axis=1, inplace=True)
    df_file.drop_duplicates(inplace=True)

    np_file = np.array(df_file['path'])
    df_file = pd.DataFrame(data=np_file, columns=['path'], index=np.arange(len(df_file)))

    # 重新生成labels
    labels = get_labels_for_pc(np_file, flag=open_flag)
    df_label = pd.DataFrame(data=labels, columns=['label'])

    final_scores = []  # 多帧逻辑时，活体每一个序列保存一个最低的score，睁闭眼则保存睁眼的score或最后一个score
    sequence = []  # 处理每次解锁的一个序列的score
    with open(scores, 'r') as csv_f:
        content = csv.reader(csv_f)
        for item in content:
            if item:
                sequence.append(item[0].split(' ')[:-1])
            else:
                # 分数的最后两列只要有1个值为1，即判断为睁眼，放入final_scores，否则将序列最后一个分数放入final_scores
                break_flag = False
                for seq in sequence:
                    if seq[-1] == 1 or seq[-2] == 1:
                        final_scores.append(seq)
                        break_flag = True
                        break
                if not break_flag:
                    final_scores.append(sequence[-1])
                sequence = []
        # 处理最后一个sequence
        if sequence:
            break_flag = False
            for seq in sequence:
                if seq[-1] == 1 or seq[-2] == 1:
                    final_scores.append(seq)
                    break_flag = True
                    break
            if not break_flag:
                final_scores.append(sequence[-1])

    # 转换str为float
    scores = []
    for score in final_scores:
        scores.append(list(map(lambda x: float(x), score)))
    final_scores = scores

    rows = len(final_scores)  # 解锁次数
    df_score = pd.DataFrame(final_scores, columns=['left_score', 'left_valid', 'right_score', 'right_valid',
                                                   'left_open', 'right_open'])

    df = pd.concat([df_score, df_file, df_label], axis=1)

    # df_unknow = df[(df['left_open'] == -1) & (df['right_open'] == -1)]
    # df_error = df[df['left_score'] == -2]

    # df2 = df[(df['left_open'] > -1) & (df['right_open'] > -1)]
    df2 = df
    close_error = pd.DataFrame(columns=df.columns)
    if isinstance(close_flag, (list, tuple)):
        for close in close_flag:
            df_error = df2[df2['path'].str.contains(close) & ((df2['left_open'] == 1) | (df2['right_open'] == 1))]
            close_error = pd.concat([close_error, df_error])
    open_error = pd.DataFrame(columns=df.columns)
    if isinstance(open_flag, (list, tuple)):
        # bug, for循环把open_error重置了
        for o in open_flag:
            df_error = df2[df2['path'].str.contains(o) & (df2['left_open'] != 1) & (df2['right_open'] != 1)]
            open_error = pd.concat([open_error, df_error], axis=0)

    columns = ["Threshold", "FAR-{}".format(version), "FRR-{}".format(version), "total",
               "far_num", "frr_num"]

    far_frr = [[open_thres, len(close_error) / rows, len(open_error) / rows, rows, len(close_error), len(open_error)]]
    df_far_frr = pd.DataFrame(far_frr, columns=columns)

    writer = pd.ExcelWriter(error_name)
    df.to_excel(writer, sheet_name='图片汇总', index=False)
    # df_unknow.to_excel(writer, sheet_name='未认识人脸', index=False)
    # df_error.to_excel(writer, sheet_name='图片格式错误', index=False)
    close_error.to_excel(writer, sheet_name='闭眼识别为睁眼', index=False)
    open_error.to_excel(writer, sheet_name='睁眼识别为闭眼', index=False)
    df_far_frr.to_excel(writer, sheet_name='far-frr', index=False)
    writer.save()


def build_verify_input(data_path, file_type, i_enroll, i_real, label_name):
    people = {}
    output = os.path.dirname(i_real)
    enroll_list = os.path.join(output, 'enroll_list')

    if not os.path.exists(enroll_list):
        os.makedirs(enroll_list)

    if file_type == 'gray16':
        file_type = '_\d\.gray16'

    p = Path(data_path).absolute()
    root = str(p)

    for path_person in p.glob('*'):
        person = path_person.name
        people[person] = list(path_person.rglob('*.{0}'.format(file_type)))

    label_enroll = np.array([], dtype=int)
    label_real = np.array([], dtype=int)

    with open(i_enroll, 'w') as enroll:
        with open(i_real, 'w') as real:
            for i, key in enumerate(people.keys()):
                # enroll.write("{}/{}".format(enroll_list.rstrip(os.sep), key))
                enroll.write(os.path.join(enroll_list, key))
                enroll.write(os.linesep)
                label_enroll = np.append(label_enroll, i)
                with open(os.path.join(enroll_list, key), 'w') as roll:
                    for img in people[key]:
                        if '/enroll/' in str(img).lower():
                            roll.write(os.path.join(root, str(img)))
                            roll.write(os.linesep)
                        elif '/hack/' in str(img).lower():
                            continue
                        else:
                            real.write(os.path.join(root, str(img)))
                            real.write(os.linesep)
                            label_real = np.append(label_real, i)

    with open(label_name, 'w') as label:
        label_enroll.tofile(label, sep=' ')
        print('', file=label)
        label_real.tofile(label, sep=' ')


def load_verify_server_result(names, files, scores, replace_file, replace_name="output/enroll_list/"):
    real_photos = pd.read_csv(files, names=['filename'])
    real_photos['filename'] = real_photos['filename'].apply(
        lambda x: x.replace(replace_file, ''))
    real_photos['person'] = real_photos['filename'].apply(
        lambda x: x.split('/')[0])

    persons = pd.read_csv(names, names=['person'])
    persons['person'] = persons['person'].apply(
        lambda x: x.replace(replace_name, ''))

    score = np.fromfile(scores, dtype=np.float32)
    score = score.reshape(len(persons), len(real_photos))
    df = pd.DataFrame(score, columns=real_photos['filename'])
    df.index = persons['person']
    return df, real_photos


def get_verify_errors(df, real_photos, positive=0.7, negative=0.7):
    other_errors = []
    self_errors = []
    self_nums = 0
    other_nums = 0
    for person in df.index:
        print("index: {}   {}".format(person, time.ctime()), end='\r')
        row = df.loc[str(person)]
        # print(row)
        row.index = [real_photos['person'].astype(str), real_photos['filename']]
        # print(row)
        self = row[str(person)]
        self_detect = self[self > -1]           # 去除未检测人脸的图
        self_nums = self_nums + len(self_detect)       # self_nums去除未检测人脸的图
        self_error = self[(self < positive) & (self > -1)]
        for item in self_error.index:
            self_errors.append((item, self_error[item]))
        others = row.drop(person, level=0)
        others_detect = others[others > -1]          # 去除未检测人脸的图
        other_nums = other_nums + len(others_detect)       # others_detect去除未检测人脸的图
        other_error = others[others >= negative]
        for item in other_error.index:
            other_errors.append([person, item[1], other_error.loc[item]])

    df_person_errors = pd.DataFrame(self_errors, columns=['filename', 'score'])
    df_other_errors = pd.DataFrame(other_errors, columns=['person', 'filename', 'score'])

    return df_person_errors, df_other_errors, self_nums, other_nums


def get_verify_frr_far(selfs_num, others_num, df_person_errors, df_other_errors, colomn, score):
    frr_num = len(df_person_errors[df_person_errors[colomn] < score])
    far_num = len(df_other_errors[df_other_errors[colomn] > score])
    frr = 0 if not frr_num else frr_num / float(selfs_num)
    far = 0 if not far_num else far_num / float(others_num)
    return far, frr, selfs_num + others_num, selfs_num, frr_num, others_num, far_num


def get_verify_result(names, files, scores, replace_file, replace_name="output/enroll_list/",
                      error_name="verify_error.xlsx", version=''):
    df, real_photos = load_verify_server_result(names, files, scores, replace_file=replace_file,
                                                replace_name=replace_name)

    df.to_csv("scores.csv")

    df_person_errors, df_other_errors, selfs_num, others_num = \
        get_verify_errors(df, real_photos, positive=0.9, negative=0.7)

    writer = pd.ExcelWriter(error_name)
    df_person_errors.to_excel(writer, sheet_name='本人识别分值低于0.9', index=False)
    df_other_errors.to_excel(writer, sheet_name='他人识别高于0.7', index=False)

    values = [0.70, 0.71, 0.72, 0.73, 0.74, 0.75, 0.76, 0.77, 0.78, 0.79, 0.80,
              0.81, 0.82, 0.83, 0.84, 0.85, 0.86, 0.87, 0.88, 0.89, 0.90]

    results = []
    for value in values:
        result = get_verify_frr_far(selfs_num, others_num, df_person_errors, df_other_errors, 'score', value)
        results.append([value, *result])

    df4 = pd.DataFrame(
        results,
        columns=["Threshold", "FAR-{}".format(version), "FRR-{}".format(version), "number", "real_number", "frr_number",
                 "no_number", "far_number"])

    df4.to_excel(writer, sheet_name='FAR_FRR', index=False)
    writer.save()


def build_detect_input(data_path, file_type, file_name):
    files = get_files(data_path, file_type=file_type, is_abs=True)
    list2file(files, file_name)


def analysis_detect_result(all_result, report_file, final_result_name):
    all_report = {}
    for result in all_result:
        if 'detect' in result:
            detect_version = re.search('\d+\.\d+\.\d+', result).group()
            try:
                resize = re.search('resize\d+', result).group()
            except:
                resize = ''
            title = '{}_{}'.format(detect_version, resize)
            report_name = Path(result) / report_file
            report = report_name.read_text()
            all_report[title] = report
    # analysis_result = 'result_{}'.format(Path(exe_file).name)
    json.dump(all_report, open(final_result_name, 'w'), indent=4, separators=(',', ':'))


def analysis_verify_result(all_result, list_id, ana_result_dir):
    """
    分析比对结果
    :param all_result:
    :param list_id: 存在相同的命令id值的序列
    :param result_dir: 最终分析结果的目录
    :return:
    """
    if not Path(ana_result_dir).is_dir:
        os.makedirs(ana_result_dir)
    # key为id， value为空列表，用于存放结果
    cmp_result = dict(zip(list_id, [[]]*len(list_id)))
    for result in all_result:
        val_id = re.search('_id(\d+)_', result).group(1)
        version = re.search('\d+\.\d+\.\d+', result)
        if int(val_id) not in list_id:
            continue
        # 拷贝roc
        roc_file = str(list(Path(result).glob("*roc*"))[0])
        shutil.move(roc_file, ana_result_dir)

        # 结果汇总
        result_file = str(list(Path(result).glob("*.xlsx"))[0])
        df_far_frr = pd.read_excel(result_file, sheet_name='FAR_FRR', engine='xlsx',
                                usecols=['Threshold', 'FAR-{}'.format(version), 'FRR-{}'.format(version)])
        cmp_result[int(val_id)].append(df_far_frr)

    for val in list_id:
        df_result = functools.reduce(lambda a, b: a + b, cmp_result[val])
        csv_result_name = os.path.join(ana_result_dir, 'id{}_far_frr.csv'.format(val))
        df_result.to_csv(csv_result_name, index=False)


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="test", formatter_class=argparse.RawTextHelpFormatter)
    # parser.add_argument('-d', dest='dataset', action="store", help="数据集路径")
    # parser.add_argument('-s', dest='score', action="store", default='score_2.6.42.5-snpe.csv', help="score分数文件")
    # parser.add_argument('-f', dest='file', action='store', default='files.txt', help='数据集的文件列表')
    # args = parser.parse_args()
    # # get_liveness_result_for_multi_frame(args.score, args.file, error_name='result_2.6.42.5.xlsx')
    # get_files(args.dataset, file_type='gray16')
    # 活体
    raw_result = "liveness_files_liveness_7.47.1.txt.csv"
    file_name = "files_liveness.txt"
    label_name = "liveness_label.txt"
    final_result = "v2.6.50.xlsx"
    version = ""
    get_liveness_result(raw_result, file_name, label_name, score_thres=0.95,
                        error_name=final_result, version=version)

    # 写roc
    import s_roc

    roc = "liveness_roc.txt"
    fprs = [10 ** (-p) for p in np.arange(1, 7, 1.)]
    s_roc.cal_roc(raw_result, label_name, roc_name=roc, fprs=fprs)
