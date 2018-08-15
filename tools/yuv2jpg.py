#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: 
    jinxiao <jinxiao@sensetime.com>

Modified:
    liqiming <liqiming@sensetime.com>
    yangshifu <yangshifu@sensetime.com>
Usage:
    python <scripts-name> --help

Function:
    transfer yuv image to jpg
"""

import numpy as np
import cv2, os, sys
import argparse
import imutils

def cvt_yuv_nv21_to_rgb(args, yuv_file):
    # yuv_file = 't.yuv'
    # print 'yuv_file = ',yuv_file
    stream = open(yuv_file, 'rb')
    # Seek to the fourth frame in the file
    # stream.seek(4 * width * height * 1.5)
    # Calculate the actual image size in the stream (accounting for rounding
    # of the resolution)
    fwidth = (args.width + 31) // 32 * 32
    fheight = (args.height + 15) // 16 * 16
    # Load the Y (luminance) data from the stream

    Y = np.fromfile(stream, dtype=np.uint8, count=fwidth*fheight).\
            reshape((fheight, fwidth))
    # Load the UV (chrominance) data from the stream, and double its size
    UV = np.fromfile(stream, dtype=np.uint8, count= 2 * (fwidth//2)*(fheight//2)).\
            reshape((fheight//2, fwidth//2,2)).\
            repeat(2, axis=0).repeat(2, axis=1)

    U = UV[:,:,0] 
    V = UV[:,:,1]

    # Stack the YUV channels together, crop the actual resolution, convert to
    # floating point for later calculations, and apply the standard biases
    YUV = np.dstack((Y, U, V))[:args.height, :args.width, :].astype(np.float)
    YUV[:, :, 0]  = YUV[:, :, 0]  - 16   # Offset Y by 16
    YUV[:, :, 1:] = YUV[:, :, 1:] - 128  # Offset UV by 128
    # YUV conversion matrix from ITU-R BT.601 version (SDTV)
    # Note the swapped R and B planes!
    #              Y       U       V
    M = np.array([[1.164,  2.017,  0.000],    # B
                  [1.164, -0.392, -0.813],    # G
                  [1.164,  0.000,  1.596]])   # R
    # Take the dot product with the matrix to produce BGR output, clamp the
    # results to byte range and convert to bytes
    BGR = YUV.dot(M.T).clip(0, 255).astype(np.uint8)
    RGB = cv2.cvtColor(BGR, cv2.COLOR_BGR2RGB)
    IMG = imutils.rotate_bound(RGB, args.rotate)
    return IMG


def process(args, yuv_list):
    count = 0
    succ = 0
    fail = 0
    for file in yuv_list:
        count += 1
        # image_path = args.files_path + file.strip()
        image_path = os.path.dirname(file) + os.sep + os.path.basename(file).strip()
        print(image_path)
        try:
            img = cvt_yuv_nv21_to_rgb(args, image_path)
            saved_image_path = image_path + '.jpg'
            cv2.imwrite(saved_image_path, img)
            print("[%d/%d] Success: %s" % (count, len(yuv_list), image_path))
            succ += 1
        except:
            print("[%d/%d] Fail: %s" % (count, len(yuv_list), image_path))
            fail += 1

    print()
    print("Success %d times" % succ)
    print("Fail %d times" % fail)


def getYuvFileList(filesPath):
    all_filesList = []
    yuv_filesList = []
    for (dirpath, dirnames, filenames) in os.walk(filesPath):
        for f in filenames:
            file_path = os.path.join(dirpath, f)
            all_filesList.append(file_path)
        # all_filesList.extend(filenames)
    for file in all_filesList:
        if file[-4:] in '.yuv':
            yuv_filesList.append(file)
        
    return yuv_filesList


if __name__ == '__main__':
    default_description = 'transfrom yuv image to jpg'
    parser = argparse.ArgumentParser(prog="yuv2jpg.py", description=default_description)
    parser.add_argument('-p', '--files_path', type=str, required=False, default='./', help='default ./')
    parser.add_argument('-t', '--height',     type=int, required=False, default=480,  help='default 480')
    parser.add_argument('-w', '--width',      type=int, required=False, default=640,  help='default 640')
    parser.add_argument('-a', '--rotate',     type=int, required=False, default=0,    help='default 0')
    args = parser.parse_args()

    print()
    print('----------START----------')
    print()
    yuv_filesList = getYuvFileList(args.files_path)
    if len(yuv_filesList) is not 0:
        process(args, yuv_filesList)
    else:
        print('no yuv file')

    print()
    print('----------END----------')
    
