import requests
import random


def __call_baidu(query_str):
    """调用百度api
    返回值:
    "网络访问异常"  错误
    "获取数据异常"  错误
    0 未知路况
    1 畅通
    2 缓行
    3 拥堵
    4 严重拥堵
    """
    try:
        r = requests.get(query_str)
        data = r.json()
    except:
        return "网络访问异常"

    if data['status'] == 0:
        # 正常获得路况数据
        return data['evaluation']['status']
    else:
        return "获取数据异常"


def api_traffic(data):
    """把api返回值转换成传感器的值 可以自行修改为合适的函数"""
    if type(data) == int:
        if data == 0:
            return 1
        elif data == 1:
            return 5 + random.randint(1,2)
        elif data == 2:
            return 10 + random.randint(2,3)
        elif data == 3:
            return 15 + random.randint(3,5)
        elif data == 4:
            return 20 + random.randint(3,5)
        else:
            return 0
    else:
        return 1


def get_NS_traffic():
    query_str = "http://api.map.baidu.com/traffic/v1/road?road_name=大学城中路&city=重庆市&ak=YvRnhfSnmgcgalCk0fPW5wRHbl1me6nG"
    return api_traffic(__call_baidu(query_str))


def get_WE_traffic():
    query_str = "http://api.map.baidu.com/traffic/v1/road?road_name=大学城南路&city=重庆市&ak=YvRnhfSnmgcgalCk0fPW5wRHbl1me6nG"
    return api_traffic(__call_baidu(query_str))
