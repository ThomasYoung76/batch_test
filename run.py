#!/usr/bin/env python3
"""
Created on 2018/7/8

@author: yangshifu
@mail: yangshifu@sensetime.com
"""
import re
import time
import sys
import argparse
import shutil
import json
import subprocess


from pathlib import Path

from s_config import *
from s_common import *
from s_file import *
import s_roc


PATH_CONFIG = os.path.join(PATH_BASE, 'config.json')    # config.json的路径


def init_args():
    desc = """ pc端批处理 """
    parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-p', '--test_type', action="store", default='liveness', help=u'测试类型')
    parser.add_argument('-d', '--data_path', action='store', help='数据集目录或者数据集的绝对路径')
    parser.add_argument('-w', action="store_true", dest='wait', default=False, help=u'是否等待结束')
    parser.add_argument('-e', action='store', dest='ext', default='', help='文件扩展名，默认为ir')
    parser.add_argument('-t', action='store', dest='time', default=None, help='执行时间')
    parser.add_argument('-f', action='store', dest='file', help='带执行的文件')
    args = parser.parse_args()

    global test_type, data_path, is_wait, file_ext, crontab_time, exe_file
    test_type, data_path, is_wait, file_ext, crontab_time, exe_file = \
        args.test_type, args.data_path, args.wait, args.ext, args.time, args.file


def check_args():
    if exe_file is not None:
        try:
            assert Path(exe_file).is_file()
        except AssertionError:
            sys.exit("Error. Parameter: {} is not a file".format(exe_file))
        try:
            json.load(exe_file)
        except:
            sys.exit("Error. Parameter: {} is not a json file".format(exe_file))
        return None

    # 参数检查
    try:
        assert test_type in ['liveness', 'detect', 'verify']
    except AssertionError:
        sys.exit("Error. Parameter: {} not in ['liveness', 'detect', 'verify']".format(test_type))

    if data_path is None:
        sys.exit("Error. Parameter: data_path cannot be None")

    # # 提供简洁的输入data_path的方法
    # if not data_path.startswith('/'):
    #     if file_ext in ['jpg', 'yuv']:
    #         data_path = os.path.join(PATH_DATA_2D, [test_type, data_path])
    #     else:
    #         data_path = file_ext.directory    # 3d数据集查找方法待定

    if not Path(data_path).exists():
        # print()
        sys.exit("Error. Parameter: {} not exists. ".format(data_path))

    if crontab_time is not None:
        try:
            datetime.datetime.strptime(crontab_time, "%H:%M")
        except:
            sys.exit("Error. Parameter: {} is not time data, cannot match format '%H:%M".format(crontab_time))


def get_param(file_path):
    pass    # 从json文件中获取参数


def set_config():
    global data_version
    data_version = Path(data_path).name
    raw_config = Path(data_path).parent / "config" / (data_version + ".json")
    if raw_config.is_file():
        shutil.copy2(raw_config, PATH_CONFIG)


def get_config():
    configs = open(PATH_CONFIG).read()
    search = re.search('{0}.*?(\d+.\d+.\d+)'.format(test_type), configs)
    if not search:
        sys.exit("Error: Can not find version!")
    global version
    version = search.group(1)
    print('{} {}'.format(test_type, version))
    return configs


def check_config():
    # 检查配置文件，确认模型都存在
    d = json.load(open(PATH_CONFIG))
    for item in d['model']:
        model = d['model'][item]
        if not Path(os.path.join(PATH_BASE, model)).exists():
            print("Error. model: {} not exist".format(model))
            sys.exit(0)
    # 检查配置信息是否正确，如jpg的width和hight必须为-1，2d图片的gray为false，读取图片的长宽高是否匹配等
    pass


def check_data_set():
    pass


def get_result_name():
    if test_type == 'detect':
        result = "{0}{1}{2}{1}{2}_output%files.txt.txt".format(
            PATH_BASE, os.sep, test_type)
    else:
        result = "{0}{1}{2}{1}{2}_output%files.txt.csv".format(
            PATH_BASE, os.sep, test_type)

    if test_type == 'verify':
        result = "{0}{1}{2}{1}{2}_score_output%i_enroll.txt.csv".format(
            PATH_BASE, os.sep, test_type)

    if Path(result).exists():
        os.remove(result)
    return result


def prepare_data():
    # 暂时只支持liveness
    file_name = "{}{}{}".format(PATH_BASE, os.sep, "output/files.txt")
    label_name = "{}{}{}".format(PATH_BASE, os.sep, "output/labels.txt")
    if file_ext:
        data_set[test_type]['file_type'] = file_ext
    ext = data_set[test_type]['file_type']
    if test_type == 'liveness':
        files = get_files(data_path, file_type=ext, is_abs=True)
        labels = get_labels_for_pc(files, flag=data_set[test_type]['flag'])
    else:
        sys.exit("目前只支持跑活体，其他批处理方式后续支持")
    list2file(files, file_name)
    list2file(labels, label_name)
    return file_name, label_name


def execute():
    start = datetime.datetime.now()
    global now
    now = datetime.datetime.strftime(start, '%Y%m%d_%H%M%S')
    cmd = 'cd {} && {}'.format(PATH_BASE, data_set[test_type]['cmd'])
    print(cmd)
    ret = subprocess.call(cmd, shell=True)
    if ret != 0:
        sys.exit("Error. command {} execute failed, see {}.log in {}".format(data_set[test_type]['cmd'], test_type, PATH_BASE))
    else:
        pass
    time.sleep(3)   # 等进程起来
    # wait for result
    if not is_wait:
        exit(0)


def optimize_result(raw_result, file_name, label_name):
    result_dir = "{0}{1}result{1}{2}_{3}_{4}".format(PATH_BASE, os.sep, test_type, now, version)
    check_directory(result_dir)
    print("See result in {}".format(result_dir))
    new_result = '{}{}score_{}{}'.format(result_dir, os.sep, data_version, Path(raw_result).suffix)
    try:
        shutil.copyfile(raw_result, new_result)
    except FileNotFoundError as e:
        sys.exit(e)
    shutil.copy2(file_name, result_dir)
    shutil.copy2(label_name, result_dir)
    shutil.copy2(PATH_CONFIG, result_dir)

    # 写结果
    final_result = "{0}{1}{2}_result.xls".format(result_dir, os.sep, version)
    df1, df2, df3, df4 = get_liveness_server_result(
        new_result, file_name, label_name,
        replace='', error_name=final_result)

    # 写roc
    roc = "{0}{1}{2}-roc.txt".format(result_dir, os.sep, version)
    s_roc.cal_roc(raw_result, label_name, roc_name=roc, fprs=fprs)


def analysis_result(result):
    pass  # 执行完成后分析结果


def main():
    init_args()
    check_args()
    set_config()
    configs = get_config()
    check_config()
    raw_result = get_result_name()
    file_path, label_path = prepare_data()
    wait_crontab(crontab_time)
    execute()
    if not Path(raw_result).exists():
        wait_process('sample')

    end = datetime.datetime.now()
    gap = (end - datetime.datetime.strptime(now, '%Y%m%d_%H%M%S')).total_seconds()
    print("Success. elapse time: {}s".format(gap))

    optimize_result(raw_result, file_path, label_path)


if __name__ == "__main__":
    main()
