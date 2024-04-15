import numpy as np
import pandas as pd
import sqlalchemy
import matplotlib as plt
import matplotlib.pyplot as plt

from .db_conf import Config

MYSQL_HOST = Config['host']
MYSQL_PORT = Config['port']
MYSQL_USER = Config['username']
MYSQL_PASS = Config['password']
MYSQL_DB = Config['database']


class FactorUtil:
    
    @staticmethod
    def to_iso_date(date) -> str:
        return f"{date[0:4]}-{date[4:6]}-{date[6:8]}"
    
    @staticmethod
    def read_tick_from_sql(symbol, 
                           start_date, 
                           start_time = '00:00:00', 
                           batch_size=10000) -> pd.DataFrame:
        """
        :param symbol
        :param start_date - format 20240101
        :param start_time - format 00:00:00
        :param batch_size
        """
        url = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        con = sqlalchemy.create_engine(url)

        table = f"Q_TICK_{symbol}"
        start_date = FactorUtil.to_iso_date(start_date)
        
        sql = f"SELECT id, data_ts as ts," \
              f" symbol, date, time," \
              f" open, high, low, close, volume," \
              f" open_interest, turnover, last, average, settle," \
              f" pre_close, pre_settle, pre_open_interest," \
              f" ask1_price, ask1_volume, bid1_price, bid1_volume" \
              f" FROM {table}" \
              f" WHERE data_ts >= '{start_date} {start_time}'" \
              f" ORDER BY data_ts limit {batch_size}"
        # print(sql)
        df = pd.read_sql_query(sql, con, index_col='ts')
        df.index = pd.to_datetime(df.index)
        return df

    @staticmethod
    def read_bar_from_sql(bar_name, 
                          start_date, 
                          start_time = '00:00:00', 
                          batch_size=10000) -> pd.DataFrame:
        """
        :param bar_name - FG2401_MIN_1
        :param start_date - format %Y%m%d
        :param start_time - format %H:%i:%s
        :param batch_size
        """
        url = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        con = sqlalchemy.create_engine(url)
        
        table = f"Q_BAR_{bar_name}"
        start_date = FactorUtil.to_iso_date(start_date)
        
        sql = f"SELECT id, data_ts as ts," \
              f" symbol, date, time," \
              f" open, high, low, close, volume," \
              f" ask_price, ask_volume, bid_price, bid_volume" \
              f" FROM {table}" \
              f" WHERE data_ts >= '{start_date} {start_time}'" \
              f" AND status = 1" \
              f" ORDER BY data_ts limit {batch_size}"
        # print(sql)
        df = pd.read_sql_query(sql, con, index_col='ts')
        df.index = pd.to_datetime(df.index)
        return df
