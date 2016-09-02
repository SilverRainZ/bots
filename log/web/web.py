import os
import json
from time import strftime
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer

class IndexHandler(tornado.web.RequestHandler):
    chans = []

    def initialize(self, ):
        self.chans = self.application.chans

    def get(self):
        links = []

        for chan in self.chans:
            # TODO: concat url: is it right?
            links.append((chan, '/' + chan + '/today'))

        self.render('index.html', 
                title = 'IRC Log Index',
                subtitle = '%s channel(s)' % len(links),
                links = links)


class ChanIndexHandler(tornado.web.RequestHandler):
    path = ''

    def initialize(self):
        self.path = self.application.path

    def get(self, chan):
        links = []
        try:
            files = os.listdir(os.path.join(self.path, chan))
        except FileNotFoundError:
            raise tornado.web.HTTPError(404)

        for f in files:
            # TODO: concat url: is it right?
            links.append((os.path.splitext(f)[0], '/' + chan + '/' + os.path.splitext(f)[0]))

        self.render('logs.html', 
                title = self.path_args[0],
                subtitle = 'index',
                links = links)

    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.render('404.html', 
                    title = 'IRC Log Index',
                    subtitle = self.path_args[0],
                    msg = 'No such channel.',
                    )

class ChanLogHandler(tornado.web.RequestHandler):
    path = ''

    def initialize(self):
        self.path = self.application.path


    def get(self, chan, date):
        if date == 'today':
            date = strftime('%Y-%m-%d')

        logs = []
        raw = self.get_argument('raw', '0')
        fname = os.path.join(self.path, chan, date + '.json' )
        try:
            f = open(fname, 'r')
            if raw == '1':
                self.write(f.read())
                return
            logs_json = json.load(f)
            for log in logs_json:
                if log.get('command'):
                    if log['command'] == 'PRIVMSG':
                        nick = log['nick']
                        msg = log['message']
                    elif log['command'] == 'ACTION':
                        nick = log['nick']
                        msg = '*** %s %s' % (log['nick'], log['message'])
                    elif log['command'] == 'JOIN':
                        nick = '-->'
                        msg = '%s has joined %s' % (log['nick'], log['channel'])
                    elif log['command'] == 'PART':
                        nick = '<--'
                        msg = '%s has left %s' % (log['nick'], log['channel'])
                    elif log['command'] == 'QUIT':
                        nick = '<--'
                        msg = '%s has quit: %s' % (log['nick'], log['reason'])
                    logs.append((log['time'] , nick, msg, log['command']))

            self.render('log.html', 
                    title = chan,
                    subtitle = date,
                    logs = logs)
        except FileNotFoundError:
            raise tornado.web.HTTPError(404)
        else:
            f.close()


    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.render('404.html', 
                    title = self.path_args[0],
                    subtitle = self.path_args[1],
                    msg = 'There is no any log.'
                    )


class Application(tornado.web.Application):
    path = ''
    chans = []
    def __init__(self, path):
        self.path = path
        self.chans = os.listdir(path)

        handlers = [
                (r'/(.+)/(today|\d{4}-\d{2}-\d{2})', ChanLogHandler),
                (r'/([^/]+)', ChanIndexHandler),
                (r'/', IndexHandler),
                ]

        settings = { 
            'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
            'static_path': os.path.join(os.path.dirname(__file__), 'static'),
            'debug': True,
            }

        tornado.web.Application.__init__(self, handlers, **settings)
        

if __name__ == '__main__':
    log_dir = os.path.join('..', 'logs')
    app = Application(log_dir)

    http_srv = HTTPServer(app)
    http_srv.listen(8888)
    tornado.ioloop.IOLoop.current().start()
