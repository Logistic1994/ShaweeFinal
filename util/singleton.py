# -*- coding: utf-8 -*-


def singleton(class_):
    """
    单例模式，thread-safe
    :param class_: 
    :return: 
    """
    instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return get_instance
