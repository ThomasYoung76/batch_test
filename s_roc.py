#!/usr/bin/env python3
"""
Created on 2018/7/9

@author: yangshifu
@mail: yangshifu@sensetime.com
"""
import sys
import multiprocessing
import bisect

import numpy as np
from sklearn.metrics import roc_curve

from s_file import list2file


def cal_roc(score_name, label_name, roc_name, fprs):
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


thres = np.arange(0, 1, 1e-3)
th_idx = range(650, 850, 10)


def compute_roc_part(worker_id, scores, meta1, meta2, delta, thres, tp, fp, total_pos_neg):
    labels = (meta1.reshape(-1,1) == meta2.reshape(1,-1)).astype(np.int)
    if delta != -1:
        indices = np.triu_indices(delta, k=1)
        scores = scores[indices]
        labels = labels[indices]
    else:
        scores = scores.reshape(-1)
        labels = labels.reshape(-1)

    sorted_idx = np.argsort(scores)
    sorted_scores = scores[sorted_idx]
    sorted_labels = labels[sorted_idx]
    cum_pos = np.cumsum(sorted_labels, dtype=float)
    total_pos = cum_pos[-1]
    n = labels.size
    fn = cum_pos - sorted_labels
    tp_tmp = total_pos - fn
    fp_tmp = np.arange(n, 0, -1) - tp_tmp
    c_tp = [0]*len(thres)
    c_fp = [0]*len(thres)
    start = 0
    for i, th in enumerate(thres):
        #'Find rightmost value less than or equal to x'
        pos = bisect.bisect_right(sorted_scores, th, start)
        if pos != len(sorted_scores):
            c_tp[i] = tp_tmp[pos]
            c_fp[i] = fp_tmp[pos]
            start = pos
        else:
            c_tp[i] = total_pos
            c_fp[i] = 0
    total_pos_neg[worker_id] = np.array([total_pos, n - total_pos])
    tp[worker_id] = c_tp
    fp[worker_id] = c_fp


def cal_verify_roc(score_name, label_name, roc_name, fprs, is_one_vs_one=False):
    roc_list = []
    score = np.fromfile(score_name, dtype=np.float32)
    max_step = 2000
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    mgr = multiprocessing.Manager()
    if is_one_vs_one:
        label = np.loadtxt(label_name, dtype=np.int, delimiter=',').reshape(-1)[1:]
        n = label.shape[0]
        assert(len(score) == n*n)
        score = score.reshape(n, n)
        i_range = (n-1)//max_step+1
        total_num = i_range * (i_range + 1) / 2
        tp = mgr.list(range(total_num))
        fp = mgr.list(range(total_num))
        total_pos_neg = mgr.list(range(total_num))
        worker_id = 0
        for i in range(i_range):
            beg_i = i*max_step
            end_i = min(beg_i + max_step, n)
            for j in range(i, (n-1)//max_step+1):
                delta = -1
                beg_j = j*max_step
                end_j = min(beg_j + max_step, n)
                if i == j:
                    assert end_i-beg_i == end_j-beg_j
                    delta = end_i-beg_i
                score_part = score[beg_i:end_i,beg_j:end_j]
                meta1 = label[beg_i:end_i]
                meta2 = label[beg_j:end_j]
                pool.apply_async(compute_roc_part, args=(worker_id, score_part, meta1, meta2, delta, thres, tp, fp, total_pos_neg))
                worker_id += 1
    else:
        with open(label_name, 'r') as f:
            lines = f.readlines()
            assert(len(lines) == 2)
            label_enroll = np.fromstring(lines[0].strip(), sep=' ', dtype=int)
            label_real = np.fromstring(lines[1].strip(), sep=' ', dtype=int)

        assert(len(score) == len(label_enroll) * len(label_real))
        score = score.reshape(len(label_enroll), len(label_real))

        total_num = (label_real.shape[0]-1)//max_step+1
        tp = mgr.list(range(total_num))
        fp = mgr.list(range(total_num))
        total_pos_neg = mgr.list(range(total_num))
        worker_id = 0
        for beg_j in range(0, label_real.shape[0], max_step):
            end_j = min(beg_j + max_step, label_real.shape[0])
            label_real_part = label_real[beg_j:end_j]
            score_part = score[:, beg_j:end_j]
            pool.apply_async(compute_roc_part, args=(worker_id, score_part, label_enroll, label_real_part, -1, thres, tp, fp, total_pos_neg))
            worker_id += 1

    pool.close()
    pool.join()
    tp = np.sum(tp, axis=0)
    fp = np.sum(fp, axis=0)
    total_pos_neg = np.sum(total_pos_neg, axis=0)
    tpr = tp/total_pos_neg[0]
    fpr = fp/total_pos_neg[1]
    csvnp = np.array([thres, 1-tpr, fpr]).T
    np.savetxt('verify/result.csv', csvnp, fmt='%.4f,%1.4e,%1.4e')
    tpr_k_score = []
    th_k_score = []
    for fp in fprs:
        idx = np.argmin(np.abs(fpr-fp))
        tpr_k_score.append(tpr[idx])
        th_k_score.append(thres[idx])

    roc_list.append("fpr    | "+" | ".join(format(i, '>5.0e') for i in fprs))
    roc_list.append("|".join("  :-:  " for i in range(len(fprs)+1)))
    roc_list.append("tpr(%) | "+" | ".join('{:>5.2f}'.format(i*100) for i in tpr_k_score))
    roc_list.append("thres  | "+" | ".join('{:>5.3f}'.format(i) for i in th_k_score))

    roc_list.append("======================================================")

    roc_list.append("thres  | "+" | ".join('{:>5.3f}'.format(i) for i in thres[th_idx]))
    roc_list.append("|".join("  :-:  " for i in range(len(th_idx)+1)))
    roc_list.append("fpr(‰) | "+" | ".join('{:>5.2f}'.format(i*1000) for i in fpr[th_idx]))
    roc_list.append("tpr(%) | "+" | ".join('{:>5.2f}'.format(i*100) for i in tpr[th_idx]))
    list2file(roc_list, roc_name)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--score', default='', type=str, help='生成的分数矩阵')
    parser.add_argument('-l', '--label', default='', type=str, help='label文件')
    parser.add_argument('-o', '--output', default='roc.txt', type=str, help='输出的roc文本')
    args = parser.parse_args()
    cal_roc(args.score, args.label, args.output)