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


            # 生成本地group json文件，因为下面的进程会卡死，所以先生成一次
            self.set_group_json_first()

            #单聊
            self.sel_frind_message()

            # 添加好友
            self.add_friends()

            #收集群聊信息
            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)
                # 插入数据库临时群表
                params = parse.urlencode({'group_name': group_name.name, 'us_id': self.us_id})
                request.urlopen(url + "/bot/temporary_group.php?%s" % params).read()

            group_list = self.get_group_json()
            for name in group_list:
                if name['name'] in all:
                    self.start_record_bot(name['name'], name['invite_code'])


            # 循环调用接口生成json,循环调用json判断时间
            # 注：不能写t1 = threading.Thread(target=self.set_timer())
            threads = []
            #判断登录
            ti = self.us_id+"_check_login"
            ti = threading.Thread(target=self.check_login)
            threads.append(ti)
            #生成定时任务json
            set_timer = self.us_id + "_set_timer"
            set_timer = threading.Thread(target=self.set_timer)
            threads.append(set_timer)
            #定时发送定时任务
            timer_run = self.us_id+"_timer_run"
            timer_run = threading.Thread(target=self.timer_run)
            threads.append(timer_run)
            self.t3 = threading.Thread(target=self.judge_group_or_same)
            threads.append(self.t3)
            #判断一次接口最新数据库与本地生成的json是否相同，不同的数据，生成群聊对象
            judge_group_or_same = self.us_id+"_judge_group_or_same"
            judge_group_or_same = threading.Thread(target=self.judge_group_or_same)
            threads.append(judge_group_or_same)
            # 每天定时播报地址
            this_day_send_address = self.us_id + "_this_day_send_address"
            this_day_send_address = threading.Thread(target=self.this_day_send_address)
            threads.append(this_day_send_address)
            # 通知荣耀积分排名变化用户
            ranking_change_record = self.us_id + "_ranking_change_record"
            ranking_change_record = threading.Thread(target=self.ranking_change_record)
            threads.append(ranking_change_record)
            # 每半个小时没人发言推送文章
            check_chat = self.us_id + "_check_chat"
            check_chat = threading.Thread(target=self.check_chat)
            threads.append(check_chat)
            # 存储群成员
            storage_members = self.us_id + "_storage_members"
            storage_members = threading.Thread(target=self.storage_members)
            threads.append(storage_members)
            # 定时发送定时任务（全部群）
            # timer_run_all = self.us_id + "_timer_run_all"
            # timer_run_all = threading.Thread(target=self.timer_run_all)
            # threads.append(timer_run_all)
            # 多少天群没有说话的，自动改成删除
            check_chat_to_group = self.us_id + "_check_chat_to_group"
            check_chat_to_group = threading.Thread(target=self.check_chat_to_group)
            threads.append(check_chat_to_group)
            # 中午12点推送top10留言
            send_leave_message = self.us_id + "_send_leave_message"
            send_leave_message = threading.Thread(target=self.send_leave_message)
            threads.append(send_leave_message)
            # 随机奖励
            random_reward = self.us_id + "_random_reward"
            random_reward = threading.Thread(target=self.random_reward)
            threads.append(random_reward)
            # 审核群
            # audit_group = self.us_id + "_audit_group"
            # audit_group = threading.Thread(target=self.audit_group)
            # threads.append(audit_group)
            for t in threads:
                t.start()
            for t in threads:
                t.join()


    def set_time2r(self):
        while True:
            if self.bot.alive == False:
                # 杀死进程
                self.async_raise(threading.currentThread().ident, SystemExit)
            time_list = conn.get('timer_list')
            if time_list:
                new_dict = json.loads(time_list.decode())
                # 图片下载到本地
                for i in new_dict:
                    if int(i['send_type']) == 2:
                        if int(i['is_change_img']) == 2:
                            addresss = "./static/" + i['id'] + ".jpg"
                            # 先删除本地文件
                            if os.path.exists(addresss):
                                os.remove(addresss)

                            urllib.request.urlretrieve(i['content'], addresss)

                            params = parse.urlencode({'timer_id': i['id']})
                            request.urlopen(url + "/bot/change_timer.php?%s" % params).read()

            time.sleep(120)

    # 调用group接口，生成本地json文件
    def set_group_json_first(self):
        data = request.urlopen(url + "/bot/get_group.php").read()
        data_json = json.loads(data.decode("utf-8"))
        dict = data_json['rows']
        # dumps 将数据转换成字符串
        json_str = json.dumps(dict)

        # loads: 将 字符串 转换为 字典
        new_dict = json.loads(json_str)
        # print(new_dict)

        with open("./json/group.json", "w") as f:
            json.dump(new_dict, f)

    # 调用接口循环判断
    def set_timer(self):
        while True:
            group_list = self.get_group_json()
            for name in group_list:
                params = parse.urlencode({'group_id': name['id']})
                data = request.urlopen(url + "/bot/timer.php?%s" % params).read()
                data_json = json.loads(data.decode("utf-8"))
                dict = data_json['rows']
                # dumps 将数据转换成字符串
                json_str = json.dumps(dict)

                # loads: 将 字符串 转换为 字典
                new_dict = json.loads(json_str)

                # 图片下载到本地
                for i in new_dict:
                    if int(i['send_type']) == 2:
                        if int(i['is_change_img']) == 2:
                            addresss = "./static/" + i['id'] + ".jpg"
                            # 先删除本地文件
                            if os.path.exists(addresss):
                                os.remove(addresss)

                            urllib.request.urlretrieve(i['content'], addresss)

                            params = parse.urlencode({'timer_id': i['id']})
                            request.urlopen(url + "/bot/change_timer.php?%s" % params).read()

                with open("./json/timer_" + name['id'] + ".json", "w") as f:
                    json.dump(new_dict, f)

            # 全部的
            data_all = request.urlopen(url + "/bot/timer_all.php").read()
            data_all_json = json.loads(data_all.decode("utf-8"))
            dict2 = data_all_json['rows']
            # dumps 将数据转换成字符串
            json2_str = json.dumps(dict2)

            # loads: 将 字符串 转换为 字典
            new_dict2 = json.loads(json2_str)

            # 图片下载到本地
            for i in new_dict2:
                if int(i['send_type']) == 2:
                    if int(i['is_change_img']) == 2:
                        addresss2 = "./static/" + i['id'] + ".jpg"
                        # 先删除本地文件
                        if os.path.exists(addresss2):
                            os.remove(addresss2)

                        urllib.request.urlretrieve(i['content'], addresss2)

                        params = parse.urlencode({'timer_id': i['id']})
                        request.urlopen(url + "/bot/change_timer.php?%s" % params).read()

            with open("./json/timer_-1.json", "w") as f:
                json.dump(new_dict2, f)

            # # 循环日期或周几生成本地文件
            # d = request.urlopen(url + "/bot/get_date.php").read()
            # d_json = json.loads(d.decode("utf-8"))
            # dict2 = d_json['rows']
            # # dumps 将数据转换成字符串
            # json_str2 = json.dumps(dict2)
            #
            # # loads: 将 字符串 转换为 字典
            # new_dict2 = json.loads(json_str2)
            # # print(new_dict2)
            #
            # with open("./json/date.json", "w") as f:
            #     json.dump(new_dict2, f)

            # 每60秒调一次接口
            time.sleep(120)

    # 读取本地group文件内容
    def get_group_json(self):
        with open("./json/group.json", 'r') as load_f:
            load_dict = json.load(load_f)
            return load_dict

    # 取出本地json文件内容
    def get_timer(self, group_id):
        with open("./json/timer_" + group_id + ".json", 'r') as load_f:
            load_dict = json.load(load_f)
            return load_dict

    # 取出本地date.json文件内容
    def get_date(self):
        with open("./json/date.json", 'r') as load_f:
            load_dict = json.load(load_f)
            return load_dict


    # 每分钟判断一次**分钟内是否有人聊天，如果没人聊天，推送文章
    def check_chat(self):
        while True:
            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)
            group_list = self.get_group_json()
            for name in group_list:
                if name['name'] in all:
                   if int(name['news_switch']) == 1:
                      now = datetime.datetime.now()
                      if (now.hour >= 8) and (now.hour < 22):
                          params = parse.urlencode({'group_id': name['id']})
                          data = request.urlopen(url + "/bot/check_chat.php?%s" % params).read()
                          data_json = json.loads(data.decode("utf-8"))
                          if data_json['is_hive'] == 2:
                             result = request.urlopen(url+"/bot/get_news.php").read()
                             result_text = json.loads(result.decode("utf-8"))

                             g = self.bot.groups().search(name['name'])[0]
                             g.send(result_text['content'])

            time.sleep(600)

    #判断群成员是否达到100以上（审核群）(60秒)
    # def audit_group(self):
    #     while True:
    #         params = parse.urlencode({'status': "1", 'us_id': self.us_id})
    #         data = request.urlopen(url + "/bot/audit_group.php?%s" % params).read()
    #         data_json = json.loads(data.decode("utf-8"))
    #         groups = data_json['group_list']
    #         for i in groups:
    #             mems = []
    #             group = self.bot.groups().search(i['name'])[0]
    #             group.update_group
    #             for g in group.members:
    #                 mems.insert(0, g.name)
    #             count = len(mems)
    #             params = parse.urlencode({'status': "2", 'group_id': i['id'], 'count': count})
    #             data = request.urlopen(url + "/bot/audit_group.php?%s" % params).read()
    #             json.loads(data.decode("utf-8"))
    #
    #         time.sleep(60)

    #存储群成员(20分钟更新一次)
    def storage_members(self):
        while True:
            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)
            group_list = self.get_group_json()
            for name in group_list:
                if name['name'] in all:
                    if name['bot_us_id'] == self.us_id:
                        mems = []
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
                        response = requests.post(urls, data=params, headers=header_dict)

                        # 删除
                        params = parse.urlencode({'group_id': name['id']})
                        request.urlopen(url + "/bot/del_storage_members.php?%s" % params)

            time.sleep(1200)

    # 多少天群没有说话的，自动改成删除
    def check_chat_to_group(self):
        while True:
            now = datetime.datetime.now()
            if now.hour == 23 and now.minute == 30:
                request.urlopen(url + "/bot/check_chat_to_group.php").read()
            # 每隔60秒检测一次
            time.sleep(60)

    # 中午12点推送top10留言
    def send_leave_message(self):
        while True:
            now = datetime.datetime.now()
            now_hour = now.hour
            now_minute = now.minute
            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)
            group_list = self.get_group_json()
            for name in group_list:
                if name['name'] in all:
                    if name['bot_us_id'] == self.us_id:
                        group = self.bot.groups().search(name['name'])[0]
                        if int(name['leave_message_switch']) == 1:
                            if int(now_hour) == 12 and int(now_minute) == 2:
                                data = request.urlopen(url + "/bot/get_leave_message.php").read()
                                data_json = json.loads(data.decode("utf-8"))
                                group.send(data_json['content'])
            time.sleep(60)

    # 随机奖励
    def random_reward(self):
        while True:
            array = ['8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21']
            now = datetime.datetime.now()
            now_hour = now.hour
            now_minute = now.minute
            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)
            group_list = self.get_group_json()
            for name in group_list:
                if name['name'] in all:
                    if name['bot_us_id'] == self.us_id:
                        group = self.bot.groups().search(name['name'])[0]
                        if int(name['random_reward_switch']) == 1:
                            if (str(now_hour) in array) and int(now_minute) == 30:
                                params = parse.urlencode({'group_id': name['id']})
                                data = request.urlopen(url + "/bot/random_reward.php?%s" % params).read()
                                data_json = json.loads(data.decode("utf-8"))
                                group.send(data_json['content'])
            time.sleep(60)


    #登录状态判断
    def check_login(self):
        while True:
            if self.bot.alive == True:
                status = 1
            else:
                status = 2

            params = parse.urlencode({'robot_alive': status, 'us_id': self.us_id})
            request.urlopen(url + "/bot/bot_alive.php?%s" % params)


            #判断微信退出，线程退出,发送验证码通知
            if status == 2:
                params = parse.urlencode({'us_id': self.us_id})
                request.urlopen(url + "/bot/send_message.php?%s" % params).read()
                #终止这个用户的进程
                ti = self.us_id + "_check_login"
                ti.stop()

                timer_run = self.us_id + "_timer_run"
                timer_run.stop()

                judge_group_or_same = self.us_id + "_judge_group_or_same"
                judge_group_or_same.stop()

                storage_members = self.us_id + "_storage_members"
                storage_members.stop()

                set_timer = self.us_id + "_set_timer"
                set_timer.stop()

                check_chat = self.us_id + "_check_chat"
                check_chat.stop()

                # audit_group = self.us_id + "_audit_group"
                # audit_group.stop()

                ranking_change_record = self.us_id + "_ranking_change_record"
                ranking_change_record.stop()

                this_day_send_address = self.us_id + "_this_day_send_address"
                this_day_send_address.stop()

                # timer_run_all = self.us_id + "_timer_run_all"
                # timer_run_all.stop()

                check_chat_to_group = self.us_id + "_check_chat_to_group"
                check_chat_to_group.stop()

                send_leave_message = self.us_id + "_send_leave_message"
                send_leave_message.stop()

                random_reward = self.us_id + "_random_reward"
                random_reward.stop()

            time.sleep(20)




    # 每60秒判断一次接口最新数据库与本地生成的json是否相同，不同的数据，生成群聊对象
    def judge_group_or_same(self):
        while True:
            data = request.urlopen(url + "/bot/get_group.php").read()
            data_json = json.loads(data.decode("utf-8"))
            dict = data_json['rows']
            # dumps 将数据转换成字符串
            json_str = json.dumps(dict)

            # loads: 将 字符串 转换为 字典
            dict2 = json.loads(json_str)

            dict1 = self.get_group_json()
            id = []
            name = []
            # ba_id = []
            for i in dict1:
                id.insert(0, i['id'])
                name.insert(0, i['name'])
                # ba_id.insert(0, i['ba_id'])

            #所有群组
            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)

            for a in dict2:
                if (a['id'] not in id) or (a['name'] not in name):
                    if a['name'] in all:
                        self.start_record_bot(a['name'], a['invite_code'])

            #更新json文件
            self.set_group_json_first()

            time.sleep(60)



    #每分钟获取排名变化数据推送
    def ranking_change_record(self):
        while True:
            # 所有群组
            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)

            group_list = self.get_group_json()
            for name in group_list:
                if name['name'] in all:
                    #判断群是否可以开启
                    if int(name['is_del']) == 1 and int(name['is_admin_del']) == 1 and self.us_id == name['bot_us_id'] and int(name['ranking_change_switch']) == 1:
                        group = self.bot.groups().search(name['name'])[0]
                        params = parse.urlencode({'group_id': name['id']})
                        data = request.urlopen(url + "/bot/get_ranking_change_record.php?%s" % params).read()
                        data_json = json.loads(data.decode("utf-8"))
                        rows = data_json['rows']
                        for s in rows:
                            content = "@"+s['wechat']+"，您在CCVT荣耀排行榜上的排名从第 "+s['first_rand']+" 位已经上升至第 "+s['after_rand']+" 位"
                            group.send(content)
                            continue

            time.sleep(40)

    #每天播报地址
    def this_day_send_address(self):
        while True:
            # 所有群组
            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)

            now = datetime.datetime.now()
            now_hour = now.hour
            now_minute = now.minute
            group_list = self.get_group_json()
            for name in group_list:

                if name['name'] in all:
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
            time.sleep(60)

    # 每秒定时循环本地json文件内容（所有群统一）
    # def timer_run_all(self):
    #     while True:
    #         rows = self.get_timer("-1")
    #         if rows:
    #             # 所有群组
    #             all = []
    #             all_groups = self.bot.groups()
    #             for group_name in all_groups:
    #                 all.insert(0, group_name.name)
    #
    #             now = datetime.datetime.now()
    #             now_hour = now.hour
    #             now_minute = now.minute
    #
    #             for i in rows:
    #                 group_list = self.get_group_json()
    #                 for name in group_list:
    #                     if name['name'] in all:
    #
    #                         group = self.bot.groups().search(name['name'])[0]
    #
    #                         # 判断是否群可以发送定时任务
    #                         if int(name['is_del']) == 1 and int(name['is_admin_del']) == 1 and self.us_id == name['bot_us_id']:
    #                             h = int(i['time'].split(":")[0])
    #                             m = int(i['time'].split(":")[1])
    #                             if now_hour == h and now_minute == m:
    #                                 content = i['content']
    #                                 if int(i['type']) == 1:
    #                                     # 图片
    #                                     if int(i['send_type']) == 2:
    #                                         group.send_image("./static/" + i['id'] + ".jpg")
    #                                         continue
    #                                     else:
    #                                         group.send(content)
    #                                         continue
    #                                 elif int(i['type']) == 2:
    #                                     if "-" in i['tx_content']:
    #                                         ss = i['tx_content'].split("-")
    #                                     else:
    #                                         ss = [i['tx_content']]
    #                                     a = time.localtime()
    #                                     week = time.strftime("%A", a).lower()
    #                                     if str(week) in ss:
    #                                         # 图片
    #                                         if int(i['send_type']) == 2:
    #                                             group.send_image("./static/" + i['id'] + ".jpg")
    #                                             continue
    #                                         else:
    #                                             group.send(content)
    #                                             continue


            time.sleep(60)

    # 每60秒定时循环本地json文件内容
    def timer_run(self):
        while True:
            now = datetime.datetime.now()
            now_hour = now.hour
            now_minute = now.minute

            rows = conn.get("timer_" + str(now_hour) + ":" + str(now_minute))
            if rows:
                is_send = ''
                # 所有群组
                all = []
                all_groups = self.bot.groups()
                for group_name in all_groups:
                    all.insert(0, group_name.name)

                rows = json.loads(rows.decode())
                for i in rows:
                    if int(i['group_id']) == -1:
                        group_list = conn.get("group_list")
                        if group_list:
                            group_list = json.loads(group_list.decode())
                            for name in group_list:
                                if int(name['is_del']) == 1 and int(name['is_admin_del']) == 1 and self.us_id == name['bot_us_id']:
                                    is_send = 1
                                    group = self.bot.groups().search(name['name'])[0]
                    else:
                        group_info = conn.get("group_info_"+i['group_id'])
                        if group_info:
                            group_info = json.loads(group_info.decode())
                            if int(group_info['is_del']) == 1 and int(group_info['is_admin_del']) == 1 and self.us_id == group_info['bot_us_id']:
                                is_send = 1
                                group = self.bot.groups().search(group_info['name'])[0]
                    if is_send == 1:
                        content = i['content']
                        if int(i['type']) == 1:
                            # 图片
                            if int(i['send_type']) == 2:
                                group.send_image("./static/" + i['id'] + ".jpg")
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
                                    group.send_image("./static/" + i['id'] + ".jpg")
                                    continue
                                else:
                                    group.send(content)
                                    continue


            time.sleep(60)

    #每秒定时循环本地json文件内容
    def timer_run2(self):
        while True:
            # 所有群组
            all = []
            all_groups = self.bot.groups()
            for group_name in all_groups:
                all.insert(0, group_name.name)

            now = datetime.datetime.now()
            now_hour = now.hour
            now_minute = now.minute
            group_list = self.get_group_json()
            for name in group_list:

                if name['name'] in all:

                    group = self.bot.groups().search(name['name'])[0]

                    #判断是否群可以发送定时任务
                    if int(name['is_del']) == 1 and int(name['is_admin_del']) == 1 and self.us_id == name['bot_us_id']:

                        rows = self.get_timer(name['id'])
                        for i in rows:
                            if name['id'] == i['group_id']:
                                h = int(i['time'].split(":")[0])
                                m = int(i['time'].split(":")[1])
                                if now_hour == h and now_minute == m:
                                    content = i['content']
                                    if int(i['type']) == 1:
                                        #图片
                                        if int(i['send_type']) == 2:
                                            group.send_image("./static/"+i['id']+".jpg")
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
                                                group.send_image("./static/" + i['id'] + ".jpg")
                                                continue
                                            else:
                                                group.send(content)
                                                continue

            time.sleep(60)


    # 收集群聊信息
    #lstrip :从字符串左侧删除
    def start_record_bot(self, name, invite_code):
        record_group = self.bot.groups().search(name)[0]
        @self.bot.register(record_group)
        def forward_boss_message(msg):

            gr = self.get_group_json()
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

                   #专属注册地址
                   reg_url = self.get_reg_url(msg.raw['ActualNickName'], g['id'], invite_code)
                   # params = parse.urlencode({'wechat': msg.raw['ActualNickName'], 'group_id': g['id'], 'invite_code': invite_code})
                   # reg_url = address + "/h5/user/register.html?%s" % params
                   #判断调戏功能是否打开
                   if int(g['is_flirt']) == 1:

                       if "@"+self.bot.self.name in msg.text:
                           conte = msg.text.replace('@'+self.bot.self.name, '')

                           conte = conte.strip()

                           #搜索当前群中微信昵称数量
                           this_group = self.bot.groups().search(name)[0]
                           this_group.update_group
                           lenth = len(this_group.members.search(msg.raw['ActualNickName']))
                           #关键词调用方法
                           result = self.keywords(conte, msg.raw['ActualNickName'], name, reg_url, lenth, g['id'])
                           if result:
                               ret = result
                           else:
                               #判断是否在黑名单(暂时不启用了)
                               # params = parse.urlencode({'nickname': msg.raw['ActualNickName'], 'group_name': name})
                               # data = request.urlopen(url + "/bot/bot_blacklist.php?%s" % params).read()
                               # data_json = json.loads(data.decode("utf-8"))
                               # if data_json["status"] == 2:
                               #     ret = self.auto_ai(conte)

                               #关键词
                               params = parse.urlencode({'ask': conte, 'group_id': g['id']})
                               data = request.urlopen(url + "/bot/get_key_words.php?%s" % params).read()
                               data_json = json.loads(data.decode("utf-8"))
                               if (data_json["errcode"] == "0"):
                                   if int(data_json['rows']['send_type']) == 2:
                                       send_address = "./static/key_" + data_json['rows']['id'] + ".jpg"
                                       # 先删除本地文件
                                       if os.path.exists(send_address):
                                           os.remove(send_address)

                                       #下载图片
                                       urllib.request.urlretrieve(data_json['rows']['answer'], send_address)

                                       # 插入数据库（因为下面的发送图片会终止，所以这里插入）
                                       self.insert_message(msg.raw['CreateTime'], self.bot.self.name, data_json['rows']['answer'], g['ba_id'], g['id'], name, "Picture", '', self.us_id)
                                       #发送图片
                                       record_group.send_image(send_address)
                                   else:
                                       ret = data_json['rows']['answer']
                               else:
                                   ret = self.auto_ai(conte)

                           # 插入数据库
                           self.insert_message(msg.raw['CreateTime'], self.bot.self.name, ret, g['ba_id'], g['id'], name, msg.raw['Type'], '', self.us_id)

                           return ret

                   # 判断是否已经绑定ccvt账号，没绑定通知下
                   if int(g['bind_account_notice']) == 1:
                       params = parse.urlencode({'nickname': msg.raw['ActualNickName']})
                       data = request.urlopen(url + "/bot/notice_records.php?%s" % params).read()
                       data_json = json.loads(data.decode("utf-8"))
                       if data_json['status'] == 2:
                           res = "@" + msg.raw['ActualNickName'] + "，沟通创造价值，感谢您的发言。由于您的群聊昵称尚未在 " + address + " 官网上绑定，将无法收到AI机器人每晚发放的CCVT聊天奖励哦"
                           if int(g['exclusive_switch']) == 1:
                               res = res+"，您的专属注册地址为：" + reg_url
                           return res
                       elif data_json['status'] == 3:
                           res = "@" + msg.raw['ActualNickName'] + "，由于您的荣耀积分为负数，将无法获得聊天奖励"
                           return res



    #获取专属地址
    def get_reg_url(self, nickname, group_id, invite_code):
        params = parse.urlencode({'wechat': nickname})
        data = request.urlopen(url + "/bot/get_exclusive_code.php?%s" % params).read()
        data_json = json.loads(data.decode("utf-8"))

        params = parse.urlencode({'code': data_json["errmsg"], 'group_id': group_id, 'invite_code': invite_code})
        return address + "/h5/user/register.html?%s" % params


    #关键词回复封装
    def keywords(self, conte, nickname, group_name, reg_url, lenth, group_id):
        st = conte.replace(' ', ' ')
        st = st.split(' ')
        while '' in st:
            st.remove('')

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
            data = request.urlopen(url + "/bot/wechat_is_bind.php?%s" % params).read()
            data_json = json.loads(data.decode("utf-8"))
            if data_json['errcode'] == "0":
                reg_url = address + "/h5/user/register.html?invite_code="+data_json['code']
                return "@" + nickname + "，您的专属邀请地址为：" + reg_url
            else:
                return "@" + nickname + "，您的专属注册地址为：" + reg_url

        elif conte == "是否绑定":
            params = parse.urlencode({'nickname': nickname})
            data = request.urlopen(url + "/bot/wechat_is_bind.php?%s" % params).read()
            data_json = json.loads(data.decode("utf-8"))
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
        elif (len(st)==3 and ("赞" in st or "踩" in st)):
            if lenth > 1:
                return "本群中存在多个昵称：" + nickname + "，无法继续执行"
            else:
                params = parse.urlencode({'give_wechat': nickname, 'group_id': group_id, 'recive_wechat': st[0].replace('@', ''), 'status': st[1], 'num': st[2]})
                data = request.urlopen(url + "/bot/give_like_or_nolike.php?%s" % params).read()
                data_json = json.loads(data.decode("utf-8"))
                return data_json["errmsg"]

    #兑换码兑换
    def exchange_voucher(self, nickname, voucher):
        # 兑换码兑换
        params = parse.urlencode({'nickname': nickname, 'voucher': voucher})
        data = request.urlopen(url + "/bot/exchange_voucher.php?%s" % params).read()
        data_json = json.loads(data.decode("utf-8"))
        return data_json["errmsg"]

    # 插入数据库
    def insert_message(self, sendTime, nikename, content, ba_id, group_id, name, type , head_img, us_id):
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


