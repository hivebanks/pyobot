import json
import requests
import time

# url = 'http://phpmanong.cn/api/bot/timer.php'
# req = requests.get(url)
# dict = json.loads(req.text)['rows']
# #dumps 将数据转换成字符串
# json_str = json.dumps(dict)
#
# #loads: 将 字符串 转换为 字典
# new_dict = json.loads(json_str)
# print(new_dict)
#
# with open("timer.json", "w") as f:
#     json.dump(new_dict, f)
#     print("加载入文件完成...")

#生成本地json文件
def set_json():
    url = 'http://phpmanong.cn/api/bot/timer.php'
    req = requests.get(url)
    dict = json.loads(req.text)['rows']
    # dumps 将数据转换成字符串
    json_str = json.dumps(dict)

    # loads: 将 字符串 转换为 字典
    new_dict = json.loads(json_str)
    print(new_dict)

    with open("timer.json", "w") as f:
        json.dump(new_dict, f)
    #每5秒调一次接口
    time.sleep(5)
    set_json()
set_json()