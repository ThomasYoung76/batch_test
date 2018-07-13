#!/usr/bin/env python3
"""
Created on 

@author: yangshifu
@mail: yangshifu@sensetime.com
"""

import numpy as np
import pandas as pd
import csv

phone_file = "frr_M_Verify_MimicG2Pruned_Common_3.70.0.model.csv"
pc_file = "count.csv"
output = "output.xls"

# # 矩阵转换成csv
# df_pc = pd.read_csv(pc_file)
# # print(df_pc)
#
# df = pd.DataFrame(columns=['name', 'score'])
# for row in range(len(df_pc)):
#     name = df_pc.iloc[row][0]
#     s_row = df_pc.iloc[row]
#     lines = list(filter(lambda x: name not in x, s_row.index))
#     s_row_1 = s_row.drop(lines)
#     s_row_1.to_csv('pc.csv', mode='a')


# 结果
columns_phone = ['path', 'score']   # 路径和分数
pc_columns = ['name', 'score']

df_phone = pd.read_csv(phone_file, usecols=columns_phone)
df_pc = pd.read_csv('pc.csv', names=['name', 'score'])


df_phone = df_phone.rename(columns={'score': 'phone_score'})


df_phone['path'] = df_phone['path'].apply(lambda x: x.split('/')[-1].split('.')[0][:-2])
df_pc['path'] = df_pc['name'].apply(lambda x:x.split('/')[-1].split('.')[0])

df_phone = df_phone.set_index('path')
df_pc = df_pc.set_index('path')

# df_pc = df_pc.drop(['name'], axis=1)

# print(df_phone)
# print(df_pc)

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



