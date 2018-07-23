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


cwd_dir = os.path.dirname(os.path.abspath(__file__))
PATH_CONFIG = os.path.join(PATH_BASE, 'config.json')    # config.json的路径
output = os.path.join(PATH_BASE, 'output')
file_name = os.path.join(output, 'files.txt')
label_name = os.path.join(output, 'labels.txt')
i_enroll = os.path.join(output, 'i_enroll.txt')
i_real = os.path.join(output, 'i_real.txt')
whole_result = []   # 存储全部结果的路径
info = {}       # 存储模型等信息，如ip、resize大小、命令id等

desc = """pc端批处理测试, 
支持测试类型：{test}
支持图片类型：{image}
使用方法示例：
1. 活体批处理
./run.py -p liveness -d ~/code/data/testset/2d/liveness/v2.6.41 -e yuv

2. 凌晨2点钟跑比对批处理
./run.py -p verify -d ~/code/data/testset/2d/verify/base_China500 -e jpg -t 02:00

3. 从测试集中筛选部分数据跑活体批处理
./run.py -p verify -d ~/code/data/LivenessLibDataxiaomi -e ir -s xiaomi_shifu      # 跑xiaomi_shifu目录的数据
# 跑xiaomi_shifu和xiaomi_20180528的数据
./run.py -p verify -d ~/code/data/LivenessLibDataxiaomi -e ir -s xiaomi_shifu:xiaomi_20180528   
# 跑xiaomi_shifu和路径中包含2D的xiaomi_20180528的数据
./run.py -p verify -d ~/code/data/LivenessLibDataxiaomi -e ir -s xiaomi_shifu:2D.*?xiaomi_20180528

4. 通过文件来执行多项批处理测试
./run.py -f input/liveness.json         # liveness.json可配置多个批处理任务，按id值从小到大的顺序执行测试任务

""".format(test=types, image=images)


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
    parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-p', dest='test_type', action="store", default='liveness', help="测试类型")
    parser.add_argument('-d', dest='data_path', action='store', help='数据集目录或者数据集的绝对路径')
    parser.add_argument('-e', action='store', dest='ext', default='yuv', help='文件类型，默认为yuv')
    parser.add_argument('-t', action='store', dest='time', default=None, help='执行时间，格式类似"10:00"')
    parser.add_argument('-f', action='store', dest='file', help='通过json文件来执行，配置该参数，则其他参数均忽略')
    parser.add_argument('-s', action='store', dest='section', default='', help='过滤部分数据集来执行')
    args = parser.parse_args()

    global test_type, data_path, file_ext, crontab_time, exe_file, section
    test_type, data_path, file_ext, crontab_time, exe_file, section = \
        args.test_type, args.data_path, args.ext, args.time, args.file, args.section


def check_args():
    print(">>> step 2: {}".format(sys._getframe().f_code.co_name))
    print("test_type: {}. data_version: {}。 file_ext: {}. exe_time: {}. exe_file: {}. exe_section:{}".format(
        test_type, Path(data_path).name, file_ext, crontab_time, exe_file, section)
    )
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


def set_config_by_id(id_=None):
    print(">>> step 3: {}".format(sys._getframe().f_code.co_name))
    global data_version
    data_version = Path(data_path).name
    raw_config = Path(data_path).parent / "config" / (data_version + ".json")
    if raw_config.is_file():
        shutil.copy2(raw_config, PATH_CONFIG)

    # 根据id_值来修改config文件
    if id_ is not None:
        s_json.left_join_json(PATH_CONFIG, exe_file, id_=id_)
        info['id'] = id_

    # 获取版本号
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


def check_config():
    # 检查配置文件，确认模型都存在
    d = json.load(open(PATH_CONFIG))
    for item in d['model']:
        model = d['model'][item]
        if not Path(os.path.join(PATH_BASE, model)).exists():
            print("Error. model: {} not exist".format(model))
            sys.exit(0)
    # 记录resize信息
    info['resize'] = d.get('force_resize_max')
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


