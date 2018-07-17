import pdb
import numpy as np
from collections import OrderedDict
import os
import pickle as pk


def rotate_bbox(bbox, img_size, angle):
    h, w = img_size
    x1, y1, x2, y2 = bbox
    if angle == 0:
        return [x1, y1, x2, y2]
    if angle == 90:
        return [h - 1 - y2, x1, h - 1 - y1, x2]
    elif angle == 180:
        return [w - 1 - x2, h - 1 - y2, w - 1 - x1, h - 1 - y1]
    elif angle == 270:
        return [y1, w - 1 - x2, y2, w - 1 - x1]
    else:
        raise Exception("Rotate angle not supported")


def parse_meta(meta_file_path, rotate=0):
    metas = []

    meta_file = open(meta_file_path, 'r')

    state = 0

    count = 0

    path = ''
    height = 0
    width = 0

    gt_num = 0
    img_gts = []

    ign_num = 0
    img_igns = []

    labels = []

    line = meta_file.readline()
    while line:
        if state == 0:
            spt = line.split(' ')
            assert spt[0] == '#', 'error in meta file, expecting \'#\', entry id: %d' % count
            state = 10
            count = count + 1
            #if count % 1000 == 0:
            #    print(count)
            line = meta_file.readline()
        elif state == 10:
            path = line.strip('\n')
            state = 11
            line = meta_file.readline()
        elif state == 11:
            spt = line.split(' ')
            height = int(spt[1])
            width = int(spt[2])
            state = 1
            line = meta_file.readline()
        elif state == 1:
            ign_num = int(line)
            state = 2
            line = meta_file.readline()
        elif state == 2:
            spt = line.split(' ')
            if len(spt) == 4:
                x1, y1, x2, y2 = float(spt[0]), float(spt[1]), float(spt[2]), float(spt[3])
                b = [x1, y1, x2, y2]
                rotated_b = rotate_bbox(b, (height, width), rotate)
                img_igns.append(rotated_b)
            else:
                assert len(spt) == 1, 'error in meta file, expecting gt num, entry id: %d' % count
                gt_num = int(spt[0])
                state = 3
            line = meta_file.readline()
        elif state == 3:
            if line[0] != '#':
                spt = line.split(' ')
                assert len(spt) == 5, 'error in meta file, expecting box annotation, entry id: %d' % count
                labels.append(int(spt[0]))
                x1, y1, x2, y2 = float(spt[1]), float(spt[2]), float(spt[3]), float(spt[4])
                b = [x1, y1, x2, y2]
                rotated_b = rotate_bbox(b, (height, width), rotate)
                img_gts.append(rotated_b)
                line = meta_file.readline()
            else:
                if rotate == 90 or rotate == 270:
                    height, width = width, height
                metas.append((path, height, width, np.array(img_gts).reshape((-1, 4)), np.array(labels), np.array(img_igns).reshape((-1, 4))))
                img_gts = []
                labels = []
                img_igns = []
                state = 0
    if rotate == 90 or rotate == 270:
        height, width = width, height
    metas.append((path, height, width, np.array(img_gts).reshape((-1, 4)), np.array(labels), np.array(img_igns).reshape((-1, 4))))
    meta_file.close()
    return metas


class FaceDETAnnotation(object):
    def __init__(self, metas):
        # count gt box num
        gt_box_num = 0
        ig_box_num = 0
        for item in metas:
            gt_box_num += item[3].shape[0]
            ig_box_num += item[5].shape[0]
        # store all gt boxes in one array
        # store all img hws in one array
        # each img id points to its index and the range of its gts
        self.all_gt_boxes = np.zeros((gt_box_num, 4))
        self.all_ig_boxes = np.zeros((ig_box_num, 4))
        self.all_img_hws = np.zeros((len(metas), 2))
        self.index = OrderedDict()
        gts_ptr = 0
        igs_ptr = 0
        for idx, item in enumerate(metas):
            # copy gt boxes
            gts_beg = gts_ptr  # inclusive
            gts_end = gts_ptr+item[3].shape[0]  # exclusive
            igs_beg = igs_ptr
            igs_end = igs_ptr+item[5].shape[0]
            self.all_gt_boxes[gts_beg:gts_end, :] = \
                item[3][:, :]
            self.all_ig_boxes[igs_beg:igs_end, :] = \
                item[5][:, :]
            self.all_img_hws[idx, :] = (item[1], item[2])
            # build index
            self.index[item[0]] = (
                idx,
                (gts_beg, gts_end),
                (igs_beg, igs_end)
            )
            gts_ptr = gts_end
            igs_ptr = igs_end

    def __getitem__(self, img_path):
        index_item = self.index[img_path]
        img_id = index_item[0]
        box_range = index_item[1]
        igs_range = index_item[2]
        ref_gt_boxes = self.all_gt_boxes[box_range[0]:box_range[1], :]
        ref_ig_boxes = self.all_ig_boxes[igs_range[0]:igs_range[1], :]
        ref_hw = self.all_img_hws[img_id, :]
        # hw, gt_range, ref_boxes, ig_range, ref_igs
        return ref_hw, index_item[1], ref_gt_boxes, index_item[2], ref_ig_boxes

    def filter_gts(self, filter_bools):
        result = OrderedDict()
        for img_path, index_item in self.index.items():
            box_range = index_item[1]
            ref_gt_boxes = self.all_gt_boxes[box_range[0]:box_range[1], :]
            ref_filter = filter_bools[box_range[0]:box_range[1]]
            remain_boxes = ref_gt_boxes[ref_filter, :]
            if remain_boxes.shape[0] > 0:
                result[img_path] = remain_boxes
        return result


def parse_gt(gt_file_path, rotate):
    """
    :param gt_file_path: path to SenseTime format annotation list
    :return: FaceDETAnnotation
    """
    print('parsing from %s...' % gt_file_path)
    # convert txt annotation
    metas = parse_meta(gt_file_path, rotate)
    # convert to FaceDETAnnotation
    facedet_ann = FaceDETAnnotation(metas)

    return facedet_ann
