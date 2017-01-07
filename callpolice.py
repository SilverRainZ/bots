# -*- encoding: UTF-8 -*-
# 我要报警啦！

import json
from random import randint
from labots.bot import Bot

def gen(locale, person):
    msg = [ '歪妖妖灵吗？帮%s点一份猪扒饭' % person,
            '歪妖妖灵吗？这里是%s，场面快控制不住了！' % locale,
            '歪妖妖灵吗？这里有只%s成精啦！' % person,
            '歪妖妖灵吗？帮%s点一份猪扒饭，不要辣' % person,
            '歪妖妖灵吗？ %s在搞事你们管不管啊！' % person,
            ]

    n = randint(0, len(msg) - 1)
    while  n == gen.n:
        n = randint(0, len(msg) - 1)
    gen.n = n

    return msg[n]

class CallPoliceBot(Bot):
    targets = []
    usage = '.110 <nick>'

    def init(self):
        self.targets = self.config['targets']
        gen.n = 0

    def finalize(self):
        pass

    def on_LABOTS_MSG(self, target, bot, nick, msg):
        cmd = '.110'
        if msg.startswith(cmd):
            words = list(filter(lambda e: e, msg.split(' ', maxsplit = 2)))
            if words[1:]:
                person = words[1]
            else:
                person = '我'
            self.say(target, gen(target, person))

bot = CallPoliceBot(__file__)
