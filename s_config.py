import numpy as np

# 路径
PATH_BASE = '/mnt/lustre/yangshifu/release/linux-x86_64server'   # 梁鼎的批处理工具路径
gt_rgb = "/mnt/lustre/yangshifu/testset/2d/detect/tongyong/gt_20180615.txt"     # rgb数据集的gt文件路径
gt_ir = "/mnt/lustre/yangshifu/testset/3d/base_test_data/vivo-detect_ir_test_new_gt.clean.txt"      # dt数据集的gt文件路径


types = ('detect', 'liveness', 'verify', 'eyestate', 'landmark')    # 支持测试类型
images = ('png', 'jpg', 'yuv', 'ir', 'gray16')    # 支持图片类型

# 睁眼闭眼标识
eye_open = ['003/', '004/', '005/', '006/', '007/', '009/', '011/', '013/', '014/', '015/', '016/', '017/', '018/',
            '019/', '020/', '021/', '022/', '023/', '024/', '025/', '027/', '029/', '031/', '033/', '038/', '039/',
            '040/', '041/', '042/', '043/', '044/', '045/', '046/', '047/', '048/', '049/', '050/', '051/', '052/',
            '053/', '054/', '055/', '056/', '057/', '058/', '059/', '060/', '061/', '062/', '063/', '064/', '065/',
            '066/', '067/', '068/', '069/', '070/', '071/', '072/']         # 睁眼
eye_close = ['001/', '002/', '008/', '010/', '012/', '026/', '028/', '030/', '032/', '034/', '035/', '036/', '037/',
             '073/', '074/', '075/', '076/']        # 闭眼

# 基本配置信息
is_wait_env_free = True        # 其他测试正在进行时，是否等到环境空闲时执行，默认True，一直等待
is_wait_finish = True       # 是否等待脚本执行完成
liveness_flag = 'human_test/'  # 图片真人标识或者单帧的睁闭眼的睁眼标识, 如有多个目录为真人，则用列表或元祖来设置flag，如北京数据：['Enroll', 'Real']

# 阈值配置
liveness_score_thres = 0.95     # 活体阈值
verify_score_thres = 0.7        # 比对阈值
eye_open_thres = 9.5           # 睁闭眼是否睁眼阈值
eye_valid_thres = 9.5          # 睁闭眼是否有效阈值
fprs=[(0.1 - 0.01*p) for p in np.arange(0, 10)]      # 写roc的fprs

# 多帧策略配置参数
is_use_sequence = False     # 采用多帧策略时，设置为True，"eyestate"将开启时序模式来判断睁闭眼。此时，输入的列表中，每一段序列靠空行分隔开。
is_line_sep = False         # 多帧模型跑非多帧策略时，文件列表里每行需要采用空格隔开，则设置该值为True


# 服务器配置
linux_ip = "172.20.17.200"      # 深圳服务器ip，除此ip外其他均视为集群，数据需要回传到该ip所在服务上
collect_result = "/opt/test_tools/release/linux-x86_64server/result"    # 结果路径


cmd = {
    "liveness": "nohup ./run -l output/files.txt > liveness.log 2>&1 & ",
    "detect": "nohup ./run -d output/files.txt > detect.log 2>&1 & ",
    "verify": "nohup ./run -r output/i_enroll.txt output/i_real.txt > verify.log 2>&1 &",
    "eyestate": "nohup ./run -e output/files.txt > eyestate.log 2>&1 &",
    "align": "nohup ./run -m output/files.txt > align.log 2>&1 &"
}
