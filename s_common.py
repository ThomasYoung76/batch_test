"""
Created on 2018/7/8

@author: yangshifu
@mail: yangshifu@sensetime.com
"""
import datetime
import subprocess
import time


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
    print("Waiting {} ...".format(name))
    while check_process(name):
        time.sleep(sleep)


def wait_crontab(plan_time):
    """
    一直等到设定的时间，才退出等待
    :param plan_time: 字符串，预定的时间，格式：%H:%M(如08：00）
    :return:
    """
    if plan_time:
        print("test will execute at {}, please waiting ...".format(plan_time))
        execute_time = str_to_time(plan_time)
        while datetime.datetime.now() < execute_time:
            time.sleep(1)
