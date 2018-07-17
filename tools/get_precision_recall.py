from base_eval.raw_eval import get_raw_eval
from analyze.fp_recall import get_fp_recall, get_recall_at_fp, get_pr, get_possible_recalls_at_pre
import numpy as np

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, average_precision_score

import argparse
import os

parser = argparse.ArgumentParser(description='get precision-recall evaluation')
parser.add_argument('--gt', type=str,default='gt.txt')
parser.add_argument('--dt', type=str,default='dt.txt')
parser.add_argument('--target_cls', type=int, default=1)
parser.add_argument('--rotate', type=int, default=0)
parser.add_argument('--output_dir',type=str, default='eval_out')
parser.add_argument('--pre_score', type=int, default=99)
parser.add_argument('--iou', type=float, default=0.2)
parser.add_argument('--title', type=str, default='pr-curve')
args = parser.parse_args()

gt_file_path = args.gt
det_file_path = args.dt
target_cls = args.target_cls
rotate = args.rotate
iou = args.iou

argsort_idx, sorted_scores, fp, tp, recall_gt_id, gts, dts = \
    get_raw_eval(gt_file_path, det_file_path, target_cls=target_cls, iou=iou, rotate=rotate)

gt_num = gts.all_gt_boxes.shape[0]
dt_num = sorted_scores.shape[0]

print('calculating fp-recall...')
cum_fp, recalls = get_fp_recall(fp, tp, gt_num)
cum_fp, cum_tp, precisions, recalls=get_pr(fp, tp, gt_num)


#fp_001 = int(dt_num*0.01)

#fp_001_recall, fp_001_thresh = get_recall_at_fp(fp_001, sorted_scores, cum_fp, recalls)

# make output dir
if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)

with open(os.path.join(args.output_dir,'pr.txt'), 'w') as fout:
    for i in range(dt_num):
        fout.write('%f %f %f\n' % (sorted_scores[i], precisions[i], recalls[i]))

pre_score=args.pre_score / (1.0 * 100)
possible_rec_at_pre, recall_scores = get_possible_recalls_at_pre(pre_score, sorted_scores, precisions, recalls)
#fpr, tpr, _ = roc_curve(y_true=tp, y_score=sorted_scores)
#auc = auc(fpr, tpr)
ap=average_precision_score(tp, sorted_scores)

#print('AUC: %f ' % auc)
print('AP: %f '% ap)

import pdb
#pdb.set_trace()

fout = open(os.path.join(args.output_dir, 'pr_report.txt'),'w')
pre = 0
rec =0

if len(possible_rec_at_pre) > 0:
    max_recall_id = np.argmax(possible_rec_at_pre)
    max_recall = possible_rec_at_pre[max_recall_id]
    max_recall_score = recall_scores[max_recall_id]
    pre = pre_score
    rec = max_recall
    fout.write('Max recall at %f precision: %f \n' % (pre_score, max_recall))
    fout.write('Score thresh should be: %f \n' % max_recall_score)
    print('Max recall at %f precision: %f' % (pre_score, max_recall))
    print('Score thresh should be: %f' % max_recall_score)
else:
    pre = precisions[-1]
    rec = recalls[-1]
    print('impossible %f precision' % pre_score)
    print('the lowest precision is %f, the recall is %f, the thresh is  %f' % (precisions[-1], recalls[-1], sorted_scores[-1]))
    fout.write('Impossible %f precision \n' % pre_score)
    fout.write('The lowest precision is %f, the recall is %f, the thresh is %f \n' % (precisions[-1], recalls[-1], sorted_scores[-1]))

#fout.write('AUC: %f \n' % auc)
fout.write('AP: %f \n' % ap)

fout.flush()

plt.figure()
plt.step(recalls, precisions, color='b', alpha=0.2,
         where='post')
plt.fill_between(recalls, precisions, step='post', alpha=0.2,
                 color='b')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.ylim([0.0, 1.05])
plt.xlim([0.0, 1.0])
plt.title('{}:{:.4f}@{:.2f}precision'.format(args.title, rec, pre))
plt.savefig(os.path.join(args.output_dir,'pr.png'))
