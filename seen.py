# -*- encoding: UTF-8 -*-
# Seen And Tell => SAT

import labots
from time import strftime

class SeenAndTellBot(labots.Bot):
    usage = '.seen <nick>; .tell <nick> <msg>'

    last_msgs = {}
    untell_msgs = {}

    def init(self):
        self.targets = self.config['targets']
        self.last_msgs = self.storage.get('last_msgs') or {}
        self.untell_msgs = self.storage.get('untell_msgs') or {}

    def finalize(self):
        self.storage['last_msgs'] = self.last_msgs
        self.storage['untell_msgs'] = self.untell_msgs

    def on_channel_message(self, origin: str, channel: str, msg: str):
        # Record one's last message
        last_msg = self.last_msgs[origin] = {}

        last_msg['time'] = strftime("%Y-%m-%d %H:%M:%S")
        last_msg['msg'] = msg
        last_msg['channel'] = channel

        # Whether there is any message to tell
        if self.untell_msgs.get(origin):
            untell_msg_list = self.untell_msgs[origin]
            for untell_msg in untell_msg_list:
                self.action.message(channel,
                        '%s: %s told you: %s at %s in %s' % (
                            origin,
                            untell_msg['sender'],
                            untell_msg['msg'],
                            untell_msg['time'],
                            untell_msg['channel']
                            ))
            self.untell_msgs[origin] = []

        # .seen command
        if msg.startswith('.seen'):
            words = list(filter(lambda e: e, msg.split(' ')))
            if words[1:]:
                person = words[1]
                if self.last_msgs.get(person):
                    msg = self.last_msgs[person]
                    if msg['channel'] == channel:
                        ret_msg = 'I last saw %s at %s in here, saying %s .' % (
                                person, msg['time'], msg['msg'])
                    else:
                        ret_msg = 'I last saw %s at %s in another channel.' % (
                                person, msg['time'])
                else:
                    ret_msg = 'I haven\'t seen %s recently.' % person
            else:
                ret_msg = 'Usage: .seen <nick>'
            self.action.message(channel, origin + ': ' + ret_msg)

        # .tell command
        elif msg.startswith('.tell'):
            words = list(filter(lambda e: e, msg.split(' ', maxsplit = 2)))
            if words[2:]:
                person = words[1]
                pass_msg = words[2]
                time = strftime("%Y-%m-%d %H:%M:%S")

                if self.untell_msgs.get(person):
                    self.untell_msgs[person].append({
                            'sender': origin,
                            'channel': channel,
                            'time': time,
                            'msg': pass_msg
                            })
                else:
                    self.untell_msgs[person] = [{
                            'sender': origin,
                            'channel': channel,
                            'time': time,
                            'msg': pass_msg
                            }]

                ret_msg = 'I will pass it to %s when he/she/it is around.' % person
            else:
                ret_msg = 'Usage: .tell <nick> <msg>'

            self.action.message(channel, origin + ': ' + ret_msg)

labots.register(SeenAndTellBot)
