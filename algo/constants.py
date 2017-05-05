from enum import Enum


class Order(Enum):
    Unknown = -1
    Style = 1
    Terminate = 0


class RetCode(Enum):
    NO_ERR = 0
    ERR_READ_IMG = 1