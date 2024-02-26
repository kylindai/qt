import numpy as np
import pandas as pd
import talib

from typing import List, Union, Dict, Tuple
from datetime import datetime


class TimeSeries:
    def __init__(self, name: str, series: pd.Series = None, max_length: int = 0):
        self._name = name
        self._series = series
        if series is None:
            self._series = pd.Series()
        assert isinstance(
            self._series, pd.Series), f"TimeSeries {name} Type Error"
        self._series.name = name
        self._max_length = max_length

    def name(self):
        return self._series.name

    def max_length(self, length: int):
        self._max_length = length

    def push(self, index: Union[datetime, str], item: object, sort: bool = False):
        # insert
        if isinstance(index, datetime):
            self._series[index] = item
        elif isinstance(index, str):
            self._series[self._datetime(index)] = item
        else:
            raise IndexError('TimeSeries index error')
        # sort by index
        if sort:
            self._series.sort_index(inplace=True)
        # drop the first item
        if self._max_length > 0 and len(self._series) > self._max_length:
            self.pop()

    def pop(self):
        self._series.drop(self._series.index[0], inplace=True)

    def index(self) -> List[pd.DatetimeIndex]:
        return self._series.index

    def items(self) -> List:
        return self._series.to_list()

    def _datetime(self, datetime_str: str, fmt: str = "%Y%m%d %H:%M:%S") -> datetime:
        return datetime.strptime(datetime_str, fmt)

    def __getitem__(self, i: Union[int, slice]):
        # index
        if isinstance(i, int):
            # param validate
            if i > 0:
                raise IndexError("TimeSeries index must less than 1")
            # get value by index
            try:
                return self._series[i - 1]
            except Exception as e:
                raise IndexError("TimeSeries index out of range")
        # slice
        elif isinstance(i, slice):
            # param validate
            if (i.start is not None and i.start > 0) or (i.stop is not None and i.stop > 0):
                raise IndexError("TimeSeries slice index must less than 1")
            # start
            start = None
            if i.start is not None and i.start <= 0:
                start = i.start - 1
            # stop
            stop = None
            if i.stop is not None and i.stop < 0:
                stop = i.stop
            # get series by slice
            try:
                return TimeSeries(self._series[start:stop])
            except Exception as e:
                raise IndexError("TimeSeries index out of range")
        else:
            raise IndexError('TimeSeries index error')

    def __len__(self) -> int:
        return len(self._series)


class TimeLine(TimeSeries):

    def __init__(self, name: str, series: pd.Series = None, max_length: int = 0):
        super().__init__(name, series, max_length)

    def SMA(self, period):
        return TimeSeries(f"{self._name}.SMA({period})", talib.SMA(self._series, timeperiod=period))

    def EMA(self, period):
        return TimeSeries(f"{self._name}.EMA({period})", talib.EMA(self._series, timeperiod=period))

    def RSI(self, period):
        return TimeSeries(f"{self._name}.RSI({period})", talib.RSI(self._series, timeperiod=period))
