# -*- coding: utf-8 -*-

import Queue
import logging
import threading
import time

import numpy as np
import tensorflow as tf
from PIL import Image
from tensorflow.python.platform import gfile

from constants import Order, RetCode

logger = logging.getLogger(__name__)


class Model(threading.Thread):
    """
    风格模型处理线程，一个model load一个风格模型，对应一个线程服务
    """
    def __init__(self, meta_info, input_queue, output_queue, index):
        """
        对象构建函数
        :param meta_info: json格式的模型信息 
        :param input_queue: 输入队列，输入队列是优先级队列
        :param output_queue: 输出队列
        :param index: 处理相同的风格列表中的第几个？
        """
        threading.Thread.__init__(self)
        for key in ['name', 'tf_model_path', 'tf_input_name',
                    'tf_input_size', 'tf_output_name', 'tf_use_gpu']:
            assert key in meta_info
        assert len(meta_info['tf_input_size']) == 4
        self.name = meta_info['name']
        self.input_name = meta_info['tf_input_name']
        self.input_size = meta_info['tf_input_size']
        self.output_name = meta_info['tf_output_name']
        self.index = index
        with gfile.FastGFile(meta_info["tf_model_path"], 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            logger.info("{} {} load {} successfully.".format(self.getName(),
                                                             self.name,
                                                             meta_info["tf_model_path"]))
        self.graph_def = graph_def
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.use_gpu = meta_info['tf_use_gpu']
        if self.use_gpu:
            self.gpu_id = meta_info['tf_gpu_id']
        self.stop = False

    def terminate(self):
        self.stop = True

    def run(self):
        if not self.use_gpu:
            device = '/cpu:0'
            config = tf.ConfigProto()
            logger.info("{} {} use cpu.".format(self.getName(), self.name))
        else:
            device = '/gpu:{}'.format(self.gpu_id)
            gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.1, allow_growth=True)
            config = tf.ConfigProto(gpu_options=gpu_options, allow_soft_placement=True)
            logger.info("{} {} use gpu.".format(self.getName(), self.name))
        with tf.Graph().as_default(), tf.device(device), tf.Session(config=config) as sess:
            # prepare
            tf.import_graph_def(self.graph_def, name='')
            formula = sess.graph.get_tensor_by_name(self.output_name)

            while not self.stop:
                try:
                    # get request object
                    # contains (order_id, order_type, [img_path, save_path])
                    prior, req_obj = self.input_queue.get_nowait()
                except Queue.Empty:
                    time.sleep(1)
                    continue
                if req_obj['order'] != Order.Style:
                    continue
                if 'img_path' not in req_obj:
                    continue
                order_id = req_obj['order_id']
                img_path = req_obj['img_path']
                save_path = req_obj['save_path']
                logger.info("{} {} Style for {}.".format(self.getName(),
                                                         self.name,
                                                         img_path))

                # 打开图片
                start = time.time()
                try:
                    image = Image.open(img_path)
                    image = image.convert('RGB')
                except IOError:
                    self.output_queue.put((order_id, RetCode.ERR_READ_IMG))
                    logger.info("{} {} Load image {} failed.".format(self.getName(),
                                                                     self.name,
                                                                     img_path))
                    continue

                # 进行resize
                orig_height = image.height
                orig_width = image.width
                target_height = self.input_size[1]
                target_width = self.input_size[2]
                if orig_height < target_height and orig_width < target_width:
                    width = orig_width
                    height = orig_height
                    resized = False
                else:
                    if float(orig_height) / orig_width > float(target_height) / target_width:
                        height = target_height
                        width = int(float(orig_width) / orig_height * height)
                    else:
                        width = target_width
                        height = int(float(orig_height) / orig_width * width)
                    image = image.resize((width, height))
                    resized = True

                # load into np array
                I = np.asarray(image)
                T = np.zeros(self.input_size, dtype=np.float)
                T[0, 0:height, 0:width, :] = I

                # compute
                preds = sess.run(formula, feed_dict={self.input_name: T})
                S = preds[0, 0:height, 0:width, :].copy()

                styled = Image.fromarray(np.uint8(S))
                if resized:
                    styled = styled.resize((orig_width, orig_height))
                styled.save(save_path)

                style_duration = time.time() - start
                self.output_queue.put((order_id, RetCode.NO_ERR, save_path, style_duration))
