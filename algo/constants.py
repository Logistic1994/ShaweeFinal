# -*- coding: utf-8 -*-

from enum import Enum


class Order(Enum):
    """
    任务需求
    Style：进行风格化任务
    Terminate：消灭这个风格线程
    """
    Unknown = -1
    Style = 1
    Terminate = 0


class RetCode(Enum):
    """
    任务返回码
    """
    NO_ERR = 0
    ERR_READ_IMG = 1
