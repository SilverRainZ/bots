# -*- encoding: UTF-8 -*-

import labots
from labots import colorizer
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
            self.bot.logger.info('Trusted IP %s', ip)

        content_type = self.request.headers.get('Content-Type')
        if content_type != 'application/json':
            return
        event = self.request.headers.get('X-GitHub-Event')
        try:
            data = json.loads(self.request.body)
        except json.JSONDecodeError as e:
            self.bot.logger.error('JSONDecodeError: %s', str(e))
            return

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
        elif event == 'push':
            self.bot.logger.error('Unsupported event: %s', event)


    def event_create(self, data):
        repo = data['repository']['full_name']
        _type = data['ref_type']
        ref = data['ref']
        sender = data['sender']['login']
        for t in self.bot.subscribers[repo]:
            self.bot.action.message(t, '%s %s created %s %s' %
                    (format_repo(repo), format_author(sender), _type, format_ref(ref)))


    def event_delete(self, data):
        repo = data['repository']['full_name']
        _type = data['ref_type']
        ref = data['ref']
        sender = data['sender']['login']
        for t in self.bot.subscribers[repo]:
            self.bot.action.message(t, '%s %s deleted %s %s' %
                    (format_repo(repo), format_author(sender), _type, format_ref(ref)))


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
                self.bot.action.message(t, '%s %s commented on issue %s: %s <%s>' %
                        (format_repo(repo), format_author(commenter), format_issue(number), title, url))
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
            self.bot.action.message(t, '%s %s %s issue %s: %s <%s>' %
                    (format_repo(repo), format_author(sender), action, format_issue(number), title, url))


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
        if action in ['opened', 'reopened', 'closed', 'merged']:
            for t in self.bot.subscribers[repo]:
                self.bot.action.message(t, '%s %s %s pull request %s: %s <%s>' %
                        (format_repo(repo), format_author(sender), action, format_issue(number), title, url))


    def event_push(self, data):
        repo = data['repository']['full_name']
        branch = data['ref']
        pusher = data['pusher']['name']
        url = data['compare']
        commits = data['commits']
        num_commits = len(commits)
        # Ignore push event with 0 commit
        if num_commits == 0:
            return
        for t in self.bot.subscribers[repo]:
            self.bot.action.message(t, '%s %s pushed %s commit(s) to branch %s <%s>' %
                    (format_repo(repo), format_author(pusher), highlight(num_commits), format_ref(branch), url))
            # Only report commit details for push event of master
            if not branch in ['master']:
                continue
            for commit in commits:
                _id = format_commit_id(commit['id'])
                # author = commit['author']['name']
                # url = commit['url']
                msg = commit['message'].split('\n')
                if len(msg) == 1:
                    msg = msg[0]
                else:
                    msg = msg[0] + colorizer.style(' ...', fg = colorizer.colors.grey)
                msg = '* %s %s' % (_id, msg)
                self.bot.action.message(t, msg)

def format_repo(repo):
    return colorizer.style('[%s]' % repo, fg = colorizer.colors.green)

def format_author(author):
    return colorizer.style('@' + author, fg = colorizer.colors.blue)

def format_commit_id(commit):
    return colorizer.style(commit[:7], fg = colorizer.colors.orange)

def format_issue(issue):
    return colorizer.style('#%d' % issue, fg = colorizer.colors.orange)

def format_ref(ref):
    if ref.startswith('refs/heads/'):
        ref = ref[len('refs/heads/'):]
    return colorizer.style(ref, fg = colorizer.colors.orange)

def highlight(keyword):
    return colorizer.style(str(keyword), bold = True)

class GithubBot(labots.Bot):
    sockets = []

    def init(self):
        self.targets = self.config['targets']
        self.subscribers = self.config['subscribers']

        app = web.Application([
            (r'/', WebHookHandler, { 'bot': self }),
            ])
        self.sockets = netutil.bind_sockets(self.config['listen_port'])
        server = httpserver.HTTPServer(app)
        server.add_sockets(self.sockets)

    def finalize(self):
        for s in self.sockets:
            s.close()
        self.sockets = []


labots.register(GithubBot)
