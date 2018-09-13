from parser.det_parser import parse_det
from parser.gt_parser import parse_gt
import numpy as np
import os
import pickle as pk


def raw_eval_func(gt_file_path, det_file_path, target_cls=1, iou=0.2, rotate=0):
    """
    Calculate box matching result for further evaluation
    :param gt_file_path:
    :param det_file_path:
    :return: argsort_idx, sorted_scores, fp, tp, recall_gt_id (all in sorted order)
    """
    gts = parse_gt(gt_file_path, rotate)
    dts = parse_det(det_file_path, target_cls)

    print('calculating raw evaluation...')
    # sort by scores, high to low
    argsort_idx = np.argsort(dts.scores)[::-1]
    sorted_scores = dts.scores[argsort_idx]

    # fp, tp, recall_gt_id
    dt_num = argsort_idx.shape[0]
    fp = np.zeros((dt_num,), dtype=np.int32)
    tp = np.zeros((dt_num,), dtype=np.int32)
    recall_gt_id = np.zeros((dt_num,), dtype=np.int32)
    recall_gt_id.fill(-1)

    # flag marking matched gts
    gt_num = gts.all_gt_boxes.shape[0]
    gt_matched_flag = np.zeros((gt_num,), dtype=np.int32)

    # go over dts, decide matching
    for i in range(dt_num):
        dt_idx = argsort_idx[i]
        img_path, ref_dt_box = dts[dt_idx]
        try:
            img_hw, gt_range, ref_gt_boxes, ig_range, ref_ig_boxes = gts[img_path]
        except KeyError as e:
            print(e)
            continue

        if ref_gt_boxes.shape[0] > 0:
            # if have gt
            # compute overlaps
            # intersection
            ixmin = np.maximum(ref_gt_boxes[:, 0], ref_dt_box[:, 0])
            iymin = np.maximum(ref_gt_boxes[:, 1], ref_dt_box[:, 1])
            ixmax = np.minimum(ref_gt_boxes[:, 2], ref_dt_box[:, 2])
            iymax = np.minimum(ref_gt_boxes[:, 3], ref_dt_box[:, 3])
            iw = np.maximum(ixmax - ixmin + 1., 0.)
            ih = np.maximum(iymax - iymin + 1., 0.)
            inters = iw * ih

            # union
            uni = ((ref_dt_box[:, 2] - ref_dt_box[:, 0] + 1.) *
                   (ref_dt_box[:, 3] - ref_dt_box[:, 1] + 1.) +
                   (ref_gt_boxes[:, 2] - ref_gt_boxes[:, 0] + 1.) *
                   (ref_gt_boxes[:, 3] - ref_gt_boxes[:, 1] + 1.) - inters)

            overlaps = inters / uni
            ov_argmax = np.argmax(overlaps)
            ovmax = overlaps[ov_argmax]
            maxov_gt_id = gt_range[0] + ov_argmax

            if ovmax > iou:
                if not gt_matched_flag[maxov_gt_id] == 1:
                    # gt not matched yet
                    tp[i] = 1
                    gt_matched_flag[maxov_gt_id] = 1
                    recall_gt_id[i] = maxov_gt_id
                else:
                    # duplicate dt
                    fp[i] = 1
            else:
                # no overlap
                fp[i] = 1

        else:
            # without gt, then dt is fp
            fp[i] = 1

        # ignore ignores
        if fp[i] == 1:
            if ref_ig_boxes.shape[0] > 0:
                ixmin = np.maximum(ref_ig_boxes[:, 0], ref_dt_box[:, 0])
                iymin = np.maximum(ref_ig_boxes[:, 1], ref_dt_box[:, 1])
                ixmax = np.minimum(ref_ig_boxes[:, 2], ref_dt_box[:, 2])
                iymax = np.minimum(ref_ig_boxes[:, 3], ref_dt_box[:, 3])
                iw = np.maximum(ixmax - ixmin + 1., 0.)
                ih = np.maximum(iymax - iymin + 1., 0.)
                inters = iw * ih

                # ign area
                ignS = (ref_ig_boxes[:, 2] - ref_ig_boxes[:, 0] + 1.) * \
                       (ref_ig_boxes[:, 3] - ref_ig_boxes[:, 1] + 1.)

                # dt area
                dtS = (ref_dt_box[0, 2] - ref_dt_box[0, 0] + 1.) * \
                      (ref_dt_box[0, 3] - ref_dt_box[0, 1] + 1.)

                ovigs = inters / ignS
                ovdts = inters / dtS
                ovmax = np.max(np.maximum(ovigs, ovdts))
                if ovmax > 0.1:
                    fp[i] = -1

    keep = (fp != -1)
    fp = fp[keep]
    tp = tp[keep]
    argsort_idx = argsort_idx[keep]
    sorted_scores = sorted_scores[keep]
    recall_gt_id = recall_gt_id[keep]

    return argsort_idx, sorted_scores, fp, tp, recall_gt_id, gts, dts


def get_raw_eval(gt_file_path, det_file_path, target_cls=1, iou=0.2, rotate=0):
    raw_eval = raw_eval_func(gt_file_path, det_file_path, target_cls, iou, rotate)
    argsort_idx, sorted_scores, fp, tp, recall_gt_id, gts, dts = raw_eval
    return argsort_idx, sorted_scores, fp, tp, recall_gt_id, gts, dts


# raw = get_raw_eval('../test_gt_1.txt', '../test_det_1.txt')
# print(raw)
