# batch_test
based on faceunlock_test_general of liangding
测试的数据集进行批处理

## 功能
1. 提供配置文件
2. 可以设置定时任务
3. 是否保持等待
4. 写配置文件
5. 已存在任务运行时等待
6. 结果写数据库
7. 从文件中读取命令执行，可以配置执行多种不同方式的命令，文件为json文件。



{
    "liveness":
    [{
        "data_path": "",
        "wait": true,
        "ext": 'jpg',
        "time": '10:00',
        "model": {
            "align": "models/align/M_Align_occlusion_106_1.6.4.model",
            "detect": "models/detect/M_Detect_Hunter_SmallFace_Gray_360_4.7.4.model",
            "verify": "models/verify/M_Verify_MimicG2Pruned_Common_3.67.0.model",
            "liveness": "models/liveness/",
        }
    },
    {
        "data_path": "",
        "wait": true,
        "ext": 'yuv',
        "time": '10:00',
        "model": {
            "align": "models/align/M_Align_occlusion_106_1.6.4.model",
            "detect": "models/detect/M_Detect_Hunter_SmallFace_Gray_360_4.7.4.model",
            "verify": "models/verify/M_Verify_MimicG2Pruned_Common_3.67.0.model",
            "liveness": "models/liveness/",
        }
    },
    ]
    "verify":
    [{
        "data_path": "",
        "wait": true,
        "ext": 'jpg',
        "time": '10:00',
        "model": {
            "align": "models/align/M_Align_occlusion_106_1.6.4.model",
            "detect": "models/detect/M_Detect_Hunter_SmallFace_Gray_360_4.7.4.model",
            "verify": "models/verify/M_Verify_MimicG2Pruned_Common_3.67.0.model",
            "liveness": "models/liveness/",
        }
    },
    {
        "data_path": "",
        "wait": true,
        "ext": 'yuv',
        "time": '10:00',
        "model": {
            "align": "models/align/M_Align_occlusion_106_1.6.4.model",
            "detect": "models/detect/M_Detect_Hunter_SmallFace_Gray_360_4.7.4.model",
            "verify": "models/verify/M_Verify_MimicG2Pruned_Common_3.67.0.model",
            "liveness": "models/liveness/",
        }
    },
    ]
}
