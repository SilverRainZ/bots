# -*- encoding: UTF-8 -*-
# Simple IRC log bot runs on <https://github.com/LastAvenger/labots>

import os
import json
import logging
import tornado.ioloop
from time import time, tzset, strftime
from bot import Bot, echo
from log.web import Application


# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

time_zone = 'Asia/Shanghai'
json_output = './json'

def strip(msg):
    tmp = ''
    is_color = 0
    for c in msg:
        if c in '\x02\x0f\x16\x1d\x1f':
            continue
        if c == '\x03':
            is_color = 2
            continue
        if is_color and c in '0123456789':
            is_color -= 1
            continue
        tmp += c
    return tmp


def logdown(target, log):
    time1 = time()

    fname = os.path.join(json_output, target, strftime('%Y-%m-%d.json'))

    logger.debug('Try opening %s' % fname)
    if not os.path.exists(fname):
        with open(fname, 'w') as f:
            logger.info('New log file: %s' % fname)
            json.dump([{'TimeZone': time_zone}], f, ensure_ascii = False)

    logger.debug('Logging: %s' % log)
    with open(fname, 'r+') as f:
        j = json.load(f)
        j.append(log)
        f.seek(0)
        json.dump(j, f, ensure_ascii = False)

    logger.debug('<%s> 1 message logged, time usage: %s'
            % (strftime('%H:%M:%S'), time() - time1))

class LogBot(Bot):
    apps = None
    targets = ['#archlinux-cn', '#linuxba']
    trig_cmds = ['JOIN', 'PART', 'QUIT', 'NICK', 'PRIVMSG']

    def init(self):
        os.environ['TZ'] = time_zone
        tzset()

        if not os.path.exists(json_output):
            logger.info('Creating JSON output directory "%s"' % json_output)
            os.makedirs(json_output)
        for t in self.targets:
            dirname = os.path.join(json_output, t[1:])
            if not os.path.exists(dirname):
                logger.info('Creating directory "%s"' % dirname)
                os.makedirs(dirname)

        app = Application(json_output)
        app.start()


    def finalize(self):
        app.stop()


    @echo
    def on_join(self, nick, chan):
        logdown(chan, {
                'time': strftime('%H:%M:%S'),
                'command': 'JOIN',
                'channel': chan,
                'nick': nick,
                })
        return (True, None, None)

    @echo
    def on_part(self, nick, chan, reason):
        logdown(chan, {
                'time': strftime('%H:%M:%S'),
                'command': 'PART',
                'channel': chan,
                'nick': nick,
                'reason': reason,
                })
        return (True, None, None)

    @echo
    def on_quit(self, nick, chan, reason):
        logdown(chan, {
                'time': strftime('%H:%M:%S'),
                'command': 'QUIT',
                'nick': nick,
                'reason': reason,
                })
        return (True, None, None)

    @echo
    def on_nick(self, nick, new_nick, chan):
        logdown(chan, {
                'time': strftime('%H:%M:%S'),
                'command': 'NICK',
                'nick': nick,
                'new_nick': new_nick,
                })
        return (True, None, None)

    @echo
    def on_privmsg(self, nick, target, msg):
        logdown(target, {
                'time': strftime('%H:%M:%S'),
                'command': 'PRIVMSG',
                'channel': target,
                'nick': nick,
                'message': strip(msg),
                })
        return (True, None, None)

bot = LogBot()
