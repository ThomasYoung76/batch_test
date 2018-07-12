#!/usr/bin/env python3
"""
Created on 2018/7/10

@author: yangshifu
@mail: yangshifu@sensetime.com
"""
import json


def get_params(json_file):
    val_json = json.load(open(json_file))
    list_params = []
    list_config = []
    params = ['id', 'test_type', 'data_path', 'ext', 'time']
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


if __name__ == "__main__":
    all_id, params, configs = get_params('batch.json')
    for i in range(len(all_id)):
        print(params[i])
