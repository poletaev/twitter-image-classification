import ssl
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from frontend_for_tweets import create_app

if __name__ == "__main__":
    app = create_app(debug=True)
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(app.config['PORT'], app.config['ADDRESS'])
    try:
        IOLoop.instance().start()
    except ssl.SSLError as e:
        app.logger.error(e.message)

