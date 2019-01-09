#!/usr/bin/python
#-*- coding:utf-8 -*-

import cv2
#import multiprocessing

from pathlib import Path
import os

src = '/home/andrew/code/1_project/2D_RGB/9_testset/v3.0/eyestate/eyestate-black95_9715'
dst = '/home/andrew/code/yangshifu/eyestate-black95_9715_png' 
# dst_resize = '/home/andrew/code/yangshifu/eyestate-black69_8426_png_resize' 


def proc(file):
    name = file.strip(".jpg") + ".png"
    name = name.replace(src, dst)
    print(name)
    if not Path(os.path.dirname(name)).exists():
        Path(os.path.dirname(name)).mkdir(parents=True)
    img = cv2.imread(file)
    img = cv2.resize(img, (480, 640), interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(name,img)

def resize_jpg(file):
    name = file.replace(src, dst_resize)
    if not Path(os.path.dirname(name)).exists():
        Path(os.path.dirname(name)).mkdir(parents=True)
    img = cv2.imread(str(file))  
    img = cv2.resize(img, (480, 640), interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(name,img)
    return name



#for file1 in Path(src).rglob("*.jpg"):
#resize_jpg(str(file1))

for file in Path(src).rglob("*.jpg"):
    print(str(file))
#    file_resized = resize_jpg(str(file))
    proc(str(file))
