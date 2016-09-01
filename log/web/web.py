import os
import json
from time import strftime
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer

class IndexHandler(tornado.web.RequestHandler):
    chans = []

    def initialize(self, chans):
        self.chans = chans

    def get(self):
        links = []
        for chan in self.chans:
            links.append((chan, self.reverse_url(chan, 'today')))
        self.render('index.html', 
                title = 'IRC Log Index',
                subtitle = strftime('%Y-%m-%d'),
                links = links)

class ChanLogHandler(tornado.web.RequestHandler):
    name = ''
    path = ''

    def initialize(self, name, path):
        self.name = name
        self.path = path

    def get(self, date):
        if date == 'today':
            date = strftime('%Y-%m-%d')
        logs = []
        fname = os.path.join(self.path, self.name, date + '.json' )
        try:
            f = open(fname, 'r')
            j = json.load(f)
            for l in j:
                if l.get('command'):
                    if l['command'] == 'PRIVMSG':
                        msg = '<%s> %s' % (l['nick'], l['message'])
                    elif l['command'] == 'ACTION':
                        msg = '*** %s %s' % (l['nick'], l['message'])
                    elif l['command'] == 'JOIN':
                        msg = '->| %s has joined %s' % (l['nick'], l['channel'])
                    elif l['command'] == 'PART':
                        msg = '|<- %s has left %s' % (l['nick'], l['channel'])
                    elif l['command'] == 'QUIT':
                        msg = '<-- %s has quit: %s' % (l['nick'], l['reason'])
                    logs.append((l['time'] , msg))

            self.render('log.html', 
                    title = self.name,
                    subtitle = date,
                    logs = logs)
        except FileNotFoundError:
            raise tornado.web.HTTPError(404)
        else:
            f.close()

    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.render('log-no-found.html', 
                    title = self.name,
                    subtitle = self.path_args[0],
                    )

class Application(tornado.web.Application):

    def __init__(self, path):
        chans = os.listdir(path)

        urls = []
        for chan in chans:
           urls.append(tornado.web.url(
               r'/%s/(today|\d{4}-\d{2}-\d{2})' % chan,
               ChanLogHandler, 
               { 'name': chan, 'path': path},
               name = chan,
               ))
           handlers = [ tornado.web.url(r'/', IndexHandler, { 'chans': chans }) ] + urls

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
