# -*- coding: utf-8 -*-
"""
Created on 2018/7/9

@author: yangshifu
@mail: yangshifu@sensetime.com
"""
import os
import sys
import re
import time
import shutil
from pathlib import Path

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


def get_files(src, file_type="jpg", is_abs=False, filter_=''):
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
    Path(name).mkdir(parents=True, exist_ok=True)


def build_liveness_input(data_path, file_type, flag, file_name, label_name, filter_):
    if file_type == 'gray16':
        file_type = ('_\d\.gray16', '_depth.gray16')
    if file_type == 'ir':
        file_type = ('ir', 'depth')
    if isinstance(file_type, tuple):
        file_0 = get_files(data_path, file_type=file_type[0], is_abs=True, filter_=filter_)
        file_1 = get_files(data_path, file_type=file_type[1], is_abs=True, filter_=filter_)
        file_0.sort(key=lambda x: Path(x).name)
        file_1.sort(key=lambda x: Path(x).name)
        files = concat_list(file_0, file_1, sep=' ')
        labels = get_labels_for_pc(file_0, flag=flag)
    else:
        files = get_files(data_path, file_type=file_type, is_abs=True, filter_=filter_)
        labels = get_labels_for_pc(files, flag=flag)
    list2file(files, file_name)
    list2file(labels, label_name)
    return file_name, label_name


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


def get_liveness_result(scores, files, labels, score=0.95, error_name="live_error.xlsx", version=''):
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

    columns = ["Threshold", "FAR-{}".format(version), "FRR-{}".format(version), "total",
               "real_num", "frr_num", "photo_num", "far_num", "unknow", "unknow_rate",
               'num_2d', 'far_number_2d', 'far2d',
               'num_3d', 'far_number_3d', 'far3d',
               'num_3d_high', 'far_number_3d_high', 'far3d_high',
               'num_3d_low', 'far_number_3d_low', 'far3d_low']

    df4 = pd.DataFrame(results, columns=columns)
    df4.to_excel(writer, sheet_name='FAR_FRR', index=False)
    writer.save()
    return df1, df2, df3, df4


def get_eyestate_result(scores, files, error_name="eye_error.xlsx"):
    df_score = pd.read_csv(scores, sep=' ', engine='c',
                     names=['left_score', 'left_valid', 'right_score', 'right_valid'])
    df_file = pd.read_csv(files, names=['filename'], dtype=np.str)
    df = pd.concat([df_file, df_score], axis=1)
    df_unknow = df[df['left_score'] == -1]
    df_error = df[df['left_score'] == -2]

    df2 = df[df['left_score'] > -1]

    close_error = df2[df2['filename'].str.contains('/close') & ((df2['left_score'] > 9.5) | (df2['right_score'] > 9.5))]
    open_error = df2[df2['filename'].str.contains('/open') & (df2['left_score'] < 9.5) & (df2['right_score'] < 9.5)]

    writer = pd.ExcelWriter(error_name)
    df.to_excel(writer, sheet_name='图片汇总', index=False)
    df_unknow.to_excel(writer, sheet_name='未认识人脸', index=False)
    df_error.to_excel(writer, sheet_name='图片格式错误', index=False)
    close_error.to_excel(writer, sheet_name='闭眼识别为睁眼', index=False)
    open_error.to_excel(writer, sheet_name='睁眼识别为闭眼', index=False)
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
                        else:
                            real.write(os.path.join(root, str(img)))
                            real.write(os.linesep)
                            label_real = np.append(label_real, i)

    with open(label_name, 'w') as label:
        label_enroll.tofile(label, sep=' ')
        print('', file=label)
        label_real.tofile(label, sep=' ')
    return i_enroll, i_real, label_name


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
        print("index: {}   {}".format(person, time.ctime()))
        row = df.loc[str(person)]
        # print(row)
        row.index = [real_photos['person'].astype(str), real_photos['filename']]
        # print(row)
        self = row[str(person)]
        self_nums = self_nums + len(self)
        self_error = self[(self < positive) & (self > -1)]
        for item in self_error.index:
            self_errors.append((item, self_error[item]))
        # print(self_error)
        others = row.drop(person, level=0)
        other_nums = other_nums + len(others)
        other_error = others[others >= negative]
        for item in other_error.index:
            other_errors.append([person, item[1], other_error.loc[item]])
            # print(other_error)

    df_person_errors = pd.DataFrame(self_errors, columns=['filename', 'score'])
    df_other_errors = pd.DataFrame(other_errors, columns=['person', 'filename', 'score'])

    return df_person_errors, df_other_errors, self_nums, other_nums


def get_verify_frr_far(selfs_num, others_num, df_person_errors, df_other_errors, colomn, score):
    frr_num = len(df_person_errors[df_person_errors[colomn] < score])
    far_num = len(df_other_errors[df_other_errors[colomn] > score])
    frr = 0 if not frr_num else frr_num / float(selfs_num)
    far = 0 if not far_num else far_num / float(others_num)
    return (far, frr, selfs_num + others_num, selfs_num, frr_num, others_num, far_num)


def get_verify_result(names, files, scores, replace_file, replace_name="output/enroll_list/",
                      error_name="verify_error.xlsx"):
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
        columns=["Threshold", "FAR", "FRR", "number", "real_number", "frr_number",
                 "no_number", "far_number"])

    df4.to_excel(writer, sheet_name='FAR_FRR', index=False)
    writer.save()


def build_detect_input(data_path, file_type, file_name):
    files = get_files(data_path, file_type=file_type, is_abs=True)
    list2file(files, file_name)


if __name__ == "__main__":
    get_eyestate_result(scores='output_eyestate.csv', files='image_list.txt')