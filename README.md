# 这个工具用来进行pc端批处理测试
（基于梁顶的工具）
主要功能：
1.每个测试集对应一个配置文件
2.支持gray16数据类型
3.设置定时任务
4.跑分前增加各种情况的检查点
5.通过文件连续执行多条命令，且命令中可以设置使用不同的模型及其他配置信息
6.通过命令id控制命令执行顺序，是否执行0，及是否进行版本比对
7.简单分析结果，执行多条命令时，给出每条命令的结果是否可能不合理
8.结果写数据库（待定）

## 要求：
### 第一步，环境准备工作：
- 运行init.sh, 命令：./init.sh000
- 根据实际情况修改s_config.py, 将PATH_BASE的值改为实际环境中梁鼎工具的目录， 例如：PATH_BASE = '/opt/test_tools/faceunlock_test_general'

### 第二步，准备好测试集，以及测试集对应的配置文件：
如测试集为：~/code/data/testset/2d/liveness/v2.6.41
则测试集对应的配置文件为：~/code/data/testset/2d/liveness/config/v2.6.41.json
（该json文件如果存在则代替梁鼎工具下的config.json文件，如果不存在，则config.json生效，建议配置，保证一个测试集对应一个配置文件）
# 配置文件v2.6.41.json的内容
{
    "model" : {
        "align": "models/align/M_Align_occlusion_106_1.6.4.model",
        "detect": "models/detect/M_Detect_Hunter_SmallFace_Gray_360_4.7.4.model",
        "verify": "models/verify/M_Verify_MimicG2Pruned_Common_3.67.0.model",
        "liveness": "models/liveness/",
        "head3d": "",
        "eyestate": "",
        "gaze_mn": ""
    },
    "input" : {
        "width" : 640,
        "height": 400,
        "orient": "top",
        "gray"  : true      # rgb图片则gray为False，3d图片为True
    },
    "intrinsic" : [
        480.422444, 0,  320.977978,
        0,  480.422444, 195.290545,
        0,  0,  1
    ],                      # 测试注视时才有用
    "eyestate_thres" : 0.8, # 睁闭眼阈值
    "feature_len" : 128,
    "force_resize_max": 0,
    "align_thres" : 0,      # align阈值，建议设置为0.1
    "verify_cropped": false,
    "input_prefix": "",
    "output_prefix": "",
    "save_aligned_img": false,
    "benchmark": true,      # 设置为False，可屏蔽接口的打印信息
    "use_snpe_gpu": true
}

### 第三步，根据实际情况修改s_config.py
is_wait_env_free = False        # 其他测试正在进行时，是否等到环境空闲时执行，默认False，不等环境空闲直接中断当前测试，
is_wait_finish = True       # 是否等待脚本执行完成
real_rgb_flag = 'human_test/ '   # rgb照片活体真人标识，
rgb_flag = 'photo/'   # rgb图片假人标识
raw_flag = 'hack/'  # 3d图片假人标志
fprs=[(0.1 - 0.01*p) for p in np.arange(0,10)]      # 设置写roc的fprs的取值范围和精度


### 第四步，运行批处理脚本
- 1. 立即执行测试：
    ./run -p liveness -d ~/code/data/testset/2d/liveness/v2.6.41 -e yuv
- 2. 定时执行：
    ./run -p liveness -d ~/code/data/testset/2d/liveness/v2.6.41 -e yuv -t 02:30
    注：该命令会将脚本定时到21点30分执行，如果当前时间已过21点30分则再下一天的21点30分执行。
- 3. 通过文件连续执行多项批处理测试：
    ./run -f input/liveness.json
    说明：
    1.配置liveness.json文件：
    每一个id对应一条批处理命令，如id=0, test_type、data_path、ext、time分别对应测试类型、数据集路径、文件类型、定时时间
    （定时时间为空则立即执行），model里的值、input值的如果设置了，则优先采用这里设置的值
    2.按id值从小到大的顺序执行
    3.id设置为负数（如-1），该命令将被忽略
    4.两条命令的id相同，且待测试的版本相同，且
    对比的结果，用于发送测试结果邮件。
    {
	"liveness":
	[{
			"id": 0,
			"test_type": "liveness",
			"data_path": "/mnt/lustre/yangshifu/testset/2d/liveness/v2.6.41",
			"ext": "yuv",
			"time": "",
			"model": {
				"align": "models/align/M_Align_occlusion_106_1.6.4.model",
				"detect": "models/detect/M_Detect_Hunter_SmallFace_Gray_360_4.7.4.model",
				"verify": "models/verify/M_Verify_MimicG2Pruned_Common_3.67.0.model",
				"liveness": "models/liveness/"
			},
			"input" : {
				"width" : 640,
				"height": 480,
				"orient": "right",
				"gray"  : false
			}
		}, {
			"id": 1,
			"test_type": "liveness",
			"data_path": "/mnt/lustre/yangshifu/testset/2d/liveness/v2.6.42",
			"ext": "yuv",
			"time": "",
			"model": {
				"align": "models/align/M_Align_occlusion_106_1.6.4.model",
				"detect": "models/detect/M_Detect_Hunter_SmallFace_Gray_360_4.7.4.model",
				"verify": "models/verify/M_Verify_MimicG2Pruned_Common_3.67.0.model",
				"liveness": "models/liveness/"
			}
		}
	],
	"verify":
	[{
			"id": -1,
			"test_type": "verify",
			"data_path": "",
			"ext": "jpg",
			"time": "10:00",
			"model": {
				"align": "models/align/M_Align_occlusion_106_1.6.4.model",
				"detect": "models/detect/M_Detect_Hunter_SmallFace_Gray_360_4.7.4.model",
				"verify": "models/verify/M_Verify_MimicG2Pruned_Common_3.67.0.model",
				"liveness": "models/liveness/"
			}
		}, {
			"id": -1,
			"test_type": "verify",
			"data_path": "",
			"ext": "jpg",
			"time": "10:00",
			"model": {
				"align": "models/align/M_Align_occlusion_106_1.6.4.model",
				"detect": "models/detect/M_Detect_Hunter_SmallFace_Gray_360_4.7.4.model",
				"verify": "models/verify/M_Verify_MimicG2Pruned_Common_3.67.0.model",
				"liveness": "models/liveness/"
			}
		}
	]
}

## 批处理步骤
>>> step 1: init_env  # 检查环境
>>> step 2: check_args  # 检查命令参数是否合理
>>> step 3: set_config  # 根据实际情况修改并检查配置文件
>>> step 4: prepare_data    # 准备文件list和labels
>>> step 5: execute     # 运行梁顶的工具跑分
>>> step 6: optimize_result # 优化结果，计算FRR和FAR及ROC等
