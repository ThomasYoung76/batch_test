#-*- coding:utf-8 -*-


import os
import pandas as pd
map_1 = {
    "03":"有遮挡一只眼睛关键点遮挡，一只闭眼正常光遮住部分关键点近视镜",
    "04":"有遮挡一只眼睛关键点遮挡，一只闭眼正常光不遮住关键点(戴在额头上或眼睛以下)近视镜",
    "05":"有遮挡一只眼睛关键点遮挡，一只闭眼正常光不遮住关键点(戴在额头上或眼睛以下)佩戴鸭舌帽",
    "06":"有遮挡一只眼睛关键点遮挡，一只闭眼正常光不遮住关键点(戴在额头上或眼睛以下)佩戴鸭舌帽加黑框眼镜",
    "07":"有遮挡一只眼睛关键点遮挡，一只闭眼正常光不遮住关键点(戴在额头上或眼睛以下)佩戴有色透明眼镜",
    "09":"有遮挡一只眼睛关键点遮挡，一只闭眼暗光近视镜",
    "11":"有遮挡一只眼睛关键点遮挡，一只闭眼逆光近视镜",
    "13":"有遮挡一只眼睛关键点遮挡，一只闭眼强光近视镜",
    "14":"有遮挡一只眼睛关键点遮挡，一只睁眼正常光遮住关键点纯黑墨镜",
    "15":"有遮挡一只眼睛关键点遮挡，一只睁眼正常光遮住部分关键点纯黑墨镜",
    "16":"有遮挡一只眼睛关键点遮挡，一只睁眼正常光遮住部分关键点近视镜",
    "17":"有遮挡一只眼睛关键点遮挡，一只睁眼正常光不遮住关键点(戴在额头上或眼睛以下)近视镜",
    "18":"有遮挡一只眼睛关键点遮挡，一只睁眼正常光不遮住关键点(戴在额头上或眼睛以下)佩戴鸭舌帽加黑框眼镜",
    "19":"有遮挡一只眼睛关键点遮挡，一只睁眼正常光不遮住关键点(戴在额头上或眼睛以下)佩戴有色透明眼镜",
    "20":"有遮挡一只眼睛关键点遮挡，一只睁眼暗光纯黑墨镜",
    "21":"有遮挡一只眼睛关键点遮挡，一只睁眼暗光近视镜",
    "22":"有遮挡一只眼睛关键点遮挡，一只睁眼逆光纯黑墨镜",
    "23":"有遮挡一只眼睛关键点遮挡，一只睁眼逆光近视镜",
    "24":"有遮挡一只眼睛关键点遮挡，一只睁眼强光纯黑墨镜",
    "25":"有遮挡一只眼睛关键点遮挡，一只睁眼强光近视镜",
    "27":"有遮挡双眼关键点遮挡正常光近视镜",
    "29":"有遮挡双眼关键点遮挡暗光近视镜",
    "31":"有遮挡双眼关键点遮挡强光近视镜",
    "33":"有遮挡双眼关键点遮挡逆光近视镜",
    "38":"无遮挡一睁一闭正常光",
    "39":"无遮挡一睁一闭逆光",
    "40":"无遮挡一睁一闭暗光",
    "41":"无遮挡一睁一闭强光",
    "42":"无遮挡眯眼正常光双眼眯成一条线",
    "43":"无遮挡眯眼正常光双眼半眯",
    "44":"无遮挡眯眼正常光一只眯，一只睁",
    "45":"无遮挡眯眼正常光一只眯，一只闭",
    "46":"无遮挡眯眼强光双眼眯成一条线",
    "47":"无遮挡眯眼强光双眼半眯",
    "48":"无遮挡眯眼强光一只眯，一只睁",
    "49":"无遮挡眯眼强光一只眯，一只闭",
    "50":"无遮挡眯眼逆光双眼眯成一条线",
    "51":"无遮挡眯眼逆光双眼半眯",
    "52":"无遮挡眯眼逆光一只眯，一只睁",
    "53":"无遮挡眯眼逆光一只眯，一只闭",
    "54":"无遮挡眯眼暗光双眼眯成一条线",
    "55":"无遮挡眯眼暗光双眼半眯",
    "56":"无遮挡眯眼暗光一只眯，一只睁（放松状态）",
    "57":"无遮挡眯眼暗光一只眯，一只闭（放松状态）",
    "58":"无遮挡双眼睁眼正常光两眼正常睁眼",
    "59":"无遮挡双眼睁眼正常光两眼睁大眼",
    "60":"无遮挡双眼睁眼正常光佩戴鸭舌帽",
    "61":"无遮挡双眼睁眼正常光斜视",
    "62":"无遮挡双眼睁眼正常光耸鼻",
    "63":"无遮挡双眼睁眼正常光大小眼",
    "64":"无遮挡双眼睁眼逆光两眼正常睁眼",
    "65":"无遮挡双眼睁眼逆光两眼睁大眼",
    "66":"无遮挡双眼睁眼逆光佩戴鸭舌帽",
    "67":"无遮挡双眼睁眼逆光斜视",
    "68":"无遮挡双眼睁眼逆光耸鼻",
    "69":"无遮挡双眼睁眼逆光大小眼",
    "70":"无遮挡双眼睁眼强光两眼正常睁眼",
    "71":"无遮挡双眼睁眼强光两眼睁大眼",
    "72":"无遮挡双眼睁眼强光佩戴鸭舌帽"    
}
map_2 = {
    "01":"有遮挡一只眼睛关键点遮挡，一只闭眼正常光遮住关键点纯黑墨镜",
    "02":"有遮挡一只眼睛关键点遮挡，一只闭眼正常光遮住多半部分关键点（只留小部分眼角出来）纯黑墨镜",
    "08":"有遮挡一只眼睛关键点遮挡，一只闭眼暗光纯黑墨镜",
    "10":"有遮挡一只眼睛关键点遮挡，一只闭眼逆光纯黑墨镜",
    "12":"有遮挡一只眼睛关键点遮挡，一只闭眼强光纯黑墨镜",
    "26":"有遮挡双眼关键点遮挡正常光纯黑墨镜",
    "28":"有遮挡双眼关键点遮挡暗光电镀墨镜",
    "30":"有遮挡双眼关键点遮挡强光纯黑墨镜",
    "32":"有遮挡双眼关键点遮挡逆光纯黑墨镜",
    "34":"无遮挡两眼闭眼正常光",
    "35":"无遮挡两眼闭眼逆光",
    "36":"无遮挡两眼闭眼暗光",
    "37":"无遮挡两眼闭眼强光",
    "73":"有遮挡正常光双眼闭眼佩戴黑框近视镜",
    "74":"有遮挡强光双眼闭眼佩戴黑框近视镜",
    "75":"有遮挡逆光双眼闭眼佩戴黑框近视镜",
    "76":"有遮挡暗光双眼闭眼佩戴黑框近视镜"    
}

