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

from config import *
from common import *


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

    global test_type, data_path, is_wait, file_ext, crontab_time, execute_file

    test_type, data_path, is_wait, file_ext, crontab_time, execute_file = \
        args.test_type, args.data_path, args.wait, args.ext, args.time, args.file

    if execute_file is not None:
        try:
            assert Path(execute_file).is_file()
        except AssertionError:
            sys.exit("Error. Parameter: {} is not a file".format(execute_file))
        try:
            json.load(execute_file)
        except:
            sys.exit("Error. Parameter: {} is not a json file".format(execute_file))
        return None

    # 参数检查
    try:
        assert test_type in ['liveness', 'detect', 'verify']
    except AssertionError:
        sys.exit("Error. Parameter: {} not in ['liveness', 'detect', 'verify']".format(test_type))

    if data_path is None:
        sys.exit("Error. Parameter: data_path cannot be None")

    if not data_path.startswith('/'):
        if args.ext in ['jpg', 'yuv']:
            data_path = os.path.join(PATH_DATA_2D, [test_type, args.directory])
        else:
            data_path = args.directory    # 3d数据集查找方法待定

    if not Path(data_path).exists():
        # print()
        sys.exit("Error. Parameter: {} not exists. ".format(data_path))

    if crontab_time is not None:
        try:
            datetime.datetime.strptime(crontab_time, "%H:%M")
            wait_crontab(crontab_time)
        except:
            sys.exit("Error. Parameter: {} is not time data, cannot match format '%H:%M".format(crontab_time))


def get_param(file_path):

    pass    # 当参数传文件时，改变global里的值


def get_config():
    data_version = Path(data_path).name
    raw_config = Path(data_path).parent / "config" / (data_version + ".json")
    config_name = os.path.join(PATH_BASE, 'config.json')
    if raw_config.is_file():
        shutil.copy2(raw_config, config_name)
    configs = open(config_name).read()
    search = re.search('{0}.*?(\d+.\d+.\d+)'.format(test_type), configs)
    if not search:
        sys.exit("Error: Can not find version!")
    global version
    version = search.group(1)

    print('{} {}'.format(test_type, version))
    return configs


def check_config(config):
    # 检查配置文件，确认模型都存在
    d = json.load(config)
    for item in d['model']:
        model = d['model'][item]
        if not Path(os.path.join(PATH_BASE, model)).exists():
            print("Error. model: {} not exist".format(model))
            sys.exit(0)
    # 检查配置信息是否正确，如jpg的width和hight必须为-1，2d图片的gray为false，读取图片的长宽高是否匹配等
    pass


def check_data_set():
    pass


def remove_result(result_type):
    if result_type == 'detect':
        result = "{0}{1}{2}{1}{2}_output%files.txt.txt".format(
            PATH_BASE, os.sep, result_type)
    else:
        result = "{0}{1}{2}{1}{2}_output%files.txt.csv".format(
            PATH_BASE, os.sep, result_type)

    if result_type == 'verify':
        result = "{0}{1}{2}{1}{2}_score_output%i_enroll.txt.csv".format(
            PATH_BASE, os.sep, result_type)

    if Path(result).exists():
        os.remove(result)
    return result


def execute():
    start = datetime.datetime.now()
    global now
    now = datetime.datetime.strftime(start, '%Y%m%d_%H%M%S')
    cmd = 'cd {} && {}'.format(PATH_BASE, data_set[test_type]['cmd'])
    ret = subprocess.call(cmd, shell=True)
    if ret != 0:
        sys.exit("Error. command {} execute failed, see {}.log in {}".format(data_set[test_type]['cmd'], test_type, PATH_BASE))
    else:
        end = datetime.datetime.now()
        gap = (end - start).total_seconds()
        print("Success. elapse time: {}s".format(gap))


def optimize_result(result):
    result_directory = "{0}{1}result{1}{2}-{3}-{4}".format(PATH_BASE, os.sep, test_type, now, version)
    check_directory(result_directory)
    new_result = "{0}{1}{2}-result.csv".format(result_directory, os.sep, version)
    print(result)
    print(new_result)
    time.sleep(1)
    shutil.copyfile(result, new_result)
    error_name = "{0}{1}{2}----result.xlsx".format(result_directory, os.sep, version)


def main():
    init_args()
    configs = get_config()
    check_config(configs)
    raw_result = remove_result(test_type)
    execute()
    if not is_wait:
        exit(0)
    if not Path(raw_result):
        wait_process('sample')


if __name__ == "__main__":
    main()



# if options.directory is None:
#     if not options.data_type:
#         print("data_type不能为空")
#         exit(1)
#     options.directory = data_set[options.test_type][options.data_type]

# file_name = "{}{}{}".format(tool, os.sep, "output/files.txt")
# label_name = "{}{}{}".format(tool, os.sep, "output/labels.txt")
# config_name = "{}{}{}".format(tool, os.sep, "config.json")
#
# data_version = Path(options.directory).name
# raw_config = Path(options.directory).parent / "config" / (data_version + ".json")
# if raw_config.is_file():
#     shutil.copy2(raw_config, config_name)
#
# # 检查配置文件，确认模型都存在
# d = json.load(open(config_name))
# print('\n{}\n'.format(config_name))
# print('#' * 80)
# print('\n')
# pprint.pprint(d)