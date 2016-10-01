# -*- encoding: UTF-8 -*-
# Seen And Tell => SAT

import os
import json
from time import strftime

from bot import Bot

# TODO: DON'T USE GLOBAL VARIBLE

cache_file = ''
last_msgs = {}
untell_msgs = {}

class SeenAndTellBot(Bot):
    targets = []
    trig_cmds = ['PRIVMSG']

    def init(self):
        global cache_file
        global last_msgs
        global untell_msgs

        self.targets = self.config['targets']

        cache_file = self.config['cache']

        with open(cache_file, 'r') as f:
            cache = json.loads(f.read())
            last_msgs = cache['last_msgs']
            untell_msgs = cache['untell_msgs']


    def finalize(self):
        with open(cache_file, 'w') as f:
            json.dump(
                    { 'last_msgs': last_msgs, 'untell_msgs': untell_msgs },
                    f, ensure_ascii = False, indent = 4)

    def on_PRIVMSG(self, target, nick, msg):

        # Record one's last message
        last_msgs[nick] = {}
        last_msgs[nick]['time'] = strftime("%Y-%m-%d %H:%M:%S")
        last_msgs[nick]['msg'] = msg
        last_msgs[nick]['channel'] = target

        # Whether there is any message to tell
        # TODO: return multi message :(
        if untell_msgs.get(nick):
            ret_msgs = '%s: %s told you: %s at %s in %s' % (
                nick,
                untell_msgs[nick]['sender'],
                untell_msgs[nick]['msg'],
                untell_msgs[nick]['time'],
                untell_msgs[nick]['channel']
                )
            untell_msgs[nick] = {}
            self.say(target, ret_msgs)

        # .seen command
        if msg.startswith('.seen'):
            words = msg.split(' ')
            if words[1:]:
                person = words[1]
                if last_msgs.get(person):
                    msg = last_msgs[person]
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

                untell_msgs[person] = {
                        'sender': nick,
                        'channel': target,
                        'time': time,
                        'msg': pass_msg
                        }

                ret_msg = 'I will pass it to %s when he/she/it is around.' % person
            else:
                ret_msg = 'Usage: .seen <nick> <msg>'

            self.say(target, nick + ': ' + ret_msg)


bot = SeenAndTellBot(__file__)