def optimize_result(raw_result, id_=None):
    """
    优化结果
    :param raw_result: scores文件
    :param id_: 命令id
    :return:
    """
    print(">>> step 6: {}".format(sys._getframe().f_code.co_name))
    # 创建output目录
    if not Path(output).is_dir():
        os.makedirs(output)
    size = info.get('resize', 0)
    resize_info = '_resize{}'.format(size) if size else ''
    int_id = info.get('id', None)
    id_info = '_id{}'.format(int_id) if int_id is not None else ''
    result_dir = "{0}{1}result{1}{2}{3}_{4}_{5}{6}".format(
        PATH_BASE, os.sep, test_type, id_info, now, version, resize_info)
    check_directory(result_dir)
    print("See result in {}".format(result_dir))
    new_result = '{}{}score_{}{}'.format(result_dir, os.sep, data_version, Path(raw_result).suffix)
    try:
        if test_type != 'detect':
            shutil.copyfile(raw_result, new_result)
            shutil.copy2(label_name, result_dir)
        else:
            # 检测的dt文件只含文件名，保持和gt对应
            with open(raw_result, 'r') as rr:
                with open(new_result, 'w') as nr:
                    for line in rr.readlines():
                        if file_ext == 'jpg':
                            nr.write(line.split(os.sep)[-1])
                        if file_ext == 'ir':
                            nr.write(line.split(os.sep)[-1].replace('.ir', '.ir.jpg'))
    except FileNotFoundError as e:
        sys.exit(e)

    shutil.copy2(PATH_CONFIG, result_dir)

    # 写结果
    final_result = "{0}{1}{2}_result.xlsx".format(result_dir, os.sep, version)
    roc = "{0}{1}{2}-roc.txt".format(result_dir, os.sep, version)
    if test_type == 'liveness':
        shutil.copy2(file_name, result_dir)
        get_liveness_result(new_result, file_name, label_name, score=liveness_score_thres,
                            error_name=final_result, version=version)

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
                          error_name=final_result,)
    if test_type == 'detect':
        if file_ext in ['yuv', 'jpg', 'png']:
            gt_file = gt_rgb
        else:
            gt_file = gt_ir
        cmp_dt_gt = "cd {} && python3 get_precision_recall.py --dt {} --gt {} --output_dir {}".format(
            os.path.join(cwd_dir, 'tools'), new_result, gt_file, result_dir
        )
        ret = subprocess.call(cmp_dt_gt, shell=True)
        if ret != 0:
            sys.exit("Error. command {} execute failed, see {}.log in {}".format(
                ret, test_type, PATH_BASE))
        else:
            pass

    whole_result.append(result_dir)


def to_db():
    pass


def analysis_result(list_id):
    """ 多个批处理一起跑时，对结果进行汇总分析 """
    is_include_detect = any(list(filter(lambda x: 'detect' in x, whole_result)))
    is_include_liveness = any(list(filter(lambda x: 'liveness' in x, whole_result)))
    is_include_verify = any(list(filter(lambda x: 'verify' in x, whole_result)))

    final = datetime.datetime.now()
    final_time = datetime.datetime.strftime(final, '%Y%m%d_%H%M%S')
    result_dir = "{0}{1}result{1}result_{2}".format(PATH_BASE, os.sep, final_time)

    if is_include_detect:
        # result_dir = "{0}{1}result{1}result_detect".format(PATH_BASE, os.sep)
        # if not Path(result_dir).is_dir:
        #     os.makedirs(result_dir)
        analysis_result = 'result_{}'.format(Path(exe_file).name)
        analysis_detect_result(whole_result, report_file="pr_report.txt", final_result_name=analysis_result)
        # shutil.move(analysis_result, result_dir)

    if is_include_liveness:
        pass

    if is_include_verify:
        analysis_verify_result(whole_result, list_id, ana_result_dir=result_dir)


def main(id_=None):
    check_args()
    set_config_by_id(id_=id_)
    check_config()
    check_data_set()
    prepare_data()
    wait_crontab(crontab_time)
    result = execute(cmd[test_type])
    optimize_result(result)


if __name__ == "__main__":
    init_args()
    init_env()
    if not exe_file:
        main()
    else:
        # 处理文件中的参数, 按id值来执行命令
        all_id, params = s_json.get_params(exe_file)
        for i, item in enumerate(all_id):
            d_param = params[i]
            test_type, data_path, file_ext, crontab_time, section = \
                d_param.get('test_type', None), d_param.get('data_path', None), d_param.get('ext', None), \
                d_param.get('time', ''), d_param.get('section', '')
            main(id_=item)
            time.sleep(2)

        # 获取相同的id
        same_id = set(list(filter(lambda x: True if all_id.count(x) >= 2 else False, all_id)))
        analysis_result(same_id)
