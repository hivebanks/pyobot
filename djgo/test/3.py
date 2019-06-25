from wxpy import *
import time
import datetime
# bot = Bot(cache_path=False)
# @bot.register(msg_types="Friends")
# def auto_accept_friends(msg):
#     new_friend = msg.card.accept()
#     print(new_friend)
#     bot.enable_puid('wxpy_puid.pkl')
#     frind_puid = new_friend.puid
#     new_friend.set_remark_name(frind_puid)
#     new_friend.send("你好，我是您的CCVT小助手，欢迎加入，您的CCVT账户代码是" + str(frind_puid))
#

# embed()

from urllib import parse


asa =""
print(asa)
print(22)
print(asa.lstrip('.'))

s = ""

print(parse.quote(s))

a = "%E6%98%87%E8%85%BE+910+%E6%98%AF%E7%9B%AE%E5%89%8D%E5%8D%95%E8%8A%AF%E7%89%87%E8%AE%A1%E7%AE%97%E5%AF%86%E5%BA%A6%E6%9C%80%E5%A4%A7%E7%9A%84%E8%8A%AF%E7%89%87%EF%BC%8C%E8%AE%A1%E7%AE%97%E5%8A%9B%E8%B6%85+Google+%E5%8F%8A%E8%8B%B1%E4%BC%9F%E8%BE%BE%EF%BC%8C%E6%AF%94%E6%9C%80%E6%8E%A5%E8%BF%91%E7%9A%84+NV+%E7%9A%84+V100+%E8%BF%98%E8%A6%81%E9%AB%98%E5%87%BA%E4%B8%80%E5%80%8D%EF%BC%8C%E5%85%B6%E5%8D%8A%E7%B2%BE%E5%BA%A6%E7%AE%97%E5%8A%9B%E8%BE%BE%E5%88%B0%E4%BA%86+256+TFLOPS%E3%80%82%E6%98%87%E8%85%BE+910+%E7%9A%84%E6%9C%80%E5%A4%A7%E5%8A%9F%E8%80%97%E4%B8%BA+350W%E3%80%81%E9%87%87%E7%94%A8+7nm+%E5%B7%A5%E8%89%BA"

print(parse.unquote(a))

ss = parse.urlencode({'group_name': s})
print(ss)


now = (datetime.datetime.now()+datetime.timedelta(days=-1)).strftime('%Y-%m-%d %H:%I:%M:%S')
print(now)