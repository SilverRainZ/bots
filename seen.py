# -*- encoding: UTF-8 -*-
# Seen And Tell => SAT

import os
import json
from time import strftime

from bot import Bot

# TODO: DON'T USE GLOBAL VARIBLE


class SeenAndTellBot(Bot):
    targets = []

    cache_file = ''
    last_msgs = {}
    untell_msgs = {}

    def init(self):

        self.targets = self.config['targets']
        self.cache_file = self.config['cache']

        with open(self.cache_file, 'r') as f:
            cache = json.loads(f.read())
            self.last_msgs = cache['last_msgs']
            self.untell_msgs = cache['untell_msgs']


    def finalize(self):
        with open(self.cache_file, 'w') as f:
            json.dump(
                    { 'last_msgs': self.last_msgs, 'untell_msgs': self.untell_msgs },
                    f, ensure_ascii = False, indent = 4)

    def on_MSG(self, target, nick, msg):
        # Record one's last message
        last_msg = self.last_msgs[nick] = {}

        last_msg['time'] = strftime("%Y-%m-%d %H:%M:%S")
        last_msg['msg'] = msg
        last_msg['channel'] = target

        # Whether there is any message to tell
        if self.untell_msgs.get(nick):
            untell_msg_list = self.untell_msgs[nick]
            for untell_msg in untell_msg_list:
                self.say(target,
                        '%s: %s told you: %s at %s in %s' % (
                            nick,
                            untell_msg['sender'],
                            untell_msg['msg'],
                            untell_msg['time'],
                            untell_msg['channel']
                            ))
            self.untell_msgs[nick] = []

        # .seen command
        if msg.startswith('.seen'):
            words = msg.split(' ')
            if words[1:]:
                person = words[1]
                if self.last_msgs.get(person):
                    msg = self.last_msgs[person]
                    if msg['channel'] == target:
                        ret_msg = 'I last saw %s at %s in here, saying %s .' % (
                                person, msg['time'], msg['msg'])
                    else:
                        ret_msg = 'I last saw %s at %s in another channel.' % (
                                person, msg['time'])
                else:
                    ret_msg = 'I haven\'t seen %s recently.' % person
            else:
                ret_msg = 'Usage: .seen <nick>'
            self.say(target, nick + ': ' + ret_msg)

        # .tell command
        elif msg.startswith('.tell'):
            words = msg.split(' ', maxsplit = 2)
            if words[2:]:
                person = words[1]
                pass_msg = words[2]
                time = strftime("%Y-%m-%d %H:%M:%S")

                if self.untell_msgs.get(person):
                    self.untell_msgs[person].append({
                            'sender': nick,
                            'channel': target,
                            'time': time,
                            'msg': pass_msg
                            })
                else:
                    self.untell_msgs[person] = [{
                            'sender': nick,
                            'channel': target,
                            'time': time,
                            'msg': pass_msg
                            }]

                ret_msg = 'I will pass it to %s when he/she/it is around.' % person
            else:
                ret_msg = 'Usage: .tell <nick> <msg>'

            self.say(target, nick + ': ' + ret_msg)

    def on_PRIVMSG(self, target, nick, msg):
        self.on_MSG(target, nick, msg)

    def on_ACTION(self, target, nick, msg):
        self.on_MSG(target, nick, msg)

    def on_NOTICE(self, target, nick, msg):
        self.on_MSG(target, nick, msg)



bot = SeenAndTellBot(__file__)
