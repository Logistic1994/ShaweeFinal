#!/usr/bin/python
# -*- encoding:utf-8 -*-

import tornado.ioloop
import tornado.web
import os
import json
import logging
import logging.config
from algo.model_manager import ModelManager
from util.file_manager import FileManager
from handler.UploadImageHandler import UploadImageHandler
from handler.StyleHandler import StyleHandler
# Set global logger config
logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

# Check static files
static_path = os.path.join(os.path.dirname(__file__), "static")
assert os.path.isdir(static_path)
assert os.path.isfile(os.path.join(static_path, "index.html"))

# Load models config and init model
assert os.path.isfile("model.json")
with open("model.json") as f:
    model_metas = json.load(f)
model_manager = ModelManager()
model_manager.load_models(model_metas)
model_manager.start()

# Load file manager
file_manager = FileManager()
file_manager.init("static/images/upload_process")


class IndexHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render("static/index.html")


class NocacheStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")


app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/index(.*)', IndexHandler),
    (r'/upload_image', UploadImageHandler),
    (r'/style', StyleHandler),
    (r'/(.*)', NocacheStaticFileHandler, {"path": static_path}),
])


if __name__ == "__main__":
    app.listen(8080)
    try:
        logger.info("Run server on 8080...")
        tornado.ioloop.IOLoop.instance().start()
    except:
        model_manager.terminate()
        tornado.ioloop.IOLoop.instance().stop()

