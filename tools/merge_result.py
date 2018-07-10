# -*- coding: utf-8 -*-
"""
Created on 2018/6/7

@author: yangshifu
@mail: yangshifu@sensetime.com
"""
"""
    手机端活体统计数据结果合并，计算FRR和FAR
如：
阈值    FRR       FAR                  
0.91  0.098845  0.927440
0.92  0.084724  0.938282
0.93  0.078306  0.948290
0.94  0.069320  0.955796
0.95  0.069320  0.959967
0.96  0.056483  0.967473
0.97  0.038511  0.975813
"""

import os
import functools

import pandas as pd
import matplotlib.pyplot as plt


# 绘图设置中文格式
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 文件路径
src_path = r"C:\Users\yangshifu\Documents\test\合并结果\result"
dst_path = r"C:\Users\yangshifu\Documents\test\合并结果\1.xls"
real_flag = "human_test"   # 真人文件标志

df_real = []
df_photo = []
for file_name in os.listdir(src_path):
    file_path = src_path + os.sep + file_name
    if not file_name.endswith('xls'):
        continue
    if real_flag in file_name:
        try:
            df = pd.read_excel(file_path, sheet_name='统计', index_col='阈值')
        except:
            pass
        df_real.append(df)
    else:
        try:
            df = pd.read_excel(file_path, sheet_name='统计', index_col='阈值')
        except:
            pass
        df_photo.append(df)

writer = pd.ExcelWriter(dst_path)

if df_real:
    df_real_count = functools.reduce(lambda a, b: a + b, df_real)
    df_real_count['FRR'] = (df_real_count['图片总数'] - df_real_count['小于阈值']) / df_real_count['图片总数']
    df_real_count.to_excel(writer, '汇总统计', index=True)

if df_photo:
    df_photo_count = functools.reduce(lambda a, b: a + b, df_photo)
    df_photo_count['FAR'] = (df_photo_count['图片总数'] - df_photo_count['大于阈值']) / df_photo_count['图片总数']
    df_photo_count.to_excel(writer, '汇总统计', index=True, startrow=10)

if df_real and df_photo:
    df_result = pd.DataFrame(data=df_real_count['FRR'])
    df_result['FAR'] = df_photo_count['FAR']
    df_result.to_excel(writer, '汇总统计', index=True, startrow=7, startcol=8)

writer.save()
print("执行成功，汇总统计文件输出在路径：{}".format(dst_path))

if df_real and df_photo:
    plt.title('图FRR-FAR')
    plt.xlabel('FAR')
    plt.ylabel('FRR')
    plt.plot(df_result['FAR'], df_result['FRR'], 'ro-')
    plt.show()

print(df_result)