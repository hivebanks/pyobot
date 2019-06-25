from wxpy import *


bot = Bot(cache_path=True)

groups = bot.groups()

for group in groups:
    print(group)
    print(group.owner.nick_name)
    print(group.self)