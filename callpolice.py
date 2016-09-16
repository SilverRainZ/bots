# -*- encoding: UTF-8 -*-
# 我要报警啦！

import json
from random import randint
from bot import Bot, echo, read_config

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
    trig_cmds = ['PRIVMSG']

    def init(self):
        config = read_config(__file__)
        self.targets = config['targets']
        gen.n = 0

    def finalize(self):
        pass

    @echo
    def on_privmsg(self, nick, target, msg):
        cmd = '.110'
        if msg.startswith(cmd):
            words = msg.split(' ')
            if words[1:]:
                person = words[1]
            else:
                person = '我'
            return (True, target, gen(target, person))
        return None

bot = CallPoliceBot()
