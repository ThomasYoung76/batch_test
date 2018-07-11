#!/usr/bin/env python3
"""
Created on 2018/7/9

@author: yangshifu
@mail: yangshifu@sensetime.com
"""
import sys
import numpy as np
from sklearn.metrics import roc_curve

from s_config import fprs
from s_file import list2file


def cal_roc(score_name, label_name, roc_name, fprs=fprs):
    roc_list = []
    scores = np.loadtxt(score_name, dtype=np.float32, delimiter='\n')
    labels = np.loadtxt(label_name, dtype=np.int32, delimiter='\n')
    try:
        assert(len(scores) == len(labels))
    except AssertionError:
        sys.exit("Error. score file {} has {} rows, but label file {} has {} rows."
                 " same rows required. ".format(score_name, len(scores), label_name, len(labels)))
    roc_fpr, roc_tpr, roc_thresholds = roc_curve(labels, scores, pos_label=1, drop_intermediate=False)

    tpr_k_score = []
    th_k_score = []
    for fpr_ratio in fprs:
        idx = np.argmin(np.abs(roc_fpr - fpr_ratio))
        tpr = roc_tpr[idx]
        th = roc_thresholds[idx]
        tpr_k_score.append(tpr)
        th_k_score.append(th)

    roc_list.append("fpr    | "+" | ".join(format(i, '.0e') for i in fprs))
    roc_list.append("|".join("  :-:  " for i in range(len(fprs)+1)))
    roc_list.append("tpr(%) | "+" | ".join('{:.2f}'.format(i*100) for i in tpr_k_score))
    roc_list.append("thres  | "+" | ".join('{:.3f}'.format(i) for i in th_k_score))
    list2file(roc_list, roc_name)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--score', default='', type=str, help='生成的分数矩阵')
    parser.add_argument('-l', '--label', default='', type=str, help='label文件')
    parser.add_argument('-o', '--output', default='roc.txt', type=str, help='输出的roc文本')
    args = parser.parse_args()
    cal_roc(args.score, args.label, args.output)