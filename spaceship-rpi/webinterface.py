__author__ = 'yaron'

import threading
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options

class WebInterface(tornado.web.RequestHandler):

    def __init__(self):
        self.receiver_thread = threading.Thread(target=self.main)
        self.receiver_thread.setDaemon(True)
        self.receiver_thread.start()

    @staticmethod
    def set(spaceship):
        WebInterface.spaceship = spaceship

    @staticmethod
    def get_spaceship():
        return WebInterface.spaceship

    def main(self):
        define("port", default=8888, help="run on the given port", type=int)

        tornado.options.parse_command_line()
        application = tornado.web.Application([
            (r"/debug/", DebugHandler),
            (r"/content/(.*)", tornado.web.StaticFileHandler, {"path": "./static/"}),
            (r"/", MainHandler)
        ])
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(options.port)
        tornado.ioloop.IOLoop.current().start()


class MainHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):

        # Get the command arguments
        cmd_type = self.get_argument("cmd_type")
        cmd_id = self.get_argument("cmd_id", 0)
        data = self.get_argument("data", 0)

        if not cmd_type:
            return

        # TODO Check that the cmd_type is actually an integer
        # For now, we just trigger an event on the spaceship
        spaceship = WebInterface.spaceship
        text = spaceship.__str__()
        uni = str(text)
        self.write(uni)
        spaceship.handle_user_event(int(cmd_type))

class DebugHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write("Debug interface")

        # Get the command arguments
        cmd_type = self.get_argument("cmd_type")
        cmd_id = self.get_argument("cmd_id", 0)
        data = self.get_argument("data", 0)

        if not cmd_type:
            return

        # TODO Check that the cmd_type is actually an integer
        # For now, we just trigger an event on the spaceship
        spaceship = WebInterface.spaceship
        spaceship.arduino.send_command(int(cmd_type), int(cmd_id), int(data))
