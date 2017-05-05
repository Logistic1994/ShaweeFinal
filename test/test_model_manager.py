# -*- encoding: utf-8 -*-
from algo.model_manager import ModelManager

import logging
import logging.config
import threading

logging.config.fileConfig('../logging.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

meta_infos = [
  {
    "name": "la_muse",
    "chinese_name": "谬斯",
    "tf_model_path": "../models/la_muse.pb",
    "tf_input_name": "img_placeholder:0",
    "tf_input_size": [1, 800, 800, 3],
    "tf_output_name": "add_37:0",
    "tf_use_gpu": False,
    "tf_gpu_id": 0,
    "meta_image": "../static/images/la_muse.jpg"
  },
  {
    "name": "the_scream",
    "chinese_name": "尖叫",
    "tf_model_path": "../models/the_scream.pb",
    "tf_input_name": "img_placeholder:0",
    "tf_input_size": [1, 800, 800, 3],
    "tf_output_name": "add_37:0",
    "tf_use_gpu": False,
    "tf_gpu_id": 0,
    "meta_image": "../static/images/the_scream.jpg"
  }
]
model_manager = ModelManager()
model_manager.load_models(meta_infos)
model_manager.start()

model_manager2 = ModelManager() # ModelManager is Singleton


def thread_fuc(index):
    global model_manager2
    ii = index % 2
    names = ["la_muse", "the_scream"]
    flag, order_id = model_manager2.eval(names[ii],
                                        "../static/images/chicago.jpg",
                                        "../static/images/{}_{}.jpg".format(names[ii], index))
    logger.info('{}, {}'.format(flag, order_id))
    if flag:
        while True:
            ret = model_manager2.check(order_id)
            if not ret:
                continue
            else:
                logger.info(str(ret))
                break

threads = []
for i in range(10):
    t = threading.Thread(target=thread_fuc, args=(i, ))
    threads.append(t)
    t.start()

logger.info(str(model_manager2.get_all_queue_length()))

for i in range(10):
    threads[i].join()
model_manager2.terminate()