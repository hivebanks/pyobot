import json
import requests
import datetime
import hashlib
import random
import time

def get_guid():
    seed = "1234567890abcdefghijklmnopqrstuvwxyz"
    sa = []
    for i in range(12):
        sa.append(random.choice(seed))
    salt = ''.join(sa)

    hash = hashlib.md5()
    hash.update(salt.encode())
    md5ha = hash.hexdigest()
    return  md5ha


def main():
    now = datetime.datetime.now()
    url = 'http://phpmanong.cn/api/bot/timer.php'
    req = requests.get(url)
    rows = json.loads(req.text)['rows']
    for i in rows:
        h = int(i['time'].split(":")[0])
        m = int(i['time'].split(":")[1])
        s = int(i['time'].split(":")[-1])
        if now.hour == h and now.minute == m and now.second == s:
            print(111)
            break
        else:
            print(222)
            break
    time.sleep(1)
    main()
main()




