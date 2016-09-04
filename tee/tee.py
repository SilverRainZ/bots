# -*- encoding: UTF-8 -*-

import sys
import logging
from bot import Bot, echo, broadcast
from tee.teeserver import TeeServer, players_list, player_info, server_info, help_

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

tee_server = '115.159.114.54'
tee_alias = 'ExiaHanTXFun'
tee_port = 8303
    
class TeeBot(Bot):
    targets = ['#lasttest']
    trig_cmds = ['PRIVMSG']
    srv = None

    def init(self):
        self.srv = TeeServer(tee_server, tee_port, tee_alias)

    def finalize(self):
        self.srv.stop()

    @echo
    def on_privmsg(self, nick, target, msg):
        if not msg.startswith('.tee'):
            return (True, None, None)

        reply = ''
        msg = msg.split(' ')

        if msg[1:] and msg[1] == 'help':
                return (True, target, help_())

        if not self.srv.update():
            return (True, target, '%s: failed to update server info' % nick)
        
        if not msg[1:]:
            reply = players_list(self.srv)
        elif msg[1] == 'server':
            reply = server_info(self.srv)
        elif msg[1] == 'player' and msg[2:]:
            reply = player_info(self.srv, msg[2])
        else:
            reply = players_list(self.srv)

        return (True, target, '%s: %s' % (nick, reply))


bot = TeeBot()
