#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author        :   yuyong
# @Created Time  :   2020年05月14日 星期四 16时15分16秒
# @File Name     :   extract_gps.py
import os.path as osp
import json

import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--left_trj', type=str, default='/data1/yuyong/stereo/stereo_hdmap_20191204_beijing/Cam1.trj')
    parser.add_argument('--right_trj', type=str, default='/data1/yuyong/stereo/stereo_hdmap_20191204_beijing/Cam2.trj')
    parser.add_argument('--output', type=str, default='/home/yuyong/git/OpenSfM/data/hd_stereo/exif_overrides.json')
    return parser.parse_args()


def read_trj(trj_path):
    with open(trj_path, 'r') as f:
        lines = f.readlines()
    lines = [line.strip('\n') for line in lines]
    lines = lines[21:]
    gps_infos = {}
    for line in lines:
        sub_str = [x for x in line.split(' ') if x]
        gps_info = {
            "latitude": float(sub_str[3]), 
            "longitude": float(sub_str[4]), 
            "altitude": float(sub_str[5]), 
            "dop": 5.0
        }
        gps_infos[sub_str[1]+'.jpg'] = {"gps": gps_info}
    return gps_infos

def write_exif_json(trj_ids, output):
    gps_infos = {}
    for trj_id in trj_ids:
        gps_info = read_trj(trj_id)
        gps_infos.update(gps_info)
    print(len(gps_infos))
    with open(output, 'w') as f:
        json.dump(gps_infos, f, indent=4)


def main():
    args = parse_args()

    trj_ids = []
    if args.left_trj:
        trj_ids.append(args.left_trj)
    if args.right_trj:
        trj_ids.append(args.right_trj)

    print(trj_ids)
    write_exif_json(trj_ids, args.output)


if __name__ == '__main__':
    main()
