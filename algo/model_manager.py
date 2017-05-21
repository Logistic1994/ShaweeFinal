# -*- coding: utf-8 -*-

import Queue
import logging
import threading
import time
from collections import defaultdict as dd

from constants import *
from model import Model
from util.singleton import singleton

logger = logging.getLogger(__name__)


@singleton
class ModelManager(threading.Thread):
    """
    模型管理
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.inited = False
        self.models = dd(list)
        self.input_queues = {}
        self.output_queue = Queue.Queue()
        self.stop = False
        self.order_mutex = threading.Lock()
        self.order_id = 0
        self.outputs = {}
        self.unable_models = []

    def load_models(self, meta_infos):
        for meta_info in meta_infos:
            assert 'name' in meta_info
            name = meta_info['name']
            assert name not in self.models.keys()
            # 使用优先级队列，在需要更换模型的情况下，可以优先关闭现有线程，而不影响需要等待的任务
            input_queue = Queue.PriorityQueue()
            if 'inst_num' in meta_info:
                inst_num = meta_info['inst_num']
            else:
                inst_num = 1
            logger.info("{}: {}".format(name, inst_num))
            for i in range(inst_num):
                self.models[name].append(Model(meta_info, input_queue, self.output_queue, i))
            self.input_queues[name] = input_queue
        self.inited = True

    def eval(self, style_name, img_path, save_path):
        if style_name in self.unable_models:
            return False, -1
        logger.info("Will eval {} with style {}".format(img_path, style_name))
        if style_name not in self.models:
            return False, -1
        self.order_mutex.acquire()
        order_id = self.order_id + 1
        self.order_id += 1
        self.order_mutex.release()
        # 按照优先级队列的要求，先put优先级，再put数据
        self.input_queues[style_name].put((Order.Style.value, {'order_id': order_id,
                                                               'order': Order.Style,
                                                               'img_path': img_path,
                                                               'save_path': save_path}))
        return True, order_id

    def get_queue_length(self, style_name):
        if style_name not in self.models:
            return -1
        return self.input_queues[style_name].qsize()

    def get_all_queue_length(self):
        return {style_name: self.input_queues[style_name].qsize() for style_name in self.input_queues.keys()}

    def run(self):
        for models in self.models.values():
            for model in models:
                model.start()
        while not self.stop:
            try:
                order_id, ret_code, save_path, style_duration = self.output_queue.get_nowait()
            except Queue.Empty:
                time.sleep(0.5)
                continue
            self.outputs[order_id] = (ret_code, save_path, style_duration)

    def terminate(self):
        logger.info("Model manager terminate.")
        for model_name in self.models.keys():
            for i in range(len(self.models[model_name])):
                self.models[model_name][i].terminate()
        for models in self.models.values():
            for model in models:
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

    def load_new(self, meta_info):
        """
        新增一种风格模型
        :param meta_info: 
        :return: 
        """
        assert 'name' in meta_info
        name = meta_info['name']
        assert name not in self.models.keys()
        input_queue = Queue.PriorityQueue()
        if 'inst_num' in meta_info:
            inst_num = meta_info['inst_num']
        else:
            inst_num = 1
        for i in range(inst_num):
            model = Model(meta_info, input_queue, self.output_queue, i)
            model.start()
            self.models[name].append(model)
        self.input_queues[name] = input_queue

    def change_inst_num(self, meta_info, inst_num):
        assert 'name' in meta_info
        name = meta_info['name']
        assert name in self.models.keys()
        old_num = len(self.models[name])
        input_queue = self.input_queues[name]
        if old_num < inst_num:
            # 扩容
            for i in range(old_num, inst_num):
                model = Model(meta_info, input_queue, self.output_queue, i)
                model.start()
                self.models[name].append(model)
        elif old_num > inst_num:
            # 缩容
            for i in range(inst_num, old_num):
                self.models[name][i].terminate()
            for i in range(inst_num, old_num):
                self.models[name][i].join()
            self.models[name] = self.models[name][0:inst_num]

    def forever_terminate(self, meta_info):
        assert 'name' in meta_info
        name = meta_info['name']
        assert name in self.models.keys()
        self.unable_models.append(name)
        num = len(self.models.keys())
        # 等待全部运行完毕
        while self.input_queues[name].qsize() != 0:
            pass
        for i in range(num):
            self.models[name][i].terminate()
        for i in range(num):
            self.models[name][i].join()
        self.input_queues.pop(name)
        self.models.pop(name)
        self.unable_models.remove(name)
