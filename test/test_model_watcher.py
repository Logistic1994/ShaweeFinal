# -*- encoding: utf-8 -*-
import json
import logging.config
import time

from algo.model_manager import ModelManager
from algo.model_watcher import ModelWatcher

logging.config.fileConfig('../logging.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

meta_infos_1 = [
    {
        "name": "la_muse",
        "chinese_name": "谬斯",
        "tf_model_path": "../models/la_muse.pb",
        "tf_input_name": "img_placeholder:0",
        "tf_input_size": [1, 800, 800, 3],
        "tf_output_name": "add_37:0",
        "tf_use_gpu": False,
        "tf_gpu_id": 0,
        "inst_num": 1,
        "meta_image": "../static/images/la_muse.jpg"
    }
]

meta_infos_2 = [
    {
        "name": "the_scream",
        "chinese_name": "尖叫",
        "tf_model_path": "../models/the_scream.pb",
        "tf_input_name": "img_placeholder:0",
        "tf_input_size": [1, 800, 800, 3],
        "tf_output_name": "add_37:0",
        "tf_use_gpu": False,
        "tf_gpu_id": 0,
        "inst_num": 2,
        "meta_image": "../static/images/the_scream.jpg"
    }
]

with open('/tmp/models.json', 'w') as f:
    json.dump(meta_infos_1, f)

model_manager = ModelManager()
model_manager.load_models(meta_infos_1)
model_manager.start()

model_watcher = ModelWatcher('/tmp/models.json')
model_watcher.start_watch()

time.sleep(2)
# 扩容测试
meta_infos_1[0]['inst_num'] = 2
with open('/tmp/models.json', 'w') as f:
    json.dump(meta_infos_1, f)

time.sleep(2)

# 缩容测试
meta_infos_1[0]['inst_num'] = 1
with open('/tmp/models.json', 'w') as f:
    json.dump(meta_infos_1, f)

time.sleep(2)

# 新增模型测试
meta_infos_1.append(meta_infos_2[0])
with open('/tmp/models.json', 'w') as f:
    json.dump(meta_infos_1, f)

time.sleep(2)
# 彻底删除模型
meta_infos_1.pop(1)
with open('/tmp/models.json', 'w') as f:
    json.dump(meta_infos_1, f)

time.sleep(2)
model_watcher.stop_watch()
model_manager.terminate()
