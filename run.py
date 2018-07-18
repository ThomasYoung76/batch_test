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
import s_json


PATH_CONFIG = os.path.join(PATH_BASE, 'config.json')    # config.json的路径
output = os.path.join(PATH_BASE, 'output')
file_name = os.path.join(output, 'files.txt')
label_name = os.path.join(output, 'labels.txt')
i_enroll = os.path.join(output, 'i_enroll.txt')
i_real = os.path.join(output, 'i_real.txt')


def init_env():
    print(">>> step 1: {}".format(sys._getframe().f_code.co_name))
    # 环境忙时等待空闲或者直接退出
    while check_process('sample'):
        if not is_wait_env_free:
            sys.exit("Exit. someone is testing. "
                     "please ensure environment is okay first and then try again.")
        else:
            time.sleep(60)


def init_args():
    desc = """ pc端批处理 """
    parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-p', '--test_type', action="store", default='liveness', help=u'测试类型')
    parser.add_argument('-d', '--data_path', action='store', help='数据集目录或者数据集的绝对路径')
    parser.add_argument('-e', action='store', dest='ext', default='yuv', help='文件扩展名，默认为yuv')
    parser.add_argument('-t', action='store', dest='time', default=None, help='执行时间')
    parser.add_argument('-f', action='store', dest='file', help='带执行的文件')
    parser.add_argument('-s', action='store', dest='section', default='', help='过滤部分数据集来执行')
    args = parser.parse_args()

    global test_type, data_path, file_ext, crontab_time, exe_file, section
    test_type, data_path, file_ext, crontab_time, exe_file, section = \
        args.test_type, args.data_path, args.ext, args.time, args.file, args.section


def check_args():
    print(">>> step 2: {}".format(sys._getframe().f_code.co_name))
    if exe_file is not None:
        try:
            assert Path(exe_file).is_file()
        except AssertionError:
            sys.exit("Error. Parameter: {} is not a file".format(exe_file))
        try:
            json.load(open(exe_file))
        except:
            sys.exit("Error. Parameter: {} is not a json file".format(exe_file))
        return None

    # 参数检查
    try:
        assert test_type in types
    except AssertionError:
        sys.exit("Error. Parameter test_type: {} not in {}".format(test_type, types))

    if data_path is None:
        sys.exit("Error. Parameter data_path cannot be None")

    # # 提供简洁的输入data_path的方法
    # if not data_path.startswith('/'):
    #     if file_ext in ['jpg', 'yuv']:
    #         data_path = os.path.join(PATH_DATA_2D, [test_type, data_path])
    #     else:
    #         data_path = file_ext.directory    # 3d数据集查找方法待定

    if not Path(data_path).exists():
        # print()
        sys.exit("Error. Parameter data_path: {} not exists. ".format(data_path))

    if file_ext:
        try:
            assert file_ext in images
        except AssertionError:
            sys.exit("Error. Parameter ext: {} not in {}".format(file_ext, images))

    if crontab_time:
        try:
            datetime.datetime.strptime(crontab_time, "%H:%M")
        except:
            sys.exit("Error. Parameter time: {} is not time data, cannot match format '%H:%M".format(crontab_time))


def get_param():
    pass


def set_config():
    print(">>> step 3: {}".format(sys._getframe().f_code.co_name))
    global data_version
    data_version = Path(data_path).name
    raw_config = Path(data_path).parent / "config" / (data_version + ".json")
    if raw_config.is_file():
        shutil.copy2(raw_config, PATH_CONFIG)


def get_config():
    try:
        with open(PATH_CONFIG) as f:
            configs = f.read()
    except FileNotFoundError as e:
        sys.exit(e)
    search = re.search('{0}.*?(\d+.\d+.\d+)'.format(test_type), configs)
    if not search:
        sys.exit("Error: Can not find version!")
    global version
    version = search.group(1)
    print('{}: {}. testset: {}'.format(test_type, version, data_version))
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


def prepare_data():
    print(">>> step 4: {}".format(sys._getframe().f_code.co_name))

    if not Path(output).exists():
        os.makedirs(output)

    if test_type in ['liveness', 'eyestate']:
        build_liveness_input(data_path, file_type=file_ext, flag=liveness_flag,
                             file_name=file_name, label_name=label_name, filter_=section)
    elif test_type == 'verify':
        build_verify_input(data_path, file_type=file_ext, i_enroll=i_enroll, i_real=i_real, label_name=label_name)
    elif test_type == 'detect':
        build_detect_input(data_path, file_type=file_ext, file_name=file_name)
    else:
        sys.exit("目前只支持跑活体比对，其他批处理方式后续支持")


