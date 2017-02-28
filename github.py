# -*- encoding: UTF-8 -*-

import json
import logging
from netaddr import IPNetwork, IPAddress
from labots.bot import Bot
from tornado import web, escape, httpclient

logger = logging.getLogger(__name__)

class WebHookHandler(web.RequestHandler):
    bot = None

    def initialize(self, bot):
        self.bot = bot

    def check_source(self, ip):
        api = 'http://api.github.com/meta'
        http_header = { 'User-Agent' : 'Mozilla/5.0 \
                (X11; Linux x86_64; rv:51.0) \
                Gecko/20100101 Firefox/51.0' }
        http_request = httpclient.HTTPRequest(
                url = api,
                method = 'GET',
                headers = http_header)
        http_client = httpclient.HTTPClient()
        try:
            response = http_client.fetch(http_request)
            meta = json.loads(response.body)
            cidrs = meta['hooks']
            ipaddr = IPAddress(ip)
            for cidr in cidrs:
                if ipaddr in IPNetwork(cidr):
                    return True
        except httpclient.HTTPError as e:
            logger.error('HTTPError: %s %s', api, str(e))
        except json.JSONDecodeError as e:
            logger.error('JSONDecodeError: %s', str(e))
        except KeyError as e:
            logger.error('KeyError: %s', str(e))
        except Exception as e:
            logger.error('%s', str(e))
        http_client.close()

        return False


    def post(self):
        ip = self.request.remote_ip
        if not ip:
            return
        if not self.check_source(ip):
            logger.warn('Untrusted IP %s, ignored', ip)
            return
        else:
            logger.info('Webhook IP %s', ip)

        content_type = self.request.headers.get('Content-Type')
        if content_type != 'application/json':
            return
        event = self.request.headers.get('X-GitHub-Event')
        try:
            data = json.loads(self.request.body)
        except json.JSONDecodeError as e:
            logger.error('JSONDecodeError: %s', str(e))
            return

        try:
            if event == 'create':
                self.event_create(data)
            elif event == 'delete':
                self.event_delete(data)
            elif event == 'issue_comment':
                self.event_issue_comment(data)
            elif event == 'issues':
                self.event_issues(data)
            elif event == 'pull_request':
                self.event_pull_request(data)
            elif event == 'push':
                self.event_push(data)
        except KeyError as e:
            logger.error('KeyError: %s', str(e))

    def event_create(self, data):
        repo = data['repository']['full_name']
        _type = data['ref_type']
        ref = data['ref']
        sender = data['sender']['login']
        for t in self.bot.subscribers[repo]:
            self.bot.say(t, '[%s] %s created %s %s' %
                    (repo, sender, _type, ref))


    def event_delete(self, data):
        repo = data['repository']['full_name']
        _type = data['ref_type']
        ref = data['ref']
        sender = data['sender']['login']
        for t in self.bot.subscribers[repo]:
            self.bot.say(t, '[%s] %s deleted %s %s' %
                    (repo, sender, _type, ref))


    def event_issue_comment(self, data):
        repo = data['repository']['full_name']
        action = data['action']
        number = data['issue']['number']
        title = data['issue']['title']
        comment= data['comment']['body']
        commenter = data['comment']['user']['login']
        url = data['comment']['html_url']
        if action == 'created':
            for t in self.bot.subscribers[repo]:
                self.bot.say(t, '[%s] %s commented on issue #%s: %s <%s>' %
                        (repo, commenter, number, title, url))
                self.bot.say(t, msg)
        # elif action == 'edited':
        #     for t in self.bot.subscribers[repo]:
        #         self.bot.say(t, '[%s] %s updated h{is,er} comment in issue #%s(%s): %s' %
        #                 (repo, commenter, number, title, comment))


    def event_issues(self, data):
        repo = data['repository']['full_name']
        action = data['action']
        title = data['issue']['title']
        sender = data['sender']['login'] # What diff from data['user'] ?
        number = data['issue']['number']
        url = data['issue']['html_url']
        for t in self.bot.subscribers[repo]:
            self.bot.say(t, '[%s] %s %s issue #%s: %s <%s>' %
                    (repo, sender, action, number, title, url))


    def event_pull_request(self, data):
        repo = data['repository']['full_name']
        action = data['action']
        number = data['pull_request']['number']
        title = data['pull_request']['title']
        sender = data['sender']['login']
        merged = data['pull_request']['merged']
        url = data['pull_request']['html_url']
        if action == 'closed' and merged:
            action = 'merged'
        if action == 'opened' \
                or action == 'reopened' \
                or action == 'closed' \
                or action == 'merged':
            for t in self.bot.subscribers[repo]:
                self.bot.say(t, '[%s] %s %s pull request #%s: %s <%s>' %
                        (repo, sender, action, number, title, url))


    def event_push(self, data):
        repo = data['repository']['full_name']
        branch = data['ref'].split('/')[2]
        pusher = data['pusher']['name']
        for t in self.bot.subscribers[repo]:
            self.bot.say(t, '[%s] %s push to branch %s' %
                    (repo, pusher, branch))
            for commit in data['commits']:
                _id = commit['id'][:7]
                # author = commit['author']['name']
                url = commit['url']
                msg = commit['message'].split('\n')
                prefix = '* %s ' % (_id)
                indent = len(prefix) * ' '
                self.bot.say(t,  prefix + msg[0])
                for i in range(1, len(msg)):
                    if (msg[i]):
                        self.bot.say(t, indent + msg[i])
                self.bot.say(t, indent + '<%s>' % url)


class GithubBot(Bot):
    targets = []
    reload = False
    subscribers = {}

    def init(self):
        self.targets = self.config['targets']
        self.subscribers = self.config['subscribers']

        app = web.Application([
            (r'/', WebHookHandler, { 'bot': self }),
            ])
        app.listen(30512)

    def finalize(self):
        pass


bot = GithubBot(__file__)
