# -*- coding: utf-8 -*-

from __future__ import print_function

import Queue
import logging.config

from algo.constants import *
from algo.model import Model

logging.config.fileConfig('../logging.ini', disable_existing_loggers=False)

# meta_info = {
#     "name": "la_muse",
#     "chinese_name": "谬斯",
#     "tf_model_path": "../models/la_muse.pb",
#     "tf_input_name": "img_placeholder:0",
#     "tf_input_size": [1, 800, 800, 3],
#     "tf_output_name": "add_37:0",
#     "tf_use_gpu": False,
#     "tf_gpu_id": 0,
#     "meta_image": "../static/images/la_muse.jpg"
# }
meta_info = {
    "name": "the_scream",
    "chinese_name": "尖叫",
    "tf_model_path": "../models/chinese_ink.pb",
    "tf_input_name": "img_placeholder:0",
    "tf_input_size": [1, 800, 800, 3],
    "tf_output_name": "add_37:0",
    "tf_use_gpu": False,
    "tf_gpu_id": 0,
    "meta_image": "../static/images/the_scream.jpg"
}

input_queue = Queue.Queue()
output_queue = Queue.Queue()

model = Model(meta_info, input_queue, output_queue)

model.start()

input_queue.put({'order': Order.Style,
                 'order_id': 1,
                 'img_path': '../static/images/love4.jpg',
                 'save_path': '../static/images/loveMIMI.jpg'})
input_queue.put({'order': Order.Terminate})

model.join()

while True:
    try:
        a = output_queue.get_nowait()
        print(a)
    except Queue.Empty:
        break
