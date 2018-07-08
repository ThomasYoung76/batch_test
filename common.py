"""
Created on 2018/7/8

@author: yangshifu
@mail: yangshifu@sensetime.com
"""
import os
import shutil
import datetime
import subprocess
import time
from pathlib import Path


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


def str_to_time(str_execute_time):
    """
    format "%H:%M" to datetime
    :param str_execute_time: str , format '%H:%M', eg: "10:00"
    :return:
    """
    start_time = datetime.datetime.now()
    nyear, nmonth, nday = start_time.year, start_time.month, start_time.day
    execute_time = datetime.datetime.strptime("%s-%s-%s %s" % (nyear, nmonth, nday, str_execute_time), "%Y-%m-%d %H:%M")
    # 若设定的执行时间早于当前时间，则天数加1
    if execute_time < datetime.datetime.now():
        execute_time = execute_time + datetime.timedelta(days=1)
    return execute_time


def check_process(name):
    cmd = "ps afx | grep -i '{}' | grep -v grep |wc -l".format(name)
    result = subprocess.check_output(cmd, shell=True)
    return True if int(result.strip()) else False


def wait_process(name, sleep=1):
    print("Waiting " + name)
    while check_process(name):
        time.sleep(sleep)


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


def wait_crontab(plan_time):
    """
    一直等到设定的时间，才退出等待
    :param plan_time: 预定的时间，格式：%H:%M(如08：00）
    :return:
    """
    crontab = True
    while crontab:
        if plan_time:
            execute_time = str_to_time(plan_time)
            while datetime.datetime.now() < execute_time:
                time.sleep(1)
        else:
            crontab = False
