#!/usr/bin/env python3
"""
Created on

@author: yangshifu
@mail: yangshifu@sensetime.com
"""

#!/usr/bin/python
#-*- coding:utf-8 -*-

import os
import pandas as pd

phone_file = "frr_liveness.csv"
pc_file = "4.3.0-values.csv"

output = "liveness_output.xls"

# 结果
columns_phone = ['path', 'hackerscore']   # 路径和分数
pc_columns = ['score', 'name']

df_phone = pd.read_csv(phone_file, usecols=columns_phone)
df_pc = pd.read_csv(pc_file, names=pc_columns, encoding='gbk', sep=',')

df_phone = df_phone.rename(columns={'hackerscore': 'phone_score'})

df_phone['path'] = df_phone['path'].apply(lambda x: x.split('/')[-2])
df_pc['path'] = df_pc['name'].apply(lambda x:x.split(' ')[0].split('/')[-1].split('.')[0])


df_phone = df_phone.set_index('path')
df_pc = df_pc.set_index('path')

# df_pc = df_pc.drop(['name'], axis=1)

# print(df_phone)
print(df_pc)

df_phone['phone_score'] = df_phone['phone_score'].astype('float32')


df_phone = df_phone.sort_index()
df_pc = df_pc.sort_index()

df_phone['pc_score'] = df_pc['score'].astype('float32')

# # print(df_batch)
#
# df_phone['file_path'] = df_pc['name']
df_phone['diff'] = abs(df_phone['pc_score'] - df_phone['phone_score'])
df_phone['file_path'] = df_pc['name']
# # #
df_phone = df_phone.sort_values(by=['diff'])

df_phone.to_excel(output, index=False)

print("输出文件成功：{}".format(output))

# print(df_pc)