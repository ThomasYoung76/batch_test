#!/usr/bin/env python3
"""
Created on 2018/11/2

在原有测试集的基础上获取小测试集

@author: yangshifu
@mail: yangshifu@sensetime.com
"""
import os
from pathlib import Path
import random
import shutil

# 原始测试集及小测试集
testset_dir = r"\\172.20.17.200\secured\data\testset\new\bj\India58_9036"
dst_dir = r"\\172.20.17.200\secured\data\testset\little\India58_little"

count_person = 50   # 小测试集中的总人数
nums_enroll = 5     # 小测试集每个人中注册数
nums_real = 10      # 小测试集每个人总真人数
nums_hack = 20      # 小测试集每个人总假人数
file_type = 'yuv'  # 带拷贝的文件类型

people = os.listdir(testset_dir)


if len(people) > count_person:
    people_50 = random.choices(people, k=count_person)
else:
    people_50 = people

for person in people_50:
    person_path = Path(testset_dir) / person
    print('Start copy img from {}'.format(str(person_path)))
    enroll = person_path / 'Enroll'
    hack = person_path / 'Hack'
    real = person_path / 'Real'
    assert person_path.exists()
    assert enroll.exists()
    assert hack.exists()
    assert real.exists()
    enrolls = list(enroll.glob("*.{}".format(file_type)))
    reals = list(real.glob("*.{}".format(file_type)))
    hacks = list(hack.glob("*.{}".format(file_type)))
    # 随机选取相应数量的图片
    if len(enrolls) > nums_enroll:
        enroll_5 = random.choices(enrolls, k=nums_enroll)
    else:
        enroll_5 = enrolls
    if len(reals) > nums_real:
        real_10 = random.choices(reals, k=nums_real)
    else:
        real_10 = reals
    if len(hacks) > nums_hack:
        hack_20 = random.choices(hacks, k=nums_hack)
    else:
        hack_20 = hacks
    # 拷贝图片
    for en in enroll_5:
        try:
            dst_enroll = Path(dst_dir) / person / 'Enroll'
            dst_enroll.mkdir(parents=True, exist_ok=True)
            shutil.copy(str(en), str(dst_enroll))
        except FileNotFoundError as fnfe:
            print(fnfe)
            continue

    for re in real_10:
        try:
            dst_real = Path(dst_dir) / person / 'Real'
            dst_real.mkdir(parents=True, exist_ok=True)
            shutil.copy(str(re), str(dst_real))
        except FileNotFoundError as fnfe:
            print(fnfe)
            continue

    for ha in hack_20:
        try:
            dst_hack = Path(dst_dir) / person / 'Hack'
            dst_hack.mkdir(parents=True, exist_ok=True)
            shutil.copy(str(ha), str(dst_hack))
        except FileNotFoundError as fnfe:
            print(fnfe)
            continue
