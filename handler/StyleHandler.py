#!/usr/bin/python
# -*- encoding:utf-8 -*-

import json
import logging
import os
import time

import tornado.gen
import tornado.web

from algo.constants import RetCode
from algo.model_manager import ModelManager
from util.file_manager import FileManager

logger = logging.getLogger(__name__)


class StyleHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        uid = self.get_argument("uid")
        style_name = self.get_argument("style_name")
        logger.info("uid: {}, style_name: {}".format(uid, style_name))

        # Check uid exists
        file_manager = FileManager()
        if not file_manager.exists(uid):
            logger.info("uid {} not exists.".format(uid))
            self.error_ret(-1, "Uid not exists.")
            return

        # Check style exists
        model_manager = ModelManager()
        if model_manager.get_queue_length(style_name) == -1:
            logger.info("Style name {} not exists.".format(style_name))
            self.error_ret(-2, "Style name {} not exists.".format(style_name))
            return

        # Styled name
        styled_uid = "{}_{}.{}".format(".".join(uid.split(".")[0:-1]),
                                       style_name,
                                       uid.split(".")[-1])
        if file_manager.exists(styled_uid):
            logger.info("Has already processed this styled_uid.")
            self.suc_ret(styled_uid, duration=0)
            return

        # Do style
        flag, order_id = model_manager.eval(style_name,
                                            os.path.join(file_manager.upload_dir, uid),
                                            os.path.join(file_manager.upload_dir, styled_uid))
        if not flag:
            logger.info("Inner model manager failed to eval.")
            self.error_ret(-3, "Inner model manager failed to eval.")
            return

        # Check order id
        task_ret = yield tornado.gen.Task(self.poll, order_id)
        if task_ret[0] == RetCode.NO_ERR:
            duration = task_ret[-1]
            self.suc_ret(styled_uid, duration=duration)
            return
        elif task_ret[0] == RetCode.ERR_READ_IMG:
            self.error_ret(-1, "Read image failed.")
            return
        else:
            self.error_ret(-100, "Inner error.")
            return

    @tornado.gen.coroutine
    def poll(self, order_id):
        model_manager = ModelManager()
        while True:
            ret = model_manager.check(order_id)
            if not ret:
                time.sleep(0.5)
                continue
            logger.info(str(ret))
            return ret

    def error_ret(self, status, reason):
        ret = {"status": status, "reason": reason}
        self.write(json.dumps(ret))

    def suc_ret(self, styled_uid, **kwargs):
        ret = {"status": 0, "styled_uid": styled_uid}
        for key, value in kwargs.items():
            ret[key] = value
        self.write(json.dumps(ret))
