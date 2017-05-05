# -*- coding: utf-8 -*-

import Queue
from model import Model
import threading
from constants import *
import logging
from util.singleton import singleton
logger = logging.getLogger(__name__)

@singleton
class ModelManager(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.inited = False
        self.models = {}
        self.input_queues = {}
        self.output_queue = Queue.Queue()
        self.stop = False
        self.order_mutex = threading.Lock()
        self.order_id = 0
        self.outputs = {}

    def load_models(self, meta_infos):
        for meta_info in meta_infos:
            assert 'name' in meta_info
            name = meta_info['name']
            assert name not in self.models.keys()
            input_queue = Queue.Queue()
            self.models[name] = Model(meta_info, input_queue, self.output_queue)
            self.input_queues[name] = input_queue
        self.inited = True

    def eval(self, style_name, img_path, save_path):
        logger.info("Will eval {} with style {}".format(img_path, style_name))
        if style_name not in self.models:
            return False, -1
        self.order_mutex.acquire()
        order_id = self.order_id + 1
        self.order_id += 1
        self.order_mutex.release()
        self.input_queues[style_name].put({'order_id': order_id,
                                           'order': Order.Style,
                                           'img_path': img_path,
                                           'save_path': save_path})
        return True, order_id

    def get_queue_length(self, style_name):
        if style_name not in self.models:
            return -1
        return self.input_queues[style_name].qsize()

    def get_all_queue_length(self):
        return { style_name: self.input_queues[style_name].qsize() for style_name in self.input_queues.keys() }

    def run(self):
        for model in self.models.values():
            model.start()
        while not self.stop:
            try:
                order_id, ret_code, save_path, style_duration = self.output_queue.get_nowait()
            except Queue.Empty:
                continue
            self.outputs[order_id] = (ret_code, save_path, style_duration)

    def terminate(self):
        logger.info("Model manager terminate.")
        for model_name in self.models.keys():
            self.input_queues[model_name].put({'order': Order.Terminate})
        for model in self.models.values():
            model.join()
        self.stop = True
        if threading.currentThread() != self:
            self.join()

    def check(self, order_id):
        if order_id in self.outputs:
            ret = self.outputs.pop(order_id)
        else:
            ret = None
        return ret
