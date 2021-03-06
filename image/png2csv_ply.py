import numpy as np
import cv2
from PIL import Image
from pathlib import Path
import argparse

png_file = "/home/SENSETIME/yangshifu/Desktop/201902191441468170.png"
width = 240
height = 180
file_parent = Path(png_file).parent
file_stem = Path(png_file).stem


# parse = argparse.ArgumentParser(description="convert png to csv or ply")
# parse.add_argument("-c", "--csv", action="store_true", default=False, help="only convert png to csv")


img = cv2.imread(png_file)
img = cv2.resize(img, (width, height))

img_1 = img[:, :, 0]    # depth图3个通道都是一样的,取其中一个通道即可

# 写csv文件
np.savetxt("{}/{}.csv".format(file_parent, file_stem), img_1, delimiter=',',fmt='%0.1f')

x = np.stack([np.arange(0, width) for i in range(height)])
y = np.stack([np.arange(0, height) for i in range(width)])

point_cloud = np.stack([x, y.T, img_1 * 3], axis=2)
print(point_cloud.shape)
point_cloud_ = point_cloud.reshape(-1, 3)

# 写点云图
with open("{}/{}.ply".format(file_parent, file_stem), 'w') as fa:
    fa.write("""ply
format ascii 1.0
comment Generated by sampleExport
element vertex {:.1f}
property float x
property float y
property float z
element face 0
property list uchar int vertex_index
end_header""".format(point_cloud.shape[0] * point_cloud.shape[1]))
    for i in point_cloud_:
        fa.write("{:.1f} {:.1f} {:.1f}\n".format(i[0], i[1], i[2]))

