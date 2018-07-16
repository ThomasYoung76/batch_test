#!/usr/bin/python  
#-*- coding:utf-8 -*-

import os
import pandas as pd

batch_file = "unlock_data.record.csv"
server_file = "4.1.0-values.csv"

output = "verify_output.xls"

df_batch = pd.read_csv(batch_file, usecols=['ir name', 'Liveness score'])
df_server = pd.read_csv(server_file, names=['score', 'name'])

df_batch = df_batch.rename(columns={'ir name': 'path', 'Liveness score':'batch_score'})
df_batch['path'] = df_batch['path'].apply(lambda x: x.split('/')[-1].split('.')[0][:-2])
df_server['path'] = df_server['name'].apply(lambda x:x.split('/')[-1].split('.')[0])


df_batch = df_batch.set_index('path')
df_server = df_server.set_index('path')

df_batch = df_batch.sort_index()
df_server = df_server.sort_index()

df_batch['server_score'] = df_server['score']
df_batch['file_path'] = df_server['name']
df_batch['diff'] = abs(df_batch['server_score'] - df_batch['batch_score'])
# #
df_batch = df_batch.sort_values(by=['diff'])

df_batch.to_excel(output, index=False)

print("输出文件成功：{}".format(output))

