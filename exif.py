#ecoding:utf-8
import datetime
from PIL import Image
import piexif
import csv
import os
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default='')
    parser.add_argument('--left_trj', type=str, default='')
    parser.add_argument('--right_trj', type=str, default='')
    parser.add_argument('--output', type=str, default='')
    return parser.parse_args()

def Get_GPS_Info(left_trj_path, right_tri_path, image_name):
    with open(left_trj_path, 'r') as lf:
        left_lines = lf.readlines()
    with open(right_trj_path, 'r') as rf:
        right_lines = rf.readlines()
    left_lines = [line.strip('\n') for line in left_lines]
    left_lines = left_lines[21:]
    right_lines = [line.strip('\n') for line in right_lines]
    right_lines = right_lines[21:]

    lines = left_lines
    lines.append(right_lines)
	
    gps_infos = {}
    for line in lines:
        sub_str = [x for x in line.split(' ') if x]
        if(substr[5] == image_name):
	    gps_info = {
               "latitude": float(sub_str[3]), 
               "longitude": float(sub_str[4]), 
               "altitude": float(sub_str[5]), 
               "dop": 5.0
           }
    return gps_infos

def main(csv_path, image_root, save_root):
    csv_data = open(csv_path, "r")
    reader = csv.reader(csv_data)

    # 读取csv的每一行，跳过标题行
    for item in reader:
        if reader.line_num <= 1:
            continue
        lng = float(item[1])
        lat = float(item[2])
        alt=float(item[4])

        # 将经纬度与相对航高转为exif可用的经纬度与行高
        # exif需要的航高输入为(20000,2)格式，表示高度为20000/100米
        # exif需要的经度与维度为((12, 1), (20,1), (41000, 1000))格式表示12度20分41秒
        lng_exif = format_latlng(lng)
        lat_exif = format_latlng(lat)
        alt_exif = (int(100*round(alt,2)),100)
        _dict = {"alt": alt_exif, "lng": 
            lng_exif, "lat": lat_exif, "lng_ref":'East', "lat_ref":'North'}
        
        image_path = os.path.join(image_root, item[-1])
        save_path = os.path.join(save_root, item[-1])
        # 修改图片的exif
        read_modify_exif(image_path, save_path, _dict)
        print('{} finished'.format(item[-1]))


def format_latlng(latlng):
    """经纬度十进制转为分秒"""
    degree = int(latlng)
    res_degree = latlng - degree
    minute = int(res_degree * 60)
    res_minute = res_degree * 60 - minute
    seconds = round(res_minute * 60.0,3)
    return ((degree, 1), (minute,1), (int(seconds*1000), 1000))


def read_modify_exif(image_path,save_path, _dict):
    """ 读取并且修改exif文件"""
    img = Image.open(image_path)  # 读图
    exif_dict = piexif.load(img.info['exif'])  # 提取exif信息
   
    exif_dict['GPS'] = {0: (2, 2, 0, 0), 1: b'N', 2: _dict['alt'], 3: b'E', 4: _dict['lng'], 5: 0, 6: _dict['lat'], 10: b'3', 11: (50, 10)}    
	
    exif_bytes = piexif.dump(exif_dict)
    print('alt:{} lng:{} lat:{}'.format(exif_dict['GPS'][piexif.GPSIFD.GPSAltitude], exif_dict['GPS'][piexif.GPSIFD.GPSLongitude], exif_dict['GPS'][piexif.GPSIFD.GPSLatitude]))
    img.save(save_path, "jpeg", exif=exif_bytes)  # 保存
    

def check_folder(path_list):
    """输入为文件夹列表,文件夹不存在则创建"""
    for path in path_list:
        if not os.path.exists(path):
            os.mkdir(path)


if __name__ == "__main__":
    csv_path = '/home/dennis/pure_python/odm/exif_write/exif_data/from/pos.csv'
    image_root = '/home/dennis/pure_python/odm/exif_write/exif_data/from'
    save_root = '/home/dennis/pure_python/odm/exif_write/exif_data/to'
    check_folder([csv_path, image_root, save_root])
    main(csv_path, image_root, save_root)
