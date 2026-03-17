"""
GPS经纬度转换 Android应用
基于Kivy框架开发
保留原PyQt5版本的所有功能
"""
import math
import os

# 坐标系转换常量
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626

a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方


def bd09_to_gcj02(lon, lat):
    """BD-09 转 GCJ-02"""
    x = lon - 0.0065
    y = lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return gg_lng, gg_lat


def gcj02_to_wgs84(gg_lng, gg_lat):
    """GCJ-02 转 WGS84"""
    if out_of_china(gg_lng, gg_lat):
        return gg_lng, gg_lat
    
    dlat = _transformlat(gg_lng - 105.0, gg_lat - 35.0)
    dlng = _transformlng(gg_lng - 105.0, gg_lat - 35.0)
    radlat = gg_lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = gg_lat + dlat
    mglng = gg_lng + dlng
    return gg_lng * 2 - mglng, gg_lat * 2 - mglat


def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 * math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 * math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 * math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 * math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 * math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 * math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def out_of_china(lng, lat):
    """判断是否在国内"""
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)


def convert_bd09_to_wgs84(lon, lat):
    """BD-09 直接转 WGS84"""
    lon_gcj02, lat_gcj02 = bd09_to_gcj02(lon, lat)
    lon_wgs84, lat_wgs84 = gcj02_to_wgs84(lon_gcj02, lat_gcj02)
    return lon_wgs84, lat_wgs84
