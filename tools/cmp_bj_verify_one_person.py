#!/usr/bin/env python3
"""
Created on 

@author: yangshifu
@mail: yangshifu@sensetime.com
"""
import os
import numpy as np
import pandas as pd

phone_file = "frr_M_Verify_MimicG2Pruned_Common_3.70.0.model.csv"
pc_file = "i_real.txt"
output = "verify_output.xls"
pc_score = 'verify_score_result%verify-2018-07-12_19-06-56--3.70.0%i_enroll.txt.csv'

columns_phone = ['path', 'score']   # 路径和分数
pc_columns = ['name', 'score']

df_phone = pd.read_csv(phone_file, usecols=columns_phone)
df_pc = pd.read_csv(pc_file, names=['name'])
np_server = np.fromfile(pc_score, dtype=np.float32)
df_pc['score'] = np_server


df_phone = df_phone.rename(columns={'score': 'batch_score'})
df_phone['path'] = df_phone['path'].apply(lambda x: x.split('/')[-1].split('.')[0][:-2])
df_pc['path'] = df_pc['name'].apply(lambda x:x.split('/')[-1].split('.')[0])


df_phone = df_phone.set_index('path')
df_pc = df_pc.set_index('path')

print(df_phone)
print(df_pc)

df_phone['batch_score'] = df_phone['batch_score'].astype('float32')

df_phone = df_phone.sort_index()
df_pc = df_pc.sort_index()

df_phone['server_score'] = df_pc['score'].astype('float32')

# print(df_batch)

df_phone['file_path'] = df_pc['name']
df_phone['diff'] = abs(df_phone['server_score'] - df_phone['batch_score'])
# #
df_phone = df_phone.sort_values(by=['diff'])


print(df_phone)
# df_batch.to_excel(output, index=False)
#
# print("输出文件成功：{}".format(output))

