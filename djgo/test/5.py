from wxpy import *
import json
import requests
import datetime, time
from urllib import parse
from urllib import request
import os
import oss2
# import hashlib
# import random
# import base64
import threading


# 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
# auth = oss2.Auth('', '')
# # Endpoint以杭州为例，其它Region请按实际情况填写。
# bucket_name = 'pythonccvt'
# aliyun_url = 'oss-cn-hongkong.aliyuncs.com'
# bucket = oss2.Bucket(auth, aliyun_url, bucket_name)
# img_key = 'img/img.png'
# img_path = '../static/abc.png'
# result = bucket.put_object_from_file(img_key, img_path)
#
# url = bucket_name+"."+aliyun_url+"/"+img_key
#
#
# print(url)

# import redis
#
# r = redis.Redis(host='18.219.17.238',port=6379,password='Windwin2018')
# r.set('name',  'root')
# print(r.get('name').decode('utf8'))

#
# pool = redis.ConnectionPool(host='', port=6379, db=0, password='')   #实现一个连接池
# print(pool)
# r = redis.Redis(connection_pool=pool)
# r.set('foo', 'bar')
# print(r.get('foo').decode('utf8'))

# mems = []
# gr = self.bot.groups().search("CCVT创世首发群")[0]
# gr.update_group
# for g in gr.members:
#     mems.insert(0, g.name)
#
# mems = ','.join(mems)
#
# textmod = json.dumps({"group_id": "2", "group_name": "CCVT创世首发群", "members": mems})
#
# # print(textmod)
#
# header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
#                "Content-Type": "application/json"}
# urls = url + '/bot/4.php'
# response = requests.post(urls, data=textmod, headers=header_dict)
# print(response.text)


st = "  @Gavin       @阿助    赞 100"
conte = st.replace('@Gavin', '')

conte = "@阿助 赞 1000"
print(conte)
conte = conte.replace(' ', ' ')
# conte = conte.lstrip()
# print(conte)
st = conte.split(' ')
while '' in st:
    st.remove('')
print(st)
print(len(st))
if (len(st)==3 and ("赞" in st or "踩" in st)):
    print('333')
# if len(st)<3:
#     print('格式错误')
# else:
#     print(st[0].replace('@', ''))
#     if (st[1] == "赞") or (st[1] == "踩"):
#         print('格式错误')
#     print(st[1])
#     print(st[2])



