# -*- encoding: UTF-8 -*-

import labots
import json
from netaddr import IPNetwork, IPAddress
from tornado import web, httpclient, httpserver, netutil

class WebHookHandler(web.RequestHandler):
    bot = None

    def initialize(self, bot):
        self.bot = bot

    def check_source(self, ip):
        api = 'https://api.github.com/meta'
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
            self.bot.logger.error('HTTPError: %s %s', api, str(e))
        except json.JSONDecodeError as e:
            self.bot.logger.error('JSONDecodeError: %s', str(e))
        except KeyError as e:
            self.bot.logger.error('KeyError: %s', str(e))
        except Exception as e:
            self.bot.logger.error('%s', str(e))
        http_client.close()

        return False


    def post(self):
        ip = self.request.remote_ip
        if not ip:
            return
        if not self.check_source(ip):
            self.bot.logger.warn('Untrusted IP %s, ignored', ip)
            return
        else:
            self.bot.logger.info('Webhook IP %s', ip)

        content_type = self.request.headers.get('Content-Type')
        if content_type != 'application/json':
            return
        event = self.request.headers.get('X-GitHub-Event')
        try:
            data = json.loads(self.request.body)
        except json.JSONDecodeError as e:
            self.bot.logger.error('JSONDecodeError: %s', str(e))
            return

        try:
            if event == 'create':
                self.event_create(data)
            elif event == 'delete':
                self.event_delete(data)
            elif event == 'issue_comment':
                # self.event_issue_comment(data)
                return
            elif event == 'issues':
                self.event_issues(data)
            elif event == 'pull_request':
                self.event_pull_request(data)
            elif event == 'push':
                self.event_push(data)
        except KeyError as e:
            self.bot.logger.error('KeyError: %s', str(e))


    def event_create(self, data):
        repo = data['repository']['full_name']
        _type = data['ref_type']
        ref = data['ref']
        sender = data['sender']['login']
        for t in self.bot.subscribers[repo]:
            self.bot.action.message(t, '[%s] %s created %s %s' %
                    (repo, sender, _type, ref))


    def event_delete(self, data):
        repo = data['repository']['full_name']
        _type = data['ref_type']
        ref = data['ref']
        sender = data['sender']['login']
        for t in self.bot.subscribers[repo]:
            self.bot.action.message(t, '[%s] %s deleted %s %s' %
                    (repo, sender, _type, ref))


    def event_issue_comment(self, data):
        repo = data['repository']['full_name']
        action = data['action']
        number = data['issue']['number']
        title = data['issue']['title']
        # comment= data['comment']['body']
        commenter = data['comment']['user']['login']
        url = data['comment']['html_url']
        if action == 'created':
            for t in self.bot.subscribers[repo]:
                self.bot.action.message(t, '[%s] %s commented on issue #%s: %s <%s>' %
                        (repo, commenter, number, title, url))
        # elif action == 'edited':
        #     for t in self.bot.subscribers[repo]:
        #         self.bot.action.message(t, '[%s] %s updated h{is,er} comment in issue #%s(%s): %s' %
        #                 (repo, commenter, number, title, comment))


    def event_issues(self, data):
        repo = data['repository']['full_name']
        action = data['action']
        title = data['issue']['title']
        sender = data['sender']['login'] # What diff from data['user'] ?
        number = data['issue']['number']
        url = data['issue']['html_url']
        if action not in ['opened', 'closed']:
            return
        for t in self.bot.subscribers[repo]:
            self.bot.action.message(t, '[%s] %s %s issue #%s: %s <%s>' %
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
                self.bot.action.message(t, '[%s] %s %s pull request #%s: %s <%s>' %
                        (repo, sender, action, number, title, url))


    def event_push(self, data):
        repo = data['repository']['full_name']
        branch = data['ref'].split('/')[2]
        pusher = data['pusher']['name']
        url = data['compare']
        if branch not in ['master']:
            return
        for t in self.bot.subscribers[repo]:
            self.bot.action.message(t, '[%s] %s push to branch %s < %s >' %
                    (repo, pusher, branch, url))
            for commit in data['commits']:
                _id = commit['id'][:7]
                # author = commit['author']['name']
                # url = commit['url']
                msg = commit['message'].split('\n')
                prefix = '* %s ' % (_id)
                indent = len(prefix) * ' '
                self.bot.action.message(t,  prefix + msg[0])
                for i in range(1, len(msg)):
                    if (msg[i]):
                        self.bot.action.message(t, indent + msg[i])


class GithubBot(labots.Bot):
    reload = True # FIXME: not supported

    def init(self):
        self.targets = self.config['targets']
        self.subscribers = self.config['subscribers']

        app = web.Application([
            (r'/', WebHookHandler, { 'bot': self }),
            ])
        sockets = netutil.bind_sockets(30512, reuse_port = True)
        server = httpserver.HTTPServer(app)
        server.add_sockets(sockets)

    def finalize(self):
        pass


labots.register(GithubBot)
