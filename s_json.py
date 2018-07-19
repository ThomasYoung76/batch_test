#!/usr/bin/env python3
"""
Created on 2018/7/10

@author: yangshifu
@mail: yangshifu@sensetime.com
"""
import json
from pprint import pprint


def get_params(json_file):
    val_json = json.load(open(json_file))
    list_params = []
    list_config = []
    params = ['id', 'test_type', 'data_path', 'ext', 'time', 'section']
    config = ['id', 'model', 'input', 'force_resize_max']
    all_id = []
    for type_ in val_json:
        t_type = val_json[type_]
        for i in range(len(t_type)):
            dict_all = t_type[i]
            if int(dict_all['id']) < 0:
                continue
            id_ = dict_all['id']
            dict_params = dict([(k, dict_all.get(k)) for k in params])
            dict_config = dict([(k, dict_all.get(k)) for k in config])
            list_params.append(dict_params)
            list_config.append(dict_config)
            all_id.append(int(id_))
    all_id.sort()
    list_params.sort(key=lambda x: int(x['id']))
    list_config.sort(key=lambda x: int(x['id']))
    return all_id, list_params, list_config


def get_config_by_id(json_file, id_):
    val_json = json.load(open(json_file))
    for key_1 in val_json:
        val_1 = val_json[key_1]
        for i in range(len(val_1)):
            dict_all = val_1[i]
            id_val = dict_all['id']        # 命令id对应的值
            if int(id_val) == id_:
                return dict_all


def left_join_json(json_file_left, json_file_right, id_):
    """ 以左边json文件中的关键字为关键字，链接右边的json文件中id对应的数据"""
    val_left = json.load(open(json_file_left))
    val_right = get_config_by_id(json_file=json_file_right, id_=id_)
    for key1 in val_left:
        val_left_first = val_left[key1]
        val_right_first = val_right.get(key1, None)
        if not isinstance(val_left_first, dict):
            # 第一层json值处理
            if key1 in val_right:
                val_left[key1] = val_right[key1]
        else:
            # 若存在第二层json值则处理
            if val_right_first:
                for key2 in val_left_first:
                    if key2 in val_right_first:
                        val_left[key1][key2] = val_right_first[key2]

    # 覆盖json_file_left文件
    json.dump(val_left, open(json_file_left, 'w'), separators=(',', ':'), indent=4)


if __name__ == "__main__":
    # all_id, params, configs = get_params('batch.json')
    # for i in range(len(all_id)):
    #     print(params[i])
    # pprint(get_config_by_id('input/batch.json', id_=-1))
    dict_config = left_join_json('input/config.json', 'input/batch.json', id_=0)
