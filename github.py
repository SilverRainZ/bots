# -*- encoding: UTF-8 -*-

import json
from labots.bot import Bot
from tornado import web, escape
import json

class MainHandler(web.RequestHandler):
    bot = None

    def initialize(self, bot):
        self.bot = bot

    def post(self):
        event = self.request.headers.get("X-GitHub-Event")
        try:
            data = json.loads(self.request.body)
        except json.JSONDecodeError as e:
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
        title = data["issue"]['title']
        comment= data['comment']['body']
        commenter = data['comment']['user']['login']
        if action == 'created':
            for t in self.bot.subscribers[repo]:
                self.bot.say(t, '[%s] %s commented on issue #%s(%s): %s' %
                        (repo, commenter, number, title, comment))
        elif action == 'edited':
            for t in self.bot.subscribers[repo]:
                self.bot.say(t, '[%s] %s updated h{is,er} comment in issue #%s(%s): %s' %
                        (repo, commenter, number, title, comment))


    def event_issues(self, data):
        repo = data['repository']['full_name']
        action = data['action']
        title = data["issue"]['title']
        sender = data['sender']['login'] # What diff from data['user'] ?
        number = data['issue']['number']
        for t in self.bot.subscribers[repo]:
            self.bot.say(t, '[%s] %s %s issue #%s: %s' %
                    (repo, sender, action, number, title))


    def event_pull_request(self, data):
        repo = data['repository']['full_name']
        action = data['action']
        number = data['pull_request']['number']
        title = data["pull_request"]['title']
        sender = data['sender']['login']
        merged = data['pull_request']['merged']
        if action == 'closed' and merged:
            action = 'merged'
        if action == 'opened' \
                or action == 'reopened' \
                or action == 'closed' \
                or action == 'merged':
            for t in self.bot.subscribers[repo]:
                self.bot.say(t, "[%s] %s %s pull request #%s: %s" %
                        (repo, sender, action, number, title))


    def event_push(self, data):
        repo = data['repository']['full_name']
        branch = data['ref']
        pusher = data['pusher']['name']
        for t in self.bot.subscribers[repo]:
            self.bot.say(t, "[%s] %s push to branch %s" %
                    (repo, pusher, branch))
            for commit in data['commits']:
                _id = commit['id'][:7]
                author = commit['author']['name']
                msg = commit['message'] # Shorten it plz
                self.bot.say(t, "- %s by %s: %s" %
                        (_id, author, msg))


class GithubBot(Bot):
    targets = ['#srain']
    restart = False
    subscribers = {
            'SilverRainZ/srain': targets,
            'SilverRainZ/github-webhook-test': targets,
            # 'baxterthehacker/public-repo': targets,
            }

    def init(self):
        app = web.Application([
            (r'/', MainHandler, { 'bot': self }),
            ])
        app.listen(30512)

    def finalize(self):
        pass


bot = GithubBot(__file__)
