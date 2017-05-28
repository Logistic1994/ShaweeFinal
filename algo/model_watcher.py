# -*- encoding: utf-8 -*-

import json
import logging
import os

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from algo.model_manager import ModelManager
from util.singleton import singleton

logger = logging.getLogger(__name__)


@singleton
class ModelWatcher(FileSystemEventHandler):
    def __init__(self, meta_path):
        self.meta_path = meta_path
        self.old_json = None
        self.observer = None

    def start_watch(self):
        with open(self.meta_path) as f:
            self.old_json = json.load(f)
        self.observer = Observer()
        self.observer.schedule(self, os.path.dirname(self.meta_path), recursive=False)
        self.observer.start()

    def stop_watch(self):
        self.observer.stop()
        self.observer.join()

    def on_modified(self, event):
        logger.info(event.src_path)
        if event.src_path != self.meta_path:
            return
        logger.info("{} has been modified".format(self.meta_path))

        # 重点关注的几个配置
        # 1. 模型路径
        # 2. 是否使用了GPU
        # 3. inst_num
        # 注意，缩容到0和彻底关闭的区别，彻底关闭要求输入队列必须为空，缩容不一定
        model_manager = ModelManager()
        with open(self.meta_path) as f:
            new_json = json.load(f)
        old_map = {}
        new_map = {}
        for meta_info in self.old_json:
            old_map[meta_info["name"]] = meta_info
        for meta_info in new_json:
            new_map[meta_info["name"]] = meta_info
        for old_name in old_map:
            if old_name in new_map:
                if old_map[old_name]['tf_model_path'] != new_map[old_name]['tf_model_path']:
                    # 更换了模型
                    logger.info("style {} change model from {} to {}".format(old_name, old_map[old_name]['tf_model_path'], new_map[old_name]['tf_model_path']))
                    model_manager.change_inst_num(old_map[old_name], 0)
                    model_manager.load_new(new_map[old_name])
                elif old_map[old_name]['tf_use_gpu'] != new_map[old_name]['tf_use_gpu']:
                    # CPU、GPU变化
                    logger.info("style {} change cpu/gpu".format(old_name))
                    model_manager.change_inst_num(old_map[old_name], 0)
                    model_manager.load_new(new_map[old_name])
                elif old_map[old_name]['inst_num'] != new_map[old_name]['inst_num']:
                    # 仅仅是数量变化了
                    logger.info("style {} change inst_num from {} to {}".format(old_name, old_map[old_name]['inst_num'], new_map[old_name]['inst_num']))
                    model_manager.change_inst_num(old_map[old_name], new_map[old_name]['inst_num'])
            else:
                # 彻底删除了
                logger.info("style {} has been removed".format(old_name))
                model_manager.forever_terminate(old_map[old_name])
        for new_name in new_map:
            if new_name not in old_map:
                # 新增了模型
                logger.info("style {} has beed added".format(new_name))
                model_manager.load_new(new_map[new_name])
        self.old_json = new_json
