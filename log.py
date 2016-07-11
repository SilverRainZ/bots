# -*- encoding: UTF-8 -*-
# Simple IRC log bot runs on <https://github.com/LastAvenger/labots>

import os
import json
import time
import logging
from bot import Bot, echo

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

time_zone = 'Asia/Shanghai'
json_output = './json'


def log(func):
    def warpper(*args, **kw):
        log = func(*args, **kw) 

        if not log:
            return
        t = log['channel']

        fname = os.path.join(json_output, t, time.strftime('%Y-%m-%d.json'))
        if not os.path.exists(fname):
            with open(fname, 'w') as f:
                logger.info('New log file: %s' % fname)

        logger.debug('Logging: %s' % log)
        with open(fname, 'a') as f:
            f.write(json.dumps(log) + '\n')

    return warpper


class LogBot(Bot):
    targets = ['#lasttest', '#nexttest']
    trig_cmds = ['JOIN', 'PART', 'QUIT', 'NICK', 'PRIVMSG']

    def init(self):
        os.environ['TZ'] = time_zone
        time.tzset()

        if not os.path.exists(json_output):
            logger.info('Creating JSON output directory "%s"' % json_output)
            os.makedirs(json_output)
        for t in self.targets:

            dirname = os.path.join(json_output, t)
            if not os.path.exists(dirname):
                logger.info('Creating directory "%s"' % dirname)
                os.makedirs(dirname)
           

    def finalize(self):
        pass


    @log
    def on_join(self, nick, chan):
        return {
                'time': time.time(),
                'command': 'JOIN',
                'channel': chan,
                'nick': nick,
                }


    @log
    def on_part(self, nick, chan, reason):
        return {
                'time': time.time(),
                'command': 'PART',
                'channel': chan,
                'nick': nick,
                'reason': reason,
                }


    @log
    def on_quit(self, nick, reason):
        # TODO: which channel should get this log :(
        pass


    @log
    def on_nick(self, nick, new_nick):
        # TODO: which channel should get this log :(
        pass


    @log
    def on_privmsg(self, nick, target, msg):
        return {
                'time': time.time(),
                'command': 'PRIVMSG',
                'channel': target,
                'nick': nick,
                'message': msg
                }



bot = LogBot()
