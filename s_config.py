import numpy as np

# 路径
PATH_BASE = '/mnt/lustre/yangshifu/release/linux-x86_64server'   # 梁鼎的批处理工具路径


types = ('liveness', 'verify', 'detect', 'eyestate', 'gaze', 'landmark')    # 支持测试类型
images = ('jpg', 'yuv', 'ir', 'gray16')    # 支持图片类型

# 配置信息
is_wait_env_free = False        # 其他测试正在进行时，是否等到环境空闲时执行，默认False，直接中断当前测试
is_wait_finish = True       # 是否等待脚本执行完成
rgb_flag = 'photo/'   # rgb图片假人标识
raw_flag = 'hack/'  # 3d图片假人标志
fprs=[(0.1 - 0.01*p) for p in np.arange(0, 10)]      # 写roc的fprs
verify_score_thres = 0.7

cmd = {
    "liveness": "nohup ./run -l output/files.txt > liveness.log 2>&1 & ",
    "detect": "nohup ./run -m output/files.txt > detect.log 2>&1 & ",
    "verify": "nohup ./run -r output/i_enroll.txt output/i_real.txt > verify.log 2>&1 &",
    "eyestate": "nohup ./run -e output/files.txt > eyestate.log 2>&1 &"
}


maps = {
    "bj": {
        "ip": "10.10.30.87",
        "testset": "/ssd/testset"
    },
    "sz": {
        "ip": "172.20.21.68",
        "testset": "/mnt/lustre/yangshifu/testset"
    },
    "local": {
        "ip": "172.20.17.200",
        "testset": "/home/andrew/code/data/testset"
    }
}
