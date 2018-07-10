#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Google style docstrings.
Example:
    <scripts-name> --help
"""
import os
import sys
import shutil
import argparse
import socket
import multiprocessing

def listdir_recursively(path):
    result = []
    for dirpath, dirs, files in os.walk(path):
        for f in files:
            file_path = os.path.join(dirpath, f)
            result.append(file_path)
    assert path[-1] != '/'
    for i in range(len(result)):
       result[i] = result[i][len(path) + 1:]
    return result

def main():
    default_description = '该工具用于对将小米自带相机采集软件的数据整理成测试组可以使用的结构'
    parser = argparse.ArgumentParser(prog = "PROG", description=default_description)
    parser.add_argument('-i', '--input_folder',  type = str, required=True)
    parser.add_argument('-o', '--output_folder', type = str, required=False, default='', help='[default = input_folder + .sample]')
    args = parser.parse_args()
    if args.input_folder[-1] == '/':
        args.input_folder = args.input_folder[:-1]
    if not args.output_folder:
        args.output_folder = args.input_folder + '.sample'
    print(('input_folder : {:s}'.format(args.input_folder)))
    print(('output_folder: {:s}'.format(args.output_folder)))

    list_src = listdir_recursively(args.input_folder)
    print('num src : {:d}'.format(len(list_src)))

    dict_depth = {}
    dict_depth_repeat = {}
    dict_nir_all = {} # 3 nir + 1 nir_spot
    dict_rgb = {}
    # xxx/???_?_depth.gray16 + xxx/???_?.gray16 + xxx/???_?.gray16 + rgb/???.jpg -> xxx 
    for src in list_src:
        folder, name = os.path.split(src)
        if name[-13:] == '_depth.gray16' and len(name) != 36:
            continue
        key = folder
        value = src
        if name[-13:] == '_depth.gray16':
            if key not in dict_depth:
                dict_depth[key] = value
            else:
                dict_depth_repeat[key] = value
        elif name[-7:] == '.gray16':
            dict_nir_all.setdefault(key, ['','','',''])
            dict_nir_all[key][int(name[-8])] = value
        elif name[-4:] == '.jpg':
            dict_rgb[key] = value

    print('num of folders in which multiple depth files exist: {}'.format(len(dict_depth_repeat)))
    for key in dict_depth_repeat.keys():
        dict_depth.pop(key, None)
        dict_nir_all.pop(key)
        dict_rgb.pop(key, None)
        #print('{}'.format(key))
    print('num of folders in which one depth file exists: {}'.format(len(dict_depth)))

    # if nir_spot is the first of the 4, find the next file to be nir (without spot); else find the pre
    list_sample_folder = []
    list_sample_depth  = []
    list_sample_nir_spot = []
    list_sample_nir = []
    list_sample_rgb = []
    index_rgb = 0
    for key, value in dict_depth.items():
        list_nirs = dict_nir_all[key]
        order = int(value[-14])
        if order != 0:
            if list_nirs[order-1]=='':#can't find corresponding nir
                continue
            else:
                list_sample_nir.append(list_nirs[order-1])
        else: #value[-14] == '0'
            if list_nirs[1]=='':#can't find corresponding nir
                continue
            else:
                list_sample_nir.append(list_nirs[1])
        list_sample_folder.append(key)
        list_sample_depth.append(value)
        list_sample_nir_spot.append(list_nirs[order])
        if key in dict_rgb:
            list_sample_rgb.append(dict_rgb[key])
        else:
            list_sample_rgb.append("")
 
    print('num sample: {:d}'.format(len(list_sample_folder)))

    for folder in list_sample_folder:
        dst = os.path.join(args.output_folder, folder)
        if not os.path.exists(dst):
            os.makedirs(dst)

    NAME_DEPTH = 'origin_depth'
    NAME_NIR_SPOT = 'origin_nir_spot'
    NAME_NIR = 'origin_nir'
    NAME_RGB = 'origin_color'
    shared_index = multiprocessing.Value('i', 0)
    def ProcessWorker():
        while True:
            i = 0
            with shared_index.get_lock():
                i = shared_index.value
                shared_index.value += 1
            if i >= len(list_sample_folder):
                break

            def log(info):
                print_flag = (i==len(list_sample_folder)-1 or i%100==0 or i<10)
                print_info = 'Init {:s} {:11s} {:d}/{:d} {:s}'.format(
                    socket.gethostname(), 
                    multiprocessing.current_process().name, 
                    i, 
                    len(list_sample_folder), 
                    list_sample_folder[i])
                if print_flag:
                    print(print_info, info)
                    sys.stdout.flush()
            
            name = os.path.join(args.output_folder, list_sample_folder[i], NAME_DEPTH) + '.raw'
            if not os.path.exists(name):
                shutil.copyfile(os.path.join(args.input_folder, list_sample_depth[i]), name)

            name = os.path.join(args.output_folder, list_sample_folder[i], NAME_NIR_SPOT) + '.raw'
            if not os.path.exists(name):
                shutil.copyfile(os.path.join(args.input_folder, list_sample_nir_spot[i]), name)

            name = os.path.join(args.output_folder, list_sample_folder[i], NAME_NIR) + '.raw'
            if not os.path.exists(name):
                shutil.copyfile(os.path.join(args.input_folder, list_sample_nir[i]), name)

            name = os.path.join(args.output_folder, list_sample_folder[i], NAME_RGB) + '.jpg'
            if list_sample_rgb[i] != '' and not os.path.exists(name):
                shutil.copyfile(os.path.join(args.input_folder, list_sample_rgb[i]), name)
                
            log('OK')

    list_process = []
    for i in range(multiprocessing.cpu_count()):
        process = multiprocessing.Process(target=ProcessWorker)
        list_process.append(process)
        process.start()
    for process in list_process:
        process.join()
    print('num src : {:d}'.format(len(list_src)))
    print('num sample: {:d}'.format(len(list_sample_folder)))
    print('num valid rgb: {:d}'.format(len([f for f in list_sample_rgb if f != ''])))


if __name__ == "__main__":
    main()
