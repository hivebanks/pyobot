import json
import datetime, time
import urllib
from urllib import request
import threading
import os
from djgo.urls import common

# url = "http://ccvt_test.fnying.com/api"
url = common.urls
print(url)
exit()

# url = a.url()


#--------------定时任务文件----------------#


#调用接口循环判断
# def set_timer():
#     while True:
#         data = request.urlopen(url+"/bot/timer.php").read()
#         data_json = json.loads(data.decode("utf-8"))
#         dict = data_json['rows']
#         # dumps 将数据转换成字符串
#         json_str = json.dumps(dict)
#
#         # loads: 将 字符串 转换为 字典
#         new_dict = json.loads(json_str)
#
#         #图片下载到本地
#         for i in new_dict:
#             if int(i['send_type']) == 2:
#
#                 address = "../static/"+i['id']+".jpg"
#                 # 先删除本地文件
#                 if os.path.exists(address):
#                     os.remove(address)
#
#                 urllib.request.urlretrieve(i['content'], address)
#
#         with open("../json/timer.json", "w") as f:
#             json.dump(new_dict, f)
#
#         # 循环日期或周几生成本地文件
#         # d = request.urlopen(url+"/bot/get_date.php").read()
#         # d_json = json.loads(d.decode("utf-8"))
#         # dict2 = d_json['rows']
#         # # dumps 将数据转换成字符串
#         # json_str2 = json.dumps(dict2)
#         #
#         # # loads: 将 字符串 转换为 字典
#         # new_dict2 = json.loads(json_str2)
#         # # print(new_dict2)
#         #
#         # with open("./json/date.json", "w") as f:
#         #     json.dump(new_dict2, f)
#
#         # 每30秒调一次接口
#         time.sleep(30)
#
#
#
#
# # 每天半夜10：10统计今日
# def send_money_to_ccvt():
#     while True:
#         now = datetime.datetime.now()
#         if now.hour == 22 and now.minute == 10:
#             request.urlopen(url + "/crontab/send_money_ccvt.php").read()
#         # 每隔60秒检测一次
#         time.sleep(60)
#
#
# threads = []
# # 定时任务生成json
# set_timer = threading.Thread(target=set_timer)
# threads.append(set_timer)
#
# # 每天半夜10：10统计今日
# send_money_to_ccvt = threading.Thread(target=send_money_to_ccvt)
# threads.append(send_money_to_ccvt)
#
# for t in threads:
#     t.start()
# for t in threads:
#     t.join()




