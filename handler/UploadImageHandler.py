#!/usr/bin/python
# -*- encoding:utf-8 -*-
import tornado.web
import json
import logging
from PIL import Image
import io
from hashlib import md5
from util.file_manager import FileManager

logger = logging.getLogger(__name__)
file_manager = FileManager("/tmp")


def gen_md5(s):
    m = md5()
    m.update(s)
    return m.hexdigest()


class UploadImageHandler(tornado.web.RequestHandler):
    def post(self):
        # Get meta info
        file_metas = self.request.files['img_file']
        file_0 = file_metas[0]
        image_name = file_0['filename']
        logger.info('Get image {}'.format(image_name.encode('utf-8')))

        # Try to decode image body
        try:
            image = Image.open(io.BytesIO(file_0['body']))
        except IOError as e:
            logger.error('Cannot encode image')
            self.error_ret(-1, 'Bad image file.')
            return

        img_fmt = image.format

        # Generate unique id from content md5
        file_md5 = gen_md5(file_0['body'])

        file_name = '{}.{}'.format(file_md5, img_fmt).lower()

        if file_manager.exists(file_name):
            self.suc_ret(file_name)
            return

        if not file_manager.save(file_name, file_0['body']):
            self.error_ret(1, "Save file failed.")
            return

        self.suc_ret(file_name)

    def error_ret(self, status, reason):
        result = {'status': status, 'reason': reason}
        self.write(json.dumps(result))

    def suc_ret(self, uid):
        result = {"status": 0, "uid": uid}
        self.write(json.dumps(result))