input_path = "/home/sensetime/raygong/Work/Data/FaceUnlock/data/ocular/FaceUnlock_1.4.3-ocular-P1"
result = {}
for root, dirname, file in os.walk(input_path):
    for f in file:
        if f.endswith(".xls"):
            sence_id = root.split("/")[-2]
            times = root.split("/")[-1]
            ocular_pass_num = 0
            verify_pass_num = 0
            liveness_pass_num = 0
            unlock_num = 0
            total_num = 0
            records = pd.read_excel(root + os.sep + f)
            total_num = len(records)
            if records.loc[total_num-1,'睁闭眼'] == "通过":
                ocular_pass_num += 1
            if records.loc[total_num-1,'比对'] == "通过":
                verify_pass_num += 1
            if records.loc[total_num-1,'活体'] == "通过":
                liveness_pass_num += 1
            if records.loc[total_num-1,'结果'] == "通过":
                unlock_num += 1
            if sence_id in result.keys():

                result[sence_id][0] += total_num
                result[sence_id][1] += unlock_num
                result[sence_id][2] += ocular_pass_num
                result[sence_id][3] += verify_pass_num
                result[sence_id][4] += liveness_pass_num
            else:
                result[sence_id] = [total_num, unlock_num, ocular_pass_num, verify_pass_num, liveness_pass_num]
data = {}
data["睁眼"] = []
data["闭眼"] = []
#data["睁眼"] = [("用例编号","测试用例","总测试次数","解锁次数","总图片数","睁闭眼通过次数")]
#data["闭眼"] = [("用例编号","测试用例","总测试次数","解锁次数","总图片数","睁闭眼通过次数")]
for k in result.keys():
    if k in map_1.keys():
        data["睁眼"].append([k,map_1[k],20,result[k][1],result[k][0],result[k][2],result[k][3],result[k][4]])
    else:
        data["闭眼"].append([k,map_2[k],20,result[k][1],result[k][0],result[k][2],result[k][3],result[k][4]])

writer = pd.ExcelWriter("output.xls", engine='xlsxwriter')
for i in data.keys():
    df = pd.DataFrame(data[i][0:],columns=("用例编号","测试用例","总测试次数","解锁次数","总图片数","睁闭眼通过次数","比对通过次数","活体通过次数"))
    df[["用例编号"]] = df[["用例编号"]].astype(int)
    dd = df.sort_values(by="用例编号") 
    dd.to_excel(writer, sheet_name=i, index=False) 
dd.to_excel("output.xls", index=False)
writer.save()