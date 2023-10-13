import time
import json
from datetime import datetime


def date_string(fmt: str = None) -> str:
    if fmt is None:
        fmt = "%Y%m%d"
    return datetime.now().strftime(fmt)


def time_string(fmt: str = None) -> str:
    if fmt is None:
        fmt = "%H:%M:%S"
    return datetime.now().strftime(fmt)


def datetime_string(dt: datetime, fmt: str = None) -> str:
    """
    :param fmt: "%Y-%m-%d %H:%M:%S.%f"
    """
    if fmt is None:
        fmt = "%Y-%m-%d %H:%M:%S.%f"
    return dt.strftime(fmt)


def get_datetime(datetime_str: str, fmt: str = "%Y%m%d %H:%M:%S") -> datetime:
    return datetime.strptime(datetime_str, fmt)


def json_string(object) -> str:
    return json.dumps(dict(object), ensure_ascii=False, separators=(',', ':'))


