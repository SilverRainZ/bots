# -*- encoding: UTF-8 -*-
# @file sm.py
# @brief SM bot, provides commands `.sm` and `.LQYMGT`
# @author Shengyu Zhang <lastavengers@outlook.com>
# @version
# @date 2016-10-04


import labots
from random import randint

class SMBot(labots.Bot):
    usage = '.sm[.<count>|.all] <nick> [tag]; i.e: .sm LQYMGT, .sm.2 LQYMGT .sm.all LQYMGT, .lqymgt, .lqymgtf .刘青云'

    n = 0

    def init(self):
        self.targets = self.config['targets']

    def finalize(self):
        pass

    def on_channel_message(self, origin: str, channel: str, msg: str):
        words = list(filter(lambda e: e, msg.split(' ', maxsplit = 2)))

        # Command alias
        if words[0] in ['.LQYMGT', '.lqymgt', '.刘青云']:
            words = ['.sm', 'LQYMGT']
        if words[0] in ['.LQYMGTF', '.lqymgtf']:
            words = ['.sm.all', 'LQYMGT']
        if words[0] in ['.small']:
            words[0] = '.sm.all'

        if words[0].startswith('.sm'):
            # Add
            if len(words) == 3:
                name, tag = words[1], words[2]
                if self.storage.get(name):
                    if not tag in self.storage[name]:
                        self.storage[name].append(tag)
                        self.action.message(channel, '%s: Pushed!' % (origin))
                    else:
                        self.action.message(channel, '%s: Tag already exist' % origin)
                else:
                    self.storage[name] = [tag]
                    self.action.message(channel, '%s: Pushed!' % origin)
            # Query
            elif len(words) == 2:
                subcmd = words[0][4:]
                name = words[1]
                try:
                    tags = self.storage[name]
                    if not tags:
                        raise KeyError
                except KeyError:
                    self.action.message(channel, '%s: No data' % origin)
                    return

                if subcmd:
                    if subcmd == 'all':
                        count = len(tags)
                    else:
                        try:
                            count = min(int(subcmd), len(tags))
                        except ValueError:
                            count = 1
                    for i in range(0, count):
                        self.action.message(channel, '%s: %s' % (origin,tags[i]))
                else:
                    n = randint(0, len(tags) - 1)
                    while n == self.n and len(tags) != 1:
                        n = randint(0, len(tags) - 1)
                    self.n = n
                    self.action.message(channel, '%s: %s' % (origin,tags[n]))
            else:
                self.action.message(channel, '%s: Usage: .sm <nick> [tag]' % origin)

labots.register(SMBot)
