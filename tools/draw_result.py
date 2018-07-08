# -*- coding: utf-8 -*-
"""
Created on 2018/6/11

@author: yangshifu
@mail: yangshifu@sensetime.com
"""

"""
    通过roc.txt绘制roc.png
version: 7.26.0 
total_num: 26156
valid_num: 26156
fpr    | 0.100 | 0.090 | 0.080 | 0.070 | 0.060 | 0.050 | 0.040 | 0.030 | 0.020 | 0.010
  :-:  |  :-:  |  :-:  |  :-:  |  :-:  |  :-:  |  :-:  |  :-:  |  :-:  |  :-:  |  :-:  
tpr(%) | 99.96 | 99.94 | 99.94 | 99.92 | 99.92 | 99.91 | 99.88 | 99.80 | 99.72 | 99.27
thres  | 0.815 | 0.823 | 0.834 | 0.854 | 0.883 | 0.903 | 0.914 | 0.939 | 0.956 | 0.982


version: 7.24.0
total_num: 26156
valid_num: 26156
fpr    | 0.100 | 0.090 | 0.080 | 0.070 | 0.060 | 0.050 | 0.040 | 0.030 | 0.020 | 0.010
  :-:  |  :-:  |  :-:  |  :-:  |  :-:  |  :-:  |  :-:  |  :-:  |  :-:  |  :-:  |  :-:  
tpr(%) | 99.98 | 99.98 | 99.97 | 99.97 | 99.96 | 99.94 | 99.91 | 99.85 | 99.80 | 99.56
thres  | 0.535 | 0.690 | 0.897 | 0.904 | 0.912 | 0.927 | 0.950 | 0.956 | 0.964 | 0.974

"""

import re
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ver_old = "liveness-2018-06-11_17-44-24--7.24.0"        # 旧版本路径
ver_new = "liveness-2018-06-11_17-20-03--7.26.0"        # 新版本路径


# draw line
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def get_roc_data(result_path):
    """获取result_path中*roc.txt中的数据"""
    r = Path(result_path)
    df = pd.DataFrame()
    for roc in r.glob("*roc.txt"):
        content = roc.read_text()
        lines = content.split('\n')
        for i in [2, 4, 5]:
            line = lines[i].split('|')
            ret = list(map(lambda a: a.strip(' '), line))
            df[ret[0]] = ret[1:]

    df['tpr'] = df['tpr(%)'].astype('float64')
    df['tpr'] = df['tpr'] / 100
    df['fpr'] = df['fpr'].astype('float64')
    df.set_index(df['fpr'])
    df = df.sort_index(axis=1)
    return df


def get_far_frr(result_path):
    """ 获取result_path中far和frr的数据"""
    for f in Path(result_path).glob("*----result.xlsx"):
        ver = re.search(r"(\d{1,2}\.\d{1,2}\.\d{1,2})----result", str(f))
        ver_num = ver.group(1)
        df = pd.read_excel(f, sheet_name='FAR_FRR', usecols=2, index_col=0)
    return df, ver_num


def draw_roc(ver_old, ver_new):
    """
    画ROC对比曲线图
    """
    df_ver1 = get_roc_data(ver_old)
    df_ver2 = get_roc_data(ver_new)

    y1 = df_ver1['tpr'].tolist()
    y2 = df_ver2['tpr'].tolist()

    fig = plt.figure()
    plt.title('ROC曲线图')
    # plt.yticks(np.linspace(0.1, 1, 10))
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.plot(df_ver1['fpr'], y1, 'bo-', label=ver_old)
    plt.plot(df_ver1['fpr'], y2, "r*-", label=ver_new)

    plt.grid(True)
    fig.legend()

    fig.savefig(Path(ver_new) / 'roc.png')
    print("generate roc.png in {}".format(Path(ver_new)))


def draw_far_frr(ver_old, ver_new):
    """
    画FAR和FRR对比图
    :param ver_old:
    :param ver_new:
    :return:
    """
    df_old, ver_num_old = get_far_frr(ver_old)
    df_new, ver_num_new = get_far_frr(ver_new)
    df = df_old.merge(df_new, how='left')
    # print(df_old)
    fig = plt.figure()
    plt.title("FAR-FRR")
    plt.xlabel('FAR')
    plt.ylabel('FRR')
    plt.plot(df_old['FAR'], df_old['FRR'], 'bo-', label=ver_old)
    plt.plot(df_new['FAR'], df_new['FRR'], 'r*-', label=ver_new)
    plt.grid(True)
    fig.legend()
    fig.savefig(Path(ver_new) / 'frr-far.png')
    print("generate frr-far.png in {}".format(Path(ver_new)))


if __name__ == "__main__":
    parse = argparse.ArgumentParser(description="compare results of two version", formatter_class=argparse.RawTextHelpFormatter)
    parse.add_argument('-o', "--old", action="store", default=ver_old, help="旧版本批处理结果路径")
    parse.add_argument('-n', '--new', action="store", default=ver_new, help='新版本结果路径')
    options = parse.parse_args()
    draw_roc(options.old, options.new)
    draw_far_frr(options.old, options.new)