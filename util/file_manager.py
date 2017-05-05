# -*- coding: utf-8 -*-
from singleton import singleton
import threading
import os
import errno
import logging

logger = logging.getLogger(__name__)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


@singleton
class FileManager(object):
    def __init__(self, upload_dir="/tmp"):
        self.upload_dir = upload_dir

    def init(self, upload_dir):
        self.upload_dir = os.path.abspath(upload_dir)
        if os.path.exists(self.upload_dir) and os.path.isfile(self.upload_dir):
            raise IOError("{} is a file".format(self.upload_dir))
        else:
            mkdir_p(self.upload_dir)
        logger.info("Location image dir {}".format(self.upload_dir))

    def exists(self, file_name):
        return os.path.isfile(os.path.join(self.upload_dir, file_name))

    def save(self, file_name, file_body):
        try:
            with open(os.path.join(self.upload_dir, file_name), 'wb') as f:
                f.write(file_body)
            return True
        except IOError as e:
            return False





