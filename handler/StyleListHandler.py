#!/usr/bin/python
# -*- encoding:utf-8 -*-
import io
import json
import logging

import tornado.web
from algo.model_manager import ModelManager


class StyleListHandler(tornado.web.RequestHandler):
    def get(self):
        model_manager = ModelManager()
        model_infos = model_manager.get_model_metas()
        if model_infos is None:
            self.error_ret(-1, "Not yet.")
            return
        meta_infos = []
        for model_info in model_infos:
            meta_image = model_info['meta_image']
            meta_image = meta_image[meta_image.rfind('images/'):]
            meta_infos.append({"name": model_info["name"], "chinese_name": model_info["chinese_name"],
                               "meta_image": meta_image})
        self.suc_ret(meta_infos)

    def error_ret(self, status, reason):
        result = {'status': status, 'reason': reason}
        self.write(json.dumps(result))

    def suc_ret(self, meta_infos):
        result = {"status": 0, "styles": meta_infos}
        self.write(json.dumps(result))
