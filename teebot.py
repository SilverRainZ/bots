# -*- encoding: UTF-8 -*-
# this is a simple script uesd to get info of teeworlds server
# adapt from a php script: https://www.teeworlds.com/forum/viewtopic.php?id=7737
# support server version: teeworlds_srv 0.6.x

import sys
import socket
from _teeserver import teeserver
from bot import Bot, echo, broadcast

tee_server = '115.159.114.54'
tee_alias = 'ExiaHanTXFun'
tee_port = 8303
    
class TeeBot(Bot):
    targets = ['#archlinux-cn', '#linuxba']
    trig_cmds = ['PRIVMSG']
    srv = None

    def init(self):
        self.srv = teeserver(tee_server, tee_port, tee_alias)

    def finalize(self):
        self.srv.stop()

    @echo
    def on_privmsg(self, nick, target, msg):
        if not msg.startswith('.tee'):
            return (True, None, None)

        if not self.srv.update():
            return (True, target, '%s: Failed to update server info' % nick)

        reply = ''
        msg = msg.split(' ')

        if msg[1:]:
            if msg[1] == 'server':
                reply = server_info(self.srv)
            if msg[1] == 'player' and msg[2:]:
                reply = player_info(self.srv, msg[2])
            if msg[1] == 'help':
                reply = help()
        else:
            reply = players_list(self.srv)

        if reply:
            return (True, target, '%s: %s' % (nick, reply))
        
        return (True, None, None)

bot = TeeBot()

def players_list(srv):
    return '{0}/{1} people(s) in {2}: {3}'.format(
            srv.cur_player_num,
            srv.max_player_num,
            srv.alias,
            ', '.join([ '{0}({1})'.format(p['name'], p['score']) for p in srv.players])
            )


def player_info(srv, name):
    for p in srv.players:
        if p['name'] == name:
            return '{0}, clan: {1}, region: {2}, score: {3}, stat: {4}'.format(
                    p['name'],
                    p['clan'],
                    p['region'],
                    p['score'],
                    p['stat']
                    )
    return 'player `{0}` not found <(=﹁"﹁=)>'.format(name)


def server_info(srv):
    return '{0}, version: {1}, address: {2}:{3} gamemode: {4}, map: {5}, players: {6}/{7}'.format(
            srv.name,
            srv.version,
            srv.ip,
            srv.port,
            srv.mode,
            srv.map_name,
            srv.cur_player_num,
            srv.max_player_num
            )


def help():
    return ('Usage: `.tee` => get players list, '
            '`.tee server` => get server info, '
            '`.tee player <playername>` => get player info, '
            '`.tee help` => get this message.'
            )
