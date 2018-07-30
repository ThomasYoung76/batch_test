import numpy as np

# 路径
PATH_BASE = '/mnt/lustre/yangshifu/release/linux-x86_64server'   # 梁鼎的批处理工具路径
gt_rgb = "/mnt/lustre/yangshifu/testset/2d/detect/tongyong/gt_20180615.txt"     # rgb数据集的gt文件路径
gt_ir = "/mnt/lustre/yangshifu/testset/3d/base_test_data/vivo-detect_ir_test_new_gt.clean.txt"      # dt数据集的gt文件路径


types = ('detect', 'liveness', 'verify','eyestate')    # 支持测试类型
images = ('png', 'jpg', 'yuv', 'ir', 'gray16')    # 支持图片类型

# 配置信息
is_wait_env_free = False        # 其他测试正在进行时，是否等到环境空闲时执行，默认False，直接中断当前测试
is_wait_finish = True       # 是否等待脚本执行完成
liveness_flag = 'photo/'   # 图片假人标识
liveness_score_thres = 0.99     # 活体阈值
verify_score_thres = 0.7        # 比对阈值
eye_open_thres = 9.5           # 睁闭眼是否睁眼阈值
eye_valid_thres = 9.5          # 睁闭眼是否有效阈值
fprs=[(0.1 - 0.01*p) for p in np.arange(0, 10)]      # 写roc的fprs
use_sequence = False     # 采用多帧策略时，设置为True，"eyestate"将开启时序模式来判断睁闭眼。此时，输入的列表中，每一段序列靠空行分隔开。


# 服务器配置
linux_ip = "172.20.17.200"      # 深圳服务器ip，除此ip外其他均视为集群，数据需要回传到该ip所在服务上
collect_result = ""


cmd = {
    "liveness": "nohup ./run -l output/files.txt > liveness.log 2>&1 & ",
    "detect": "nohup ./run -d output/files.txt > detect.log 2>&1 & ",
    "verify": "nohup ./run -r output/i_enroll.txt output/i_real.txt > verify.log 2>&1 &",
    "eyestate": "nohup ./run -e output/files.txt > eyestate.log 2>&1 &"
}
