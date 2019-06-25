from wxpy import *
import json
import requests
import datetime, time
import urllib
from urllib import parse
from urllib import request
import os
import oss2
# import hashlib
# import random
# import base64
import threading
import djgo.common as a
import redis
import inspect
import ctypes
from djgo.redis_pool import POOL
import base64

url = a.url()
address = a.address()
conn = redis.Redis(connection_pool=POOL)

class Robot(object):
    def __init__(self, bot, us_id):
        self.bot = bot
        self.us_id = us_id
    #聊天
    def send_to_message(self):
        params = parse.urlencode({'us_id': self.us_id})
        data = request.urlopen(url + "/bot/get_qrcode.php?%s" % params).read()
        data_json = json.loads(data.decode("utf-8"))
        dict = data_json['rows']
        if int(dict['robot_alive']) != 1:

            # 获取机器人昵称，存入数据库
            params = parse.urlencode({'bot_name': self.bot.self.name, 'us_id': self.us_id})
            request.urlopen(url + "/bot/bot_qrcode.php?%s" % params).read()

            #判断登录，修改数据库
            if self.bot.alive == True:
                params = parse.urlencode({'robot_alive': 1, 'us_id': self.us_id})
                request.urlopen(url + "/bot/bot_alive.php?%s" % params)


            #单聊
            self.sel_frind_message()

            # 添加好友
            self.add_friends()

            #收集群聊信息
            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)
                # 获取机器人所有群插入数据库临时群表
                # params = parse.urlencode({'group_name': group_name.name, 'us_id': self.us_id})
                # request.urlopen(url + "/bot/temporary_group.php?%s" % params).read()

            group_list = conn.get('group_bot_' + self.us_id)
            if group_list:
                group_list = json.loads(group_list.decode())
                for name in group_list:
                    if name['name'] in all:
                        self.start_record_bot(name['name'], name['invite_code'])


            # 循环调用接口生成json,循环调用json判断时间
            # 注：不能写t1 = threading.Thread(target=self.set_timer())
            threads = []
            #判断登录
            ti = self.us_id+"_check_login"
            ti = threading.Thread(target=self.check_login, name=ti)
            threads.append(ti)
            #定时发送定时任务
            timer_run = self.us_id+"_timer_run"
            timer_run = threading.Thread(target=self.timer_run, name=timer_run)
            threads.append(timer_run)
            #判断一次接口最新数据库与本地生成的json是否相同，不同的数据，生成群聊对象
            judge_group_or_same = self.us_id+"_judge_group_or_same"
            judge_group_or_same = threading.Thread(target=self.judge_group_or_same, name=judge_group_or_same)
            threads.append(judge_group_or_same)
            # 每天定时播报地址
            this_day_send_address = self.us_id + "_this_day_send_address"
            this_day_send_address = threading.Thread(target=self.this_day_send_address, name=this_day_send_address)
            threads.append(this_day_send_address)
            # 通知荣耀积分排名变化用户
            ranking_change_record = self.us_id + "_ranking_change_record"
            ranking_change_record = threading.Thread(target=self.ranking_change_record, name=ranking_change_record)
            threads.append(ranking_change_record)
            # 每半个小时没人发言推送文章
            check_chat = self.us_id + "_check_chat"
            check_chat = threading.Thread(target=self.check_chat, name=check_chat)
            threads.append(check_chat)
            # 存储群成员
            storage_members = self.us_id + "_storage_members"
            storage_members = threading.Thread(target=self.storage_members, name=storage_members)
            threads.append(storage_members)

            # 中午12点推送top10留言
            send_leave_message = self.us_id + "_send_leave_message"
            send_leave_message = threading.Thread(target=self.send_leave_message, name=send_leave_message)
            threads.append(send_leave_message)
            # 中午12点推送top10群主排行榜
            send_group_cashback = self.us_id + "_send_send_group_cashbacke"
            send_group_cashback = threading.Thread(target=self.send_group_cashback, name=send_group_cashback)
            threads.append(send_group_cashback)
            # 随机奖励
            random_reward = self.us_id + "_random_reward"
            random_reward = threading.Thread(target=self.random_reward, name=random_reward)
            threads.append(random_reward)
            for t in threads:
                t.start()
            for t in threads:
                t.join()

    #杀死进程
    def async_raise(self, tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")



    # 每10分钟判断一次**分钟内是否有人聊天，如果没人聊天，推送文章
    def check_chat(self):
        while True:
            if self.bot.alive == False:
                # 杀死进程
                self.async_raise(threading.currentThread().ident, SystemExit)
            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)
            group_list = conn.get('group_bot_' + self.us_id)
            if group_list:
                group_list = json.loads(group_list.decode())
                for name in group_list:
                    if name['name'] in all:
                       if int(name['news_switch']) == 1:
                          now = datetime.datetime.now()
                          if (now.hour >= 8) and (now.hour < 22):
                              params = parse.urlencode({'group_id': name['id']})
                              data = request.urlopen(url + "/bot/check_chat.php?%s" % params).read()
                              data_json = json.loads(data.decode("utf-8"))
                              if data_json['is_hive'] == 2:
                                 # result = request.urlopen(url+"/bot/get_news.php").read()
                                 # result_text = json.loads(result.decode("utf-8"))
                                 try:
                                     new_rand_one = conn.srandmember('new_list')
                                     if new_rand_one:
                                         new_rand_one = json.loads(new_rand_one.decode())
                                         g = self.bot.groups().search(name['name'])[0]
                                         g.send(new_rand_one)
                                 except BaseException:
                                     print('推送文章有异常--' + name['name'])

            time.sleep(600)

    #存储群成员(20分钟更新一次)
    def storage_members(self):
        while True:
            if self.bot.alive == False:
                # 杀死进程
                self.async_raise(threading.currentThread().ident, SystemExit)

            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)
            group_list = conn.get('group_bot_' + self.us_id)
            if group_list:
                group_list = json.loads(group_list.decode())
                for name in group_list:
                    if name['name'] in all:
                        if name['bot_us_id'] == self.us_id:
                            mems = []
                            try:
                                group = self.bot.groups().search(name['name'])[0]
                                group.update_group
                                for g in group.members:
                                    mems.insert(0, g.name)

                                #字符串
                                mems = ','.join(mems)

                                #存储（批量插入post提交）
                                params = json.dumps({"group_id": name['id'], "group_name": name['name'], "members": mems})

                                header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
                                               "Content-Type": "application/json"}
                                urls = url + '/bot/storage_members.php'
                                requests.post(urls, data=params, headers=header_dict)

                                # 删除
                                params = parse.urlencode({'group_id': name['id']})
                                request.urlopen(url + "/bot/del_storage_members.php?%s" % params)

                            except BaseException:
                                print('存储群成员有异常--' + name['name'])

            time.sleep(1200)

    # 中午12点推送top10群主排行榜
    def send_group_cashback(self):
        while True:
            if self.bot.alive == False:
                # 杀死进程
                self.async_raise(threading.currentThread().ident, SystemExit)
            now = datetime.datetime.now()
            now_hour = now.hour
            now_minute = now.minute
            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)
            group_list = conn.get('group_bot_' + self.us_id)
            if group_list:
                group_list = json.loads(group_list.decode())
                for name in group_list:
                    if name['name'] in all:
                        if name['bot_us_id'] == self.us_id:
                            try:
                                group = self.bot.groups().search(name['name'])[0]
                                if int(now_hour) == 12 and int(now_minute) == 3:
                                    top10 = conn.get('group_cashback_top')
                                    top10 = json.loads(top10.decode())
                                    group.send(top10)
                            except BaseException:
                                print('中午12点推送top10群主排行榜--' + name['name'])
            time.sleep(60)

    # 中午12点推送top10留言
    def send_leave_message(self):
        while True:
            if self.bot.alive == False:
                # 杀死进程
                self.async_raise(threading.currentThread().ident, SystemExit)
            now = datetime.datetime.now()
            now_hour = now.hour
            now_minute = now.minute
            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)
            group_list = conn.get('group_bot_' + self.us_id)
            if group_list:
                group_list = json.loads(group_list.decode())
                for name in group_list:
                    if name['name'] in all:
                        if name['bot_us_id'] == self.us_id:
                            try:
                                group = self.bot.groups().search(name['name'])[0]
                                if int(name['leave_message_switch']) == 1:
                                    if int(now_hour) == 12 and int(now_minute) == 2:
                                        # data = request.urlopen(url + "/bot/get_leave_message.php").read()
                                        # data_json = json.loads(data.decode("utf-8"))
                                        top10 = conn.get('leave_top_message')
                                        top10 = json.loads(top10.decode())
                                        group.send(top10)
                            except BaseException:
                                print('中午12点推送top10留言有异常--' + name['name'])
            time.sleep(60)

    # 随机奖励
    def random_reward(self):
        while True:
            if self.bot.alive == False:
                # 杀死进程
                self.async_raise(threading.currentThread().ident, SystemExit)

            array = ['8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21']
            now = datetime.datetime.now()
            now_hour = now.hour
            now_minute = now.minute
            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)
            group_list = conn.get('group_bot_' + self.us_id)
            if group_list:
                group_list = json.loads(group_list.decode())
                for name in group_list:
                    if name['name'] in all:
                        if name['bot_us_id'] == self.us_id:
                            try:
                                group = self.bot.groups().search(name['name'])[0]
                                if int(name['random_reward_switch']) == 1:
                                    if (str(now_hour) in array) and int(now_minute) == 30:
                                        params = parse.urlencode({'group_id': name['id']})
                                        data = request.urlopen(url + "/bot/random_reward.php?%s" % params).read()
                                        data_json = json.loads(data.decode("utf-8"))
                                        group.send(data_json['content'])
                            except BaseException:
                                print('随机奖励有异常--' + name['name'])
            time.sleep(60)


    #登录状态判断
    def check_login(self):
        while True:
            if self.bot.alive == False:
                # 获取机器人状态
                params = parse.urlencode({'us_id': self.us_id})
                result = request.urlopen(url + "/bot/get_qrcode.php?%s" % params).read()
                data_json = json.loads(result.decode("utf-8"))
                if int(data_json['rows']['robot_alive']) == 1:
                    # 退出状态改变
                    params = parse.urlencode({'robot_alive': 2, 'us_id': self.us_id})
                    request.urlopen(url + "/bot/bot_alive.php?%s" % params)

                    # 发送短信通知
                    params = parse.urlencode({'us_id': self.us_id})
                    request.urlopen(url + "/bot/send_message.php?%s" % params).read()

                    # 杀死进程
                    self.async_raise(threading.currentThread().ident, SystemExit)

            time.sleep(20)




    # 每60秒判断一次接口最新数据库与本地生成的json是否相同，不同的数据，生成群聊对象
    def judge_group_or_same(self):
        while True:
            if self.bot.alive == False:
                # 杀死进程
                self.async_raise(threading.currentThread().ident, SystemExit)
            #所有群组
            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)

            dict2 = conn.lpop('new_group_' + self.us_id)
            if dict2:
                dict2 = json.loads(dict2.decode())
                if dict2['name'] in all:
                    self.start_record_bot(dict2['name'], dict2['invite_code'])

            time.sleep(60)



    #每分钟获取排名变化数据推送
    def ranking_change_record(self):
        while True:
            if self.bot.alive == False:
                # 杀死进程
                self.async_raise(threading.currentThread().ident, SystemExit)
            # 所有群组
            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)

            group_list = conn.get('group_bot_' + self.us_id)
            if group_list:
                group_list = json.loads(group_list.decode())
                for name in group_list:
                    rank_list = conn.lrange('ranking_change_record_' + name['id'], 0, 30)
                    if rank_list:
                        if name['name'] in all:
                            #判断群是否可以开启
                            if int(name['is_del']) == 1 and int(name['is_admin_del']) == 1 and self.us_id == name['bot_us_id'] and int(name['ranking_change_switch']) == 1:
                                try:
                                    group = self.bot.groups().search(name['name'])[0]
                                    for i in rank_list:
                                        record = json.loads(i.decode())
                                        content = "@" + record['wechat'] + "，您在CCVT荣耀排行榜上的排名从第 " + str(record['first_rand']) + " 位已经上升至第 " + str(record['after_rand']) + " 位"
                                        group.send(content)
                                        continue
                                    # params = parse.urlencode({'group_id': name['id']})
                                    # data = request.urlopen(url + "/bot/get_ranking_change_record.php?%s" % params).read()
                                    # data_json = json.loads(data.decode("utf-8"))
                                    # rows = data_json['rows']
                                    # for s in rows:
                                    #     content = "@"+s['wechat']+"，您在CCVT荣耀排行榜上的排名从第 "+s['first_rand']+" 位已经上升至第 "+s['after_rand']+" 位"
                                    #     group.send(content)
                                    #     continue
                                except BaseException:
                                    print('每分钟推送排名变化数据推送有异常--' + name['name'])
                        conn.ltrim('ranking_change_record_' + name['id'], 31, -1)

            time.sleep(40)

    #每天播报地址
    def this_day_send_address(self):
        while True:

            if self.bot.alive == False:
                # 杀死进程
                self.async_raise(threading.currentThread().ident, SystemExit)
            # 所有群组
            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)

            now = datetime.datetime.now()
            now_hour = now.hour
            now_minute = now.minute
            group_list = conn.get('group_bot_' + self.us_id)
            if group_list:
                group_list = json.loads(group_list.decode())
                for name in group_list:

                    if name['name'] in all:
                        try:
                            group = self.bot.groups().search(name['name'])[0]

                            # 判断是否群可以发送定时任务
                            if int(name['is_del']) == 1 and int(name['is_admin_del']) == 1 and self.us_id == name['bot_us_id']:

                                # 判断每天早上八点和晚上10推送今日统计
                                if int(name['send_address']) == 1:
                                    if int(now_hour) == 22 and int(now_minute) == 0:
                                        params = parse.urlencode({'group_name': name['name']})
                                        data = request.urlopen(url + "/bot/search_chat.php?%s" % params).read()
                                        data_json = json.loads(data.decode("utf-8"))
                                        if (data_json["is_chat"] == "1"):
                                            content = "很晚了，大家早点休息鸭~ 不要熬夜伤身体~会变胖胖哦~，今日聊天记录查看地址:" + data_json['url']
                                            group.send(content)
                                        continue
                                    elif int(now_hour) == 8 and int(now_minute) == 0:
                                        params = parse.urlencode({'group_name': name['name']})
                                        data = request.urlopen(url + "/bot/search_statistical.php?%s" % params).read()
                                        data_json = json.loads(data.decode("utf-8"))
                                        if (data_json["is_statistical"] == "1"):
                                            content = "大家早上好~，昨日ccvt奖励记录查看地址:" + data_json['url']
                                            group.send(content)
                                        continue
                                    elif int(now_hour) == 12 and int(now_minute) == 1:
                                        params = parse.urlencode({'group_name': name['name']})
                                        data = request.urlopen(url + "/bot/search_statistical.php?%s" % params).read()
                                        data_json = json.loads(data.decode("utf-8"))
                                        if (data_json["is_statistical"] == "1"):
                                            content = "大家中午好~，昨日ccvt奖励记录查看地址:" + data_json['url']
                                            group.send(content)
                                        continue
                        except BaseException:
                            print('每天播报地址有异常--' + name['name'])
            time.sleep(60)


    # 每60秒定时循环本地json文件内容
    def timer_run(self):
        while True:
            if self.bot.alive == False:
                # 杀死进程
                self.async_raise(threading.currentThread().ident, SystemExit)

            now = datetime.datetime.now()
            now_hour = now.hour
            now_minute = now.minute

            rows = conn.get("timer_" + str(now_hour) + ":" + str(now_minute))
            if rows:
                # 所有群组
                all = []
                all_groups = self.bot.groups()
                for group_name in all_groups:
                    all.insert(0, group_name.name)

                rows = json.loads(rows.decode())
                for i in rows:
                    if int(i['group_id']) == -1:
                        group_list = conn.get('group_bot_' + self.us_id)
                        if group_list:
                            group_list = json.loads(group_list.decode())
                            for name in group_list:
                                if int(name['is_del']) == 1 and int(name['is_admin_del']) == 1 and self.us_id == name['bot_us_id']:
                                    try:
                                        group = self.bot.groups().search(name['name'])[0]
                                        content = i['content']
                                        if int(i['type']) == 1:
                                            # 图片
                                            if int(i['send_type']) == 2:
                                                group.send_image("./static/timer_" + i['id'] + ".jpg")
                                                continue
                                            else:
                                                group.send(content)
                                                continue
                                        elif int(i['type']) == 2:
                                            if "-" in i['tx_content']:
                                                ss = i['tx_content'].split("-")
                                            else:
                                                ss = [i['tx_content']]
                                            a = time.localtime()
                                            week = time.strftime("%A", a).lower()
                                            if str(week) in ss:
                                                # 图片
                                                if int(i['send_type']) == 2:
                                                    group.send_image("./static/timer_" + i['id'] + ".jpg")
                                                    continue
                                                else:
                                                    group.send(content)
                                                    continue
                                    except BaseException:
                                        print('总定时任务有异常--' + name['name'])
                    else:
                        group_info = conn.get("group_info_"+i['group_id'])
                        if group_info:
                            group_info = json.loads(group_info.decode())
                            if int(group_info['is_del']) == 1 and int(group_info['is_admin_del']) == 1 and self.us_id == group_info['bot_us_id']:
                                try:
                                    group = self.bot.groups().search(group_info['name'])[0]
                                    content = i['content']
                                    if int(i['type']) == 1:
                                        # 图片
                                        if int(i['send_type']) == 2:
                                            group.send_image("./static/timer_" + i['id'] + ".jpg")
                                            continue
                                        else:
                                            group.send(content)
                                            continue
                                    elif int(i['type']) == 2:
                                        if "-" in i['tx_content']:
                                            ss = i['tx_content'].split("-")
                                        else:
                                            ss = [i['tx_content']]
                                        a = time.localtime()
                                        week = time.strftime("%A", a).lower()
                                        if str(week) in ss:
                                            # 图片
                                            if int(i['send_type']) == 2:
                                                group.send_image("./static/timer_" + i['id'] + ".jpg")
                                                continue
                                            else:
                                                group.send(content)
                                                continue
                                except BaseException:
                                    print('单任务有异常--' + group_info['name'])

            time.sleep(60)

    # 收集群聊信息
    #lstrip :从字符串左侧删除
    def start_record_bot(self, name, invite_code):
        record_group = self.bot.groups().search(name)[0]
        @self.bot.register(record_group)
        def forward_boss_message(msg):
            group_list = conn.get('group_bot_' + self.us_id)
            if group_list:
                gr = json.loads(group_list.decode())
                for g in gr:
                   # 判断群功能是否打开
                   if name == g['name'] and int(g['is_del']) == 1 and int(g['is_admin_del']) == 1 and self.us_id == g['bot_us_id']:

                   # if name == g['name'] and int(g['is_del']) == 1 and int(g['is_admin_del']) == 1:

                       path = ''

                       #如果是视频或者图片，下载图片，视频
                       if msg.raw['Type'] == "Picture":
                           t = "./static/" + msg.raw['FileName']
                           msg.get_file(t)        #下载图片

                           # 上传到阿里云
                           content = self.oss_upload('img/' + msg.raw['FileName'], t)

                           #删除本地文件
                           os.remove(t)
                       else:
                           content = msg.text


                       # 插入数据库
                       self.insert_message(msg.raw['CreateTime'], msg.raw['ActualNickName'], content, g['ba_id'], g['id'], name, msg.raw['Type'], path, self.us_id)


                       #判断是否是新人入群
                       if int(g['is_welcome']) == 1:
                           if msg.raw['Type'] == "Note":
                               s = msg.text
                               if ("邀请" in s) and ("加入了群聊" in s):
                                   res = "@"+ s.split("邀请")[1].replace('加入了群聊', '').replace('"', '')+"，"+g['welcome']
                               elif ("通过扫描" in s) and ("加入群聊" in s):
                                   res = "@" + s.split("通过扫描")[0].replace('"', '') + "，" + g['welcome']
                               return res

                       # 专属注册地址
                       reg_url = self.get_reg_url(msg.raw['ActualNickName'], g['id'], invite_code)

                       # 判断是否已经绑定ccvt账号，没绑定通知下
                       if int(g['bind_account_notice']) == 1:
                           res = self.bind_account_notice(msg.raw['ActualNickName'], reg_url, g['exclusive_switch'])
                           if res:
                               return res


                       #关键词
                       conte = msg.text.replace('@' + self.bot.self.name, '')
                       conte = conte.strip()
                       # 搜索当前群中微信昵称数量
                       this_group = self.bot.groups().search(name)[0]
                       this_group.update_group
                       lenth = len(this_group.members.search(msg.raw['ActualNickName']))
                       # 关键词调用方法
                       result = self.keywords(conte, msg.raw['ActualNickName'], name, reg_url, lenth, g['id'])
                       if result:
                           ret = result
                       else:
                           # 判断调戏功能是否打开
                           if int(g['is_flirt']) == 1:
                               if "@" + self.bot.self.name in msg.text:
                                   # 关键词
                                   params = parse.urlencode({'ask': conte, 'group_id': g['id']})
                                   data = request.urlopen(url + "/bot/get_key_words.php?%s" % params).read()
                                   data_json = json.loads(data.decode("utf-8"))
                                   if (data_json["errcode"] == "0"):

                                       if int(data_json['rows']['send_type']) == 2:

                                           send_address = "./static/key_" + data_json['rows']['id'] + ".jpg"

                                           # 插入数据库（因为下面的发送图片会终止，所以这里插入）
                                           self.insert_message(msg.raw['CreateTime'], self.bot.self.name, data_json['rows']['answer'], g['ba_id'], g['id'], name, "Picture", '', self.us_id)
                                           # 发送图片
                                           record_group.send_image(send_address)
                                       else:
                                           ret = data_json['rows']['answer']
                                   else:
                                       ret = self.auto_ai(conte)
                       if ret:
                           # 插入数据库
                           self.insert_message(msg.raw['CreateTime'], self.bot.self.name, ret, g['ba_id'], g['id'], name, msg.raw['Type'], '', self.us_id)
                           return ret



    #判断是否已经绑定ccvt账号，没绑定通知下
    def bind_account_notice(self, nickname, reg_url, exclusive_switch):
        res = ''
        params = parse.urlencode({'nickname': nickname})
        data = request.urlopen(url + "/bot/notice_records.php?%s" % params).read()
        data_json = json.loads(data.decode("utf-8"))
        if data_json['status'] == "2":
            res = "@" + nickname + "，沟通创造价值，感谢您的发言。由于您的群聊昵称尚未在 " + address + " 官网上绑定，将无法收到AI机器人每晚发放的CCVT聊天奖励哦"
            if int(exclusive_switch) == 1:
                res = res + "，您的专属注册地址为：" + reg_url
        elif data_json['status'] == "3":
            res = "@" + nickname + "，由于您的荣耀积分为负数，将无法获得聊天奖励"

        return res

    #获取专属地址
    def get_reg_url(self, nickname, group_id, invite_code):
        params = parse.urlencode({'wechat': nickname})
        data = request.urlopen(url + "/bot/get_exclusive_code.php?%s" % params).read()
        data_json = json.loads(data.decode("utf-8"))

        #获取专属地址
        params = parse.urlencode({'code': data_json["errmsg"], 'group_id': group_id, 'invite_code': invite_code, 'type': '1'})
        data = request.urlopen(url + "/bot/get_reg_url.php?%s" % params).read()
        data_json = json.loads(data.decode("utf-8"))
        return data_json["url"]


    #关键词回复封装
    def keywords(self, conte, nickname, group_name, reg_url, lenth, group_id):
        st = conte.replace(' ', ' ')
        st = st.split(' ')
        while '' in st:
            st.remove('')

        #大写全部转小写
        # ccvt = conte.lower()

        if ("兑换码" in conte) and (":" in conte or "：" in conte):
            conte = conte.replace('：', ':')
            conte = conte.split(':')[1].replace(' ', '')
            return self.exchange_voucher(nickname, conte)
        elif "ccvt-" in conte:
            return self.exchange_voucher(nickname, conte)
        elif conte == "话题" or conte == "最新话题" or conte == "今日话题" or conte == "换个话题":
            params = parse.urlencode({'ask': conte, 'group_name': group_name})
            data = request.urlopen(url + "/bot/get_topic.php?%s" % params).read()
            data_json = json.loads(data.decode("utf-8"))
            return "话题：" + data_json["content"]
        elif conte == "注册" or conte == "注册地址":
            params = parse.urlencode({'nickname': nickname})
            data = request.urlopen(url + "/bot/get_us_um.php?%s" % params).read()
            data_json = json.loads(data.decode("utf-8"))
            if data_json['errcode'] == "0":
                params = parse.urlencode({'invite_code': data_json['code'], 'type': '2'})
                data = request.urlopen(url + "/bot/get_reg_url.php?%s" % params).read()
                data_json = json.loads(data.decode("utf-8"))
                return "@" + nickname + "，您的专属邀请地址为：" + data_json["url"]
            else:
                return "@" + nickname + "，您的专属注册地址为：" + reg_url
        elif conte == "登录" or conte == "登陆" or conte == "登录地址" or conte == "登陆地址":
            params = parse.urlencode({'type': '3'})
            data = request.urlopen(url + "/bot/get_reg_url.php?%s" % params).read()
            data_json = json.loads(data.decode("utf-8"))
            return data_json["url"]
        elif conte == "是否绑定" or conte == "绑定":
            params = parse.urlencode({'nickname': nickname, 'group_id': group_id})
            data = request.urlopen(url + "/bot/wechat_is_bind.php?%s" % params).read()
            data_json = json.loads(data.decode("utf-8"))
            if data_json['errcode'] == "105":
                return "@" + nickname + "，沟通创造价值，感谢您的发言。由于您的群聊昵称尚未在 " + address + " 官网上绑定，将无法收到AI机器人每晚发放的CCVT聊天奖励哦，您的专属注册地址为：" + reg_url
            else:
                return data_json["errmsg"]
        elif conte == "升级":
            params = parse.urlencode({'nickname': nickname})
            data = request.urlopen(url + "/bot/user_to_upgrade.php?%s" % params).read()
            data_json = json.loads(data.decode("utf-8"))
            return data_json["errmsg"]
        elif conte == "领域":
            params = parse.urlencode({'group_id': group_id, 'group_name': group_name})
            data = request.urlopen(url + "/bot/group_to_upgrade.php?%s" % params).read()
            data_json = json.loads(data.decode("utf-8"))
            return data_json["errmsg"]
        elif conte == "聊天奖励" or conte == "奖励记录":
            params = parse.urlencode({'group_name': group_name})
            data = request.urlopen(url + "/bot/search_statistical.php?%s" % params).read()
            data_json = json.loads(data.decode("utf-8"))
            return "昨日奖励地址：" + data_json["url"]
        elif (len(st)==2 and ("红包" in st)):
            params = parse.urlencode({'group_id': group_id, 'nickname': nickname, 'uid': st[1]})
            data = request.urlopen(url + "/bot/red_packet.php?%s" % params).read()
            data_json = json.loads(data.decode("utf-8"))
            if data_json['errcode'] == "105":
                return "@" + nickname + "，沟通创造价值，感谢您的发言。由于您的群聊昵称尚未在 " + address + " 官网上绑定，将无法收到AI机器人每晚发放的CCVT聊天奖励哦，您的专属注册地址为：" + reg_url
            else:
                return data_json["errmsg"]

        elif (len(st)==3 and ("赞" in st or "踩" in st)):
            if lenth > 1:
                return "本矿池中存在多个昵称：" + nickname + "，无法继续执行"
            else:
                params = parse.urlencode({'give_wechat': nickname, 'group_id': group_id, 'recive_wechat': st[0].replace('@', ''), 'status': st[1], 'num': st[2]})
                data = request.urlopen(url + "/bot/give_like_or_nolike.php?%s" % params).read()
                data_json = json.loads(data.decode("utf-8"))
                return data_json["errmsg"]
        elif conte == "价格":
            data = request.urlopen(url + "/bot/get_now_ccvt_price.php").read()
            data_json = json.loads(data.decode("utf-8"))
            if data_json['errcode'] == "0":
                return data_json["errmsg"]
        elif conte == "排名":
            params = parse.urlencode({'group_id': group_id, 'group_name': group_name})
            data = request.urlopen(url + "/bot/get_group_glory_list.php?%s" % params).read()
            data_json = json.loads(data.decode("utf-8"))
            if data_json['errcode'] == "0":
                return data_json["errmsg"]
        elif conte == "群主排名":
            top10 = conn.get('group_cashback_top')
            if top10:
                return json.loads(top10.decode())
    #兑换码兑换
    def exchange_voucher(self, nickname, voucher):
        # 兑换码兑换
        params = parse.urlencode({'nickname': nickname, 'voucher': voucher})
        data = request.urlopen(url + "/bot/exchange_voucher.php?%s" % params).read()
        data_json = json.loads(data.decode("utf-8"))
        return data_json["errmsg"]

    # 插入数据库
    def insert_message(self, sendTime, nikename, content, ba_id, group_id, name, type , head_img, us_id):
        # t = time.time()
        # timeArray = time.localtime(sendTime)
        # sendTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        #
        # aItem = {}
        # aItem["bot_nickname"] = nikename
        # aItem["head_img"] = head_img
        # aItem["bot_content"] = content
        # aItem["bot_send_time"] = sendTime
        # aItem["bot_create_time"] = int(t)
        # aItem["wechat"] = nikename
        # aItem["us_id"] = us_id
        # aItem["ba_id"] = ba_id
        # aItem["group_id"] = group_id
        # aItem["group_name"] = name
        # aItem["type"] = type
        # jsonArr = json.dumps(aItem)
        # conn.rpush('message_list', jsonArr)

        timeArray = time.localtime(sendTime)
        sendTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        params = parse.urlencode({'nickname': nikename, 'content': content, 'send_time': sendTime, 'wechat': nikename, 'ba_id': ba_id, 'group_id': group_id, 'group_name': name, 'type': type, 'head_img': head_img, 'us_id': us_id})
        #print(params)
        #print(url+"/bot/collect_message.php?%s" % params)
        request.urlopen(url+"/bot/collect_message.php?%s" % params)

    #好友聊天信息
    def sel_frind_message(self):
        @self.bot.register(Friend, msg_types=TEXT)
        def sel_friend(msg):
            # 单聊开关
            params = parse.urlencode({'us_id': self.us_id})
            data = request.urlopen(url + "/bot/get_single_chat_switch.php?%s" % params).read()
            data_json = json.loads(data.decode("utf-8"))
            if data_json["errmsg"] == "1":
                if (msg.raw['Type'] == 'Text'):
                    if "ccvt" in msg.text:
                        params = parse.urlencode({'wechat': msg.sender.name})
                        data = request.urlopen(url + "/bot/search_us_amount.php?%s" % params).read()
                        data_json = json.loads(data.decode("utf-8"))
                        if (data_json["errcode"] == "101"):
                            ret = "对不起，未找到您的ccvt账户"
                        elif (data_json["errcode"] == "0"):
                            ret = "恭喜你，您已经有" + str(data_json["base_amount"]) + "个ccvt了"
                        else:
                            ret = "未知错误，请联系管理员"
                    elif "发言数" in msg.text:
                        params = parse.urlencode({'wechat': msg.sender.name})
                        #print(msg.sender.name)
                        data = request.urlopen(url + "/bot/search_day_message.php?%s" % params).read()
                        data_json = json.loads(data.decode("utf-8"))
                        if (data_json["errcode"] == "101"):
                            ret = "对不起，未找到您的ccvt账户"
                        elif (data_json["errcode"] == "0"):
                            ret = "恭喜你，你今天已经发言" + str(data_json["rows"]["count"]) + "次"
                        else:
                            ret = "未知错误，请联系管理员"
                    else:
                       ret = self.auto_ai(msg.text)
                else:
                    ret = '[奸笑][奸笑]'
            else:
                ret = ''

            path = ''


            if msg.raw['Type'] == "Picture" or msg.raw['Type'] == "Video" or msg.raw['Type'] == "Recording":
                t = "./static/" + msg.raw['FileName']
                msg.get_file(t)  # 下载图片，视频

                # 上传到阿里云
                content = self.oss_upload('img/' + msg.raw['FileName'], t)

                # 删除本地文件
                os.remove(t)
            else:
                content = msg.text
            # 插入数据库
            self.insert_message(msg.raw['CreateTime'], msg.sender.name, content, 'friend', '0', 'friend', msg.raw['Type'], path, self.us_id)

            # 插入数据库
            self.insert_message(msg.raw['CreateTime'], self.bot.self.name, ret, 'friend', '0', 'friend', msg.raw['Type'], '', self.us_id)

           #print('[发送]' + str(ret))
            return ret




    # 好友请求
    def add_friends(self):
        @self.bot.register(msg_types="Friends")
        def auto_accept_friends(msg):
            new_friend = msg.card.accept()
            self.bot.enable_puid('wxpy_puid.pkl')
            frind_puid = new_friend.puid
            #new_friend.set_remark_name(new_friend.remark_name + "-" + frind_puid)
            new_friend.set_remark_name(new_friend.remark_name)
            #new_friend.send("你好，我是您的CCVT小助手，欢迎加入，您的CCVT账户代码是" + str(frind_puid))
            new_friend.send("你好，我是您的机器小助手，欢迎加入")


    #图灵机器人
    def auto_ai(self, text):
        url = "http://www.tuling123.com/openapi/api"
        api_key = ""
        payload = {
            "key": api_key,
            "info": text,
            "userid": "316890"
        }
        r = requests.post(url, data=json.dumps(payload))
        result = json.loads(r.content.decode())
        if ('url' in result.keys()):
            return result["text"] + result["url"]
        else:
            return result["text"]

    #上传到阿里云
    def oss_upload(self, img_key, img_path):
        accessKeyId = ''
        accessKeySecret = ''
        bucket_name = 'ccvthb'
        aliyun_url = 'oss-cn-beijing.aliyuncs.com'
        auth = oss2.Auth(accessKeyId, accessKeySecret)
        bucket = oss2.Bucket(auth, aliyun_url, bucket_name)
        bucket.put_object_from_file(img_key, img_path)
        url = "http://" + bucket_name+"."+aliyun_url+"/"+img_key
        return url


