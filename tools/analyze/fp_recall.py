import numpy as np


def get_fp_recall(fp, tp, gt_num):
    cum_fp = fp.cumsum()
    cum_tp = tp.cumsum()
    recalls = cum_tp / (1.0*gt_num)
    return cum_fp, recalls


def get_recall_at_fp(fp_num, scores, cum_fp, recalls):
    fp_min = cum_fp[0]
    fp_max = cum_fp[-1]
    fp_num = np.clip(fp_num, fp_min, fp_max)
    fp_num_idx = np.where(cum_fp == fp_num)[0].max()
    return recalls[fp_num_idx], scores[fp_num_idx]-0.00001

def get_pr(fp, tp, gt_num):
    cum_tp = tp.cumsum()
    cum_fp = fp.cumsum()
    recalls = cum_tp / (1.0 * gt_num)
    precisions = cum_tp / (1.0 * (cum_tp + cum_fp)) 
    return cum_fp, cum_tp, precisions, recalls

def get_possible_recalls_at_pre(pre, scores, precisions,recalls):
    assert len(precisions) == len(recalls)
    possible_recalls = []
    recall_scores = []
    for i in range(len(recalls)-1):
        max_end = max(precisions[i], precisions[i+1])
        min_end = min(precisions[i], precisions[i+1])
        if min_end <= pre <= max_end:
            possible_recalls.append(recalls[i])
            recall_scores.append(scores[i])
    return possible_recalls, recall_scores
