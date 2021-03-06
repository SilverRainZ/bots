# -*- encoding: UTF-8 -*-
# This is a simple script to get info from specified teeworlds server
# Runs on <https://github.com/LastAvenger/labots>
# Adapt from a php script:
#   <https://www.teeworlds.com/forum/viewtopic.php?id=7737>
# Supports teeworlds_srv 0.6.x

import logging
import socket
import labots

region_map = {
        '-1':'default', '901':'XEN', '902':'XNI', '903':'XSC', '904':'XWA',
        '737':'SS', '4':'AF', '248':'AX', '8':'AL', '12':'DZ', '16':'AS',
        '20':'AD', '24':'AO', '660':'AI', '28':'AG', '32':'AR', '51':'AM',
        '533':'AW', '36':'AU', '40':'AT', '31':'AZ', '44':'BS', '48':'BH',
        '50':'BD', '52':'BB', '112':'BY', '56':'BE', '84':'BZ', '204':'BJ',
        '60':'BM', '64':'BT', '68':'BO', '70':'BA', '72':'BW', '76':'BR',
        '86':'IO', '96':'BN', '100':'BG', '854':'BF', '108':'BI', '116':'KH',
        '120':'CM', '124':'CA', '132':'CV', '136':'KY', '140':'CF', '148':'TD',
        '152':'CL', '156':'CN', '162':'CX', '166':'CC', '170':'CO', '174':'KM',
        '178':'CG', '180':'CD', '184':'CK', '188':'CR', '384':'CI', '191':'HR',
        '192':'CU', '531':'CW', '196':'CY', '203':'CZ', '208':'DK', '262':'DJ',
        '212':'DM', '214':'DO', '218':'EC', '818':'EG', '222':'SV', '226':'GQ',
        '232':'ER', '233':'EE', '231':'ET', '238':'FK', '234':'FO', '242':'FJ',
        '246':'FI', '250':'FR', '254':'GF', '258':'PF', '260':'TF', '266':'GA',
        '270':'GM', '268':'GE', '276':'DE', '288':'GH', '292':'GI', '300':'GR',
        '304':'GL', '308':'GD', '312':'GP', '316':'GU', '320':'GT', '831':'GG',
        '324':'GN', '624':'GW', '328':'GY', '332':'HT', '336':'VA', '340':'HN',
        '344':'HK', '348':'HU', '352':'IS', '356':'IN', '360':'ID', '364':'IR',
        '368':'IQ', '372':'IE', '833':'IM', '376':'IL', '380':'IT', '388':'JM',
        '392':'JP', '832':'JE', '400':'JO', '398':'KZ', '404':'KE', '296':'KI',
        '408':'KP', '410':'KR', '414':'KW', '417':'KG', '418':'LA', '428':'LV',
        '422':'LB', '426':'LS', '430':'LR', '434':'LY', '438':'LI', '440':'LT',
        '442':'LU', '446':'MO', '807':'MK', '450':'MG', '454':'MW', '458':'MY',
        '462':'MV', '466':'ML', '470':'MT', '584':'MH', '474':'MQ', '478':'MR',
        '480':'MU', '484':'MX', '583':'FM', '498':'MD', '492':'MC', '496':'MN',
        '499':'ME', '500':'MS', '504':'MA', '508':'MZ', '104':'MM', '516':'NA',
        '520':'NR', '524':'NP', '528':'NL', '540':'NC', '554':'NZ', '558':'NI',
        '562':'NE', '566':'NG', '570':'NU', '574':'NF', '580':'MP', '578':'NO',
        '512':'OM', '586':'PK', '585':'PW', '591':'PA', '598':'PG', '600':'PY',
        '604':'PE', '608':'PH', '612':'PN', '616':'PL', '620':'PT', '630':'PR',
        '634':'QA', '638':'RE', '642':'RO', '643':'RU', '646':'RW', '652':'BL',
        '654':'SH', '659':'KN', '662':'LC', '663':'MF', '666':'PM', '670':'VC',
        '882':'WS', '674':'SM', '678':'ST', '682':'SA', '686':'SN', '688':'RS',
        '690':'SC', '694':'SL', '702':'SG', '534':'SX', '703':'SK', '705':'SI',
        '90':'SB', '706':'SO', '710':'ZA', '239':'GS', '724':'ES', '144':'LK', 
        '736':'SD', '740':'SR', '748':'SZ', '752':'SE', '756':'CH', '760':'SY',
        '158':'TW', '762':'TJ', '834':'TZ', '764':'TH', '626':'TL', '768':'TG',
        '772':'TK', '776':'TO', '780':'TT', '788':'TN', '792':'TR', '795':'TM',
        '796':'TC', '798':'TV', '800':'UG', '804':'UA', '784':'AE', '826':'GB',
        '840':'US', '858':'UY', '860':'UZ', '548':'VU', '862':'VE', '704':'VN',
        '92':'VG', '850':'VI', '876':'WF', '732':'EH', '887':'YE', '894':'ZM',
        '716':'ZW',
        } 


