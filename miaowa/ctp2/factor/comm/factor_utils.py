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

BAR_COLUMN_LIST = ['O', 'H', 'L', 'C', 'V', 'AP', 'AV', 'BP', 'BV']
BAR_COLUMN_DICT = {
    'open': 'O',
    'high': 'H',
    'low': 'L',
    'close': 'C',
    'volume': 'V',
    'ask_price': 'AP',
    'ask_volume': 'AV',
    'bid_price': 'BP',
    'bid_volume': 'BV'
}

class FactorUtil:
    
    @staticmethod
    def to_iso_date(date) -> str:
        return f"{date[0:4]}-{date[4:6]}-{date[6:8]}"
    
    @staticmethod
    def read_tick_from_sql(symbol, 
                           start_date, 
                           start_time='00:00:00', 
                           batch_size=10000) -> pd.DataFrame:
        """
        :param symbol
        :param start_date - format 20240101
        :param start_time - format 00:00:00
        :param batch_size
        """
        url = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        con = sqlalchemy.create_engine(url)

        table_name = f"Q_TICK_{symbol}"
        start_date = FactorUtil.to_iso_date(start_date)
        
        sql = """
            SELECT id, data_ts as ts,
                symbol, date, time,
                open, high, low, close, volume,
                open_interest, turnover, last, average, settle,
                pre_close, pre_settle, pre_open_interest,
                ask1_price, ask1_volume, bid1_price, bid1_volume
            FROM {table_name}
            WHERE data_ts >= '{start_date} {start_time}'
            ORDER BY data_ts limit {batch_size}
        """.format(table_name=table_name,
                   start_date=start_date,
                   start_time=start_time,
                   batch_size=batch_size)
        # print(sql)
        df = pd.read_sql_query(sql, con, index_col='ts')
        df.index = pd.to_datetime(df.index)
        return df

    @staticmethod
    def read_bar_from_sql(bar_name, 
                          start_date, 
                          start_time='00:00:00', 
                          batch_size=10000) -> pd.DataFrame:
        """
        :param bar_name - FG2401_MIN_1
        :param start_date - format %Y%m%d
        :param start_time - format %H:%i:%s
        :param batch_size
        """
        url = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        con = sqlalchemy.create_engine(url)
        
        table_name = f"Q_BAR_{bar_name}"
        start_date = FactorUtil.to_iso_date(start_date)
        
        sql = """
            SELECT id, data_ts as ts,
                symbol, date, time,
                open, high, low, close, volume,
                ask_price, ask_volume, bid_price, bid_volume
            FROM {table_name}
            WHERE data_ts >= '{start_date} {start_time}'
            AND status = 1
            ORDER BY data_ts limit {batch_size}
        """.format(table_name=table_name,
                   start_date=start_date,
                   start_time=start_time,
                   batch_size=batch_size)
        # print(sql)
        df = pd.read_sql_query(sql, con, index_col='ts')
        df.index = pd.to_datetime(df.index)
        return df

    @staticmethod
    def get_bar_df(bar_name,
                   start_date,
                   start_time='00:00:00',
                   batch_size=10000) -> pd.DataFrame:
        """
        :param bar_name - FG2401_MIN_1
        :param start_date - format %Y%m%d
        :param start_time - format %H:%i:%s
        :param batch_size
        """
        bar_df = FactorUtil.read_bar_from_sql(bar_name,
                                              start_date,
                                              start_time,
                                              batch_size)
        bar_df.rename(columns=BAR_COLUMN_DICT, inplace=True)
        return bar_df[BAR_COLUMN_LIST]
    
    @staticmethod
    def concat_shift_df(df, periods, columns) -> pd.DataFrame:
        """
        """
        col_postfix = '_' + str(periods)
        df_ = df[columns].shift(periods)
        df_.columns = [c + col_postfix for c in columns]
        return pd.concat([df_, df], axis=1)

    @staticmethod
    def get_window_bar_df(bar_name,
                          start_date,
                          start_time='00:00:00',
                          batch_size=10000,
                          window_period=10) -> pd.DataFrame:
        # get bar df
        bar_df = FactorUtil.get_bar_df(bar_name,
                                       start_date,
                                       start_time,
                                       batch_size)
        for i in range(1, window_period):
            bar_df = FactorUtil.concat_shift_df(bar_df, i, BAR_COLUMN_LIST)
        return bar_df
        
               