def execute(command):
    print(">>> step 5: {}".format(sys._getframe().f_code.co_name))

    # 删除原result
    if test_type == 'verify':
        result = "{0}{1}{2}{1}{2}_score_output%i_enroll.txt.csv".format(PATH_BASE, os.sep, test_type)
    else:
        result = "{0}{1}{2}{1}{2}_output%files.txt.csv".format(PATH_BASE, os.sep, test_type)
    if Path(result).exists():
        os.remove(result)

    start = datetime.datetime.now()
    global now
    now = datetime.datetime.strftime(start, '%Y%m%d_%H%M%S')
    new_cmd = 'cd {} && {}'.format(PATH_BASE, command)
    print(new_cmd)
    ret = subprocess.call(new_cmd, shell=True)
    if ret != 0:
        sys.exit("Error. command {} execute failed, see {}.log in {}".format(
            command, test_type, PATH_BASE))
    else:
        pass
    time.sleep(4)   # 等进程起来
    # wait for result
    if not is_wait_finish:
        sys.exit('wait test finish. then see result in {}'.format(
            os.path.join(PATH_CONFIG, test_type)))
    if not Path(result).exists():
        wait_process('sample')
    end = datetime.datetime.now()
    gap = (end - datetime.datetime.strptime(now, '%Y%m%d_%H%M%S')).total_seconds()
    print("Success. elapse time: {}s".format(gap))
    time.sleep(2)
    return result


def optimize_result(raw_result):
    """
    优化结果
    :param raw_result: scores文件
    :param file_name:
    :param label_name:
    :return:
    """
    print(">>> step 6: {}".format(sys._getframe().f_code.co_name))
    result_dir = "{0}{1}result{1}{2}_{3}_{4}".format(PATH_BASE, os.sep, test_type, now, version)
    check_directory(result_dir)
    print("See result in {}".format(result_dir))
    new_result = '{}{}score_{}{}'.format(result_dir, os.sep, data_version, Path(raw_result).suffix)
    try:
        if test_type != 'detect':
            shutil.copyfile(raw_result, new_result)
        else:
            # 检测的dt文件只含文件名
            with open(raw_result, 'r') as rr:
                with open(new_result, 'w') as nr:
                    for line in rr.readlines():
                        if file_ext == 'jpg':
                            nr.write(line.split(os.sep)[-1])
                        if file_ext == 'ir':
                            nr.write(line.split(os.sep)[-1].replace('.ir', '.ir.jpg'))
    except FileNotFoundError as e:
        sys.exit(e)

    shutil.copy2(label_name, result_dir)
    shutil.copy2(PATH_CONFIG, result_dir)

    # 写结果
    final_result = "{0}{1}{2}_result.xlsx".format(result_dir, os.sep, version)
    roc = "{0}{1}{2}-roc.txt".format(result_dir, os.sep, version)
    if test_type == 'liveness':
        shutil.copy2(file_name, result_dir)
        get_liveness_result(new_result, file_name, label_name,
                            score=liveness_score_thres, error_name=final_result)

        # 写roc
        s_roc.cal_roc(raw_result, label_name, roc_name=roc, fprs=fprs)

    if test_type == 'eyestate':
        get_eyestate_result(scores=raw_result, files=file_name, error_name=final_result)

    if test_type == 'verify':
        shutil.copy2(i_real, result_dir)
        shutil.copy2(i_enroll, result_dir)
        s_roc.cal_verify_roc(score_name=raw_result, label_name=label_name, roc_name=roc, fprs=fprs)

        get_verify_result(i_enroll, i_real, new_result,
                          replace_file=data_path.rstrip(os.sep) + os.sep,
                          replace_name=PATH_BASE + '/output/enroll_list/',
                          error_name=final_result,
                          )


def analysis_result(result):
    pass  # 执行完成后分析结果


def main():
    check_args()
    set_config()
    configs = get_config()
    check_config()
    check_data_set()
    prepare_data()
    wait_crontab(crontab_time)
    result = execute(cmd[test_type])
    optimize_result(result)
    analysis_result(result)


if __name__ == "__main__":
    init_env()
    init_args()
    if not exe_file:
        main()
    else:
        # # 处理文件中的参数
        all_id, params, configs = s_json.get_params(exe_file)
        for i in range(len(all_id)):
            d_param = params[i]
            test_type, data_path, file_ext, crontab_time, section = \
                d_param.get('test_type', None), d_param.get('data_path', None), d_param.get('ext', None), \
                d_param.get('time', ''), d_param.get('section', '')
            main()
            time.sleep(2)
