import pdb
import numpy as np
import os
import pickle as pk


class FaceDETResult(object):
    def __init__(self, det_file_path, target_cls=1):
        self.img_paths = []
        img_path_reg = {}
        tmp_box2im = []
        tmp_boxes = []
        tmp_scores = []
        with open(det_file_path, 'r') as fin:
            for line in fin:
                spt = line.split(' ')
                full_img_path = spt[0]
                if full_img_path not in img_path_reg:
                    img_path_id = len(self.img_paths)
                    img_path_reg[full_img_path] = img_path_id
                    self.img_paths.append(full_img_path)
                else:
                    img_path_id = img_path_reg[full_img_path]
                cls = int(spt[5])
                if cls == target_cls:
                    tmp_box2im.append(img_path_id)
                    tmp_boxes.append([float(spt[1]),
                                      float(spt[2]),
                                      float(spt[3]),
                                      float(spt[4])])
                    tmp_scores.append(float(spt[6]))
        self.det_boxes = np.array(tmp_boxes)
        # l, t, w, h -> l, t, r, b
        #print(self.det_boxes.shape)
        self.det_boxes[:, 2] = self.det_boxes[:, 2] + self.det_boxes[:, 0]
        self.det_boxes[:, 3] = self.det_boxes[:, 3] + self.det_boxes[:, 1]
        self.scores = np.array(tmp_scores)
        self.box2im = np.array(tmp_box2im)

    def __getitem__(self, index):
        img_path = self.img_paths[self.box2im[index]]
        ref_box = self.det_boxes[index:index+1, :]
        return img_path, ref_box

    def __len__(self):
        return self.det_boxes.shape[0]


def parse_det(det_file_path, target_cls=1):
    print('parsing from %s...' % det_file_path)
    # convert to FaceDETAnnotation
    facedet_res = FaceDETResult(det_file_path, target_cls)
    return facedet_res

