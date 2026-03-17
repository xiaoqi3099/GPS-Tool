"""
百度地图API调用模块
"""
import requests
from urllib.parse import quote


class BaiduGeocodingAPI:
    def __init__(self, ak="8IcmA3zNitpqlmaA1HCYmpLc1cNvzjyL"):
        self.root_url = 'http://api.map.baidu.com/geocoding/v3/'
        self.output = 'json'
        self.ak = ak
    
    def geocode(self, address):
        """
        地理编码 - 地址转经纬度
        返回: (lon, lat) 或 (None, None)
        """
        add = quote(address)
        url = f"{self.root_url}?address={add}&output={self.output}&ak={self.ak}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and data.get("status") == 0:
                    if "result" in data and "location" in data["result"]:
                        lon = data["result"]["location"]["lng"]
                        lat = data["result"]["location"]["lat"]
                        return lon, lat
            return None, None
        except Exception as e:
            print(f"API请求错误: {e}")
            return None, None
    
    def reverse_geocode(self, lat, lon):
        """
        逆地理编码 - 经纬度转地址
        """
        url = f"{self.root_url}?location={lat},{lon}&output={self.output}&ak={self.ak}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and data.get("status") == 0:
                    return data.get("result", {}).get("formatted_address", "")
            return None
        except Exception as e:
            print(f"API请求错误: {e}")
            return None
