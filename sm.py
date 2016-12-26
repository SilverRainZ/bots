# -*- encoding: UTF-8 -*-
# @file sm.py
# @brief SM bot, provides commands `.sm` and `.LQYMGT`
# @author Shengyu Zhang <lastavengers@outlook.com>
# @version
# @date 2016-10-04


import os
import json
from random import randint
from bot import Bot

class SMBot(Bot):
    targets = []
    usage = '.sm <nick> [tag]; .LQYMGT; .lqymgt, .刘青云'

    n = 0
    data = {}
    data_file = None

    def init(self):
        self.targets = self.config['targets']
        self.data_file = self.config['data']

        with open(self.data_file, 'r') as f:
            self.data = json.loads(f.read())

    def finalize(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, ensure_ascii = False, indent = 4)

    def on_LABOTS_MSG(self, target, bot, nick, msg):
        words = list(filter(lambda e: e, msg.split(' ', maxsplit = 2)))

        if words[0] in ['.LQYMGT', '.lqymgt', '.刘青云']:
            words = ['.sm', 'LQYMGT']

        if words[0] == '.sm':
            # Add
            if words[2:] and words[2]:
                name, tag = words[1], words[2]
                if self.data.get(name):
                    if not tag in self.data[name]:
                        self.data[name].append(tag)
                        self.say(target, '%s: Pushed!' % (nick))
                    else:
                        self.say(target, '%s: Tag already exist' % nick)
                else:
                    self.data[name] = [tag]
                    self.say(target, '%s: Pushed!' % nick)
            # Query
            elif words[1:]:
                name = words[1]
                if self.data.get(name):
                    tags = self.data[name]
                    n = randint(0, len(tags) - 1)
                    while n == self.n and len(tags) != 1:
                        n = randint(0, len(tags) - 1)
                    self.n = n
                    self.say(target, '%s: %s' % (nick,tags[n]))
                else:
                    self.say(target, '%s: No data' % nick)
            else:
                self.say(target, '%s: Usage: .sm <nick> [tag]' % nick)


bot = SMBot(__file__)