class TeeServer():
    sock = None
    host = ''
    port = 0
    alias = ''
    version = ''
    name = ''
    map_name = ''
    mode = ''
    cur_player_num = 0
    max_player_num = 0
    players = []

    def __init__(self, host, port, alias,
            logger = logging.getLogger(__name__)):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.connect((host, port))
        self.sock.settimeout(10)
        self.host = host
        self.port = port
        self.alias = alias
        self.logger = logger


    def update(self):
        try:
            self.sock.send(b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x67\x69\x65\x33\x05')
            data, _ = self.sock.recvfrom(2048)
            info = data.split(b'\x00')
            info[0] = b'NULL'
            info = [x.decode('utf-8') for x in info]

            self.logger.debug('recv data: %s' % info)
            self.version = info[1]
            self.name = info[2]
            self.map_name = info[3]
            self.mode = info[4]
            self.cur_player_num = int(info[8])
            self.max_player_num = int(info[9])
            self.players = []

            if not self.alias:
                self.alias = self.name

            for i in range(0, self.cur_player_num):
                base = i*5
                player = {
                        'name':     info[base+10],
                        'clan':     info[base+11],
                        'region':   region_map[info[base+12]],
                        'score':    info[base+13],
                        'stat':     ['spectator', 'player'][int(info[base+14])],
                        }
                self.logger.debug('player: %s'% player)
                self.players.append(player)
            return True
        except socket.error as err:
            self.logger.error('SOCKET ERROR %s' % err)
        except (UnicodeDecodeError, IndexError, ValueError) as err:
            self.logger.error('UNRECOGNIZED DATA %s' % err)
        return False


    def stop(self):
        self.sock.close()



class TeeBot(labots.Bot):
    usage = ('.tee: get players list;'
             '.tee server: get server info;'
             '.tee player <playername>: get player info;'
             )
    srv = None
    host = None
    port = None

    def init(self):
        self.targets = self.config['targets']
        self.host = self.config['host']
        self.port = self.config['port']
        self.alias = self.config['alias']
        self.srv = TeeServer(self.host, self.port, self.alias, logger = self.logger) 

    def finalize(self):
        self.srv.stop()

    def on_channel_message(self, origin: str, channel: str, msg: str):
        cmd = '.tee'
        if not msg.startswith(cmd):
            return

        reply = ''
        words = list(filter(lambda e: e, msg.split(' ')))

        sub_cmd = words[1] if words[1:] else ''

        if sub_cmd == 'help':
            self.action.message(channel, help())
            return

        if not self.srv.update():
            self.action.message(channel, '%s: failed to update server info' % origin)
            return

        if sub_cmd == 'server':
            reply = server_info(self.srv)
        elif sub_cmd == 'player':
            player = words[2] if words[2:] else ''
            if not player:
                reply = 'Missing player name'
            else:
                reply = player_info(self.srv, player)
        else:
            reply = players_list(self.srv)

        self.action.message(channel, '%s: %s' % (origin, reply))

def players_list(srv):
    return '%s/%s people(s) in %s: %s' % (
            srv.cur_player_num,
            srv.max_player_num,
            srv.alias,
            ', '.join([ '%s(%s)' % (p['name'], p['score']) for p in srv.players])
            )


def player_info(srv, name):
    for p in srv.players:
        if p['name'] == name:
            return '%s, clan: %s, region: %s, score: %s, stat: %s' % (
                    p['name'], p['clan'], p['region'], p['score'], p['stat']
                    )
    return 'player `%s` not found <(=﹁"﹁=)>' % name


def server_info(srv):
    return '%s, version: %s, address: %s:%s gamemode: %s, map: %s, players: %s/%s' % (
            srv.name, srv.version, srv.host, srv.port, srv.mode, srv.map_name,
            srv.cur_player_num, srv.max_player_num
            )


def help():
    return ('Usage: `.tee` => get players list, '
            '`.tee server` => get server info, '
            '`.tee player <playername>` => get player info, '
            '`.tee help` => get this message.'
            )

labots.register(TeeBot)
