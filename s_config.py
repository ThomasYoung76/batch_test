import os
import numpy as np

# 路径
PATH_BASE = '/mnt/lustre/yangshifu/faceunlock_test_general'   # 梁鼎的批处理工具路径
PATH_DATA = '/mnt/lustre/yangshifu/testset'       # 数据集根路径
PATH_DATA_2D = os.path.join(PATH_DATA, '2d')    # 深圳2d数据集路径
PATH_DATA_3D = os.path.join(PATH_DATA, '3d')    # 深圳3d数据集路径

# 配置信息
is_wait_env_free = False        # 其他测试正在进行时，是否等到环境空闲时执行，默认False，直接中断当前测试
is_wait_finish = True       # 是否等待脚本执行完成


# 写roc的fprs
fprs=[(0.1 - 0.01*p) for p in np.arange(0,10)]

data_set = {
    "liveness": {
        'file_type': 'yuv',
        'process': 'sample_liveness',
        'flag': 'photo/',
        'cmd': "nohup ./run -l output/files.txt > liveness.log 2>&1 & ",
        },
    "detect": {
        'file_type': 'jpg',
        'process': 'sample_liveness',
        'flag': 'photo/',
        'cmd': "nohup ./run -d output/files.txt > detect.log 2>&1 & ",
        },
    "verify": {
        'file_type': 'jpg',
        'process': 'sample_liveness',
        'flag': 'photo/',
        'cmd': "nohup ./run -r output/i_enroll.txt output/i_real.txt > verify.log 2>&1 &",
        }

}
