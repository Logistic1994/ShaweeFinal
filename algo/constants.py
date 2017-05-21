# -*- coding: utf-8 -*-

from enum import Enum


class Order(Enum):
    """
    任务需求，后面的id既表示order的种类，又表示任务的优先级，越小优先级越高
    Style：进行风格化任务
    """
    Unknown = 1000
    Style = 100


class RetCode(Enum):
    """
    任务返回码
    """
    NO_ERR = 0
    ERR_READ_IMG = 1
