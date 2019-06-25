# coupon_code = "@小助手 兑换码ccvt-sfmf86h8"
#
#
# coupon_code = coupon_code.replace('@小助手', '')
#
#
# "28EBFAE0-C750-C811-E6E0-6B89DFAA2A53"+"_check_login"
#
#
# if "ccvt-" in coupon_code:
#     print(''.join([i if ord(i) < 128 else ' ' for i in coupon_code]).replace(' ', ''))
# else:
import json
import urllib
from urllib import request
import datetime, time
#     print(222)
url = "http://ccvt_test.fnying.com/api"
#
# s = "monday-tuesday-wednesday-thursday-friday-saturday"
#
# ss = s.split("-")
#
# print(ss)



# s = '"时光の流离"邀请"江上月"加入了群聊'
# s = '" 一株藤蔓"通过扫描"Spider"分享的二维码加入群聊'
# if ("邀请" in s) and ("加入了群聊" in s):
#     print(s.split("邀请")[0])
#     print(s.split("邀请")[1].replace('加入了群聊', '').replace('"', ''))
# elif ("通过扫描" in s) and ("加入群聊" in s):
#     print(s.split("通过扫描")[0].replace('"', ''))
# s = 'sunday'
# if "-" in s:
#     ss = s.split("-")
# else:
#     ss = [s]
# print(ss)

# array = ['9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21']
# now = datetime.datetime.now()
# now_hour = now.hour
# now_minute = now.minute
# if (str(now_hour) in array) and int(now_minute) == 52:
#     print(111)
# else:
#     print(22222)
#
#
# a = time.localtime()
# week = time.strftime("%A", a).lower()
# print(week)
#
#
# # 读取本地group文件内容
# def get_group_json():
#     with open("../json/group.json", 'r') as load_f:
#         load_dict = json.load(load_f)
#         return load_dict
#
#
# rows = get_group_json()
# print(rows)
import json
import os
import oss2
import redis
import sys
import requests
import threading
import random
sys.path.append("..")
from redis_pool import POOL

textmod={"action": "long2short", "long_url": "https://item.jd.com/12041625.html"}
#json串数据使用
textmod = json.dumps(textmod).encode(encoding='utf-8')

header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',"Content-Type": "application/json"}
access_token = ""
url="https://api.weixin.qq.com/cgi-bin/shorturl?access_token="+access_token
req = request.Request(url=url, data=textmod, headers=header_dict)
res = request.urlopen(req)
res = res.read()
res = json.loads(res.decode())
print(res['short_url'])
print(res)




def Schedule(a, b, c):
    """
    a:已经下载的数据块
    b:数据块的大小
    c:远程文件的大小
    """
    per = 100.0*float(a*b)/float(c)
    if per > 100:
        per = 100
    print("a", a)
    print("b", b)
    print("c", c)
    print('{:.2f}%'.format(per))


# url = 'https://avatars1.githubusercontent.com/u/14261323?s=400&u=&v=4'
# local = 'mylogo.png'
# filename = urllib.request.urlretrieve(url, local, Schedule)
# # ('mylogo.png', <http.client.HTTPMessage object at 0x000001FD6491D6D8>)
# print(filename)
#
# conn = redis.Redis(connection_pool=POOL)
#
# new_rand_one = conn.srandmember('new_list')
# if new_rand_one:
#     new_rand_one = json.loads(new_rand_one.decode())
# #     print(new_rand_one)
# def check_login():
#     while True:
#         s = random.random()
#         # print(s)
#         time.sleep(1)

# threads = []
# for i in range(5000):
#     ti = threading.Thread(target=check_login, name=i)
#     threads.append(ti)
#
# for t in threads:
#     t.start()
# for t in threads:
#     t.join()

# top10 = conn.get('leave_top_message')
# top10 = json.loads(top10.decode())
# print(top10)


# list = conn.lpop('-C750-C811--')
# if list:
#     list = json.loads(list.decode())
#     print(list['name'])
# print(list)


# conn = redis.Redis(connection_pool=POOL)
# list = conn.lrange('ranking_change_record_2', 0, 20)
# if list:
#     for i in list:
#         record = json.loads(i.decode())
#         print(record)
#         print(record['wechat'])
# conn.ltrim('ranking_change_record_2', 20, 0)
#
#
# conte = "红包      12345"
# st = conte.replace(' ', ' ')
# st = st.split(' ')
# print(st)
# while '' in st:
#     st.remove('')
# print(len(st))
# print(st)
# print(st[1])




# time_list = conn.get("timer_12:0")
# if time_list:
#     time_list = json.loads(time_list.decode())
#     for i in time_list:
#         group_info = conn.get("group_info_" + i['group_id'])
#         print(group_info)
# else:
#     print(222)


# group_info = conn.get("group_info_82")
# if group_info:
#     group_info = json.loads(group_info.decode())
#     print(type(group_info['id']))
# else:
#     print(222)

# print(time_list)

















#
# data = request.urlopen(url+"/bot/timer.php").read()
# data_json = json.loads(data.decode("utf-8"))
# dict = data_json['rows']
# print(dict)
# # dumps 将数据转换成字符串
# json_str = json.dumps(dict)
#
# # loads: 将 字符串 转换为 字典
# new_dict = json.loads(json_str)
#
# #图片下载到本地
# for i in new_dict:
#     if int(i['send_type']) == 2:
#
#         address = "../../static/"+i['id']+".jpg"
#         print(address)
#         print(i['content'])
#         src_path = i['content']
#         urllib.request.urlretrieve(src_path, address)
#
# with open("../../json/timer.json", "w") as f:
#     json.dump(new_dict, f)


