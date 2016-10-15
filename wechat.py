import json
import threading
import logging
import itchat, time
from bot import Bot
from itchat.content import *

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@itchat.msg_register(TEXT, isGroupChat=True)
def text_reply(msg):
    logger.info('FromUserName: %s', msg['FromUserName'])
    logger.info('ActualNickName: %s', msg['ActualNickName'])
    logger.info('Content: %s', msg['Content'])

    if not msg['FromUserName'] in bot.wechat_rooms:
        return

    target = bot.targets[bot.wechat_rooms.index(msg['FromUserName'])]
    bot.say(target,
            '[%s] %s' % (msg['ActualNickName'], msg['Content']),
            recv_msg = False)

class WeChatRelayBot(Bot):
    targets = []
    wechat_rooms = []

    def init(self):
        self.targets = self.config['targets']
        self.wechat_rooms = self.config['wechat_rooms']

        itchat.auto_login(True)
        thread = threading.Thread(target = itchat.run)
        thread.start()

    def finalize(self):
        pass

    def on_PRIVMSG(self, target, nick, msg):
        wechat_room = self.wechat_rooms[self.targets.index(target)]
        itchat.send('[%s] %s' % (nick, msg), wechat_room)


bot = WeChatRelayBot(__file__)
