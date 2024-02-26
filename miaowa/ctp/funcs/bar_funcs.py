# coding: utf-8

import numpy as np
import pandas as pd
import sqlalchemy
import matplotlib as plt
import matplotlib.pyplot as plt
import mplfinance as mpf

from typing import List, Dict, Tuple

MYSQL_HOST = "ctp-mysql"
MYSQL_PORT = 3306
MYSQL_USER = "miaowa"
MYSQL_PASS = "pass1234"
MYSQL_DB = "miaowadb"

def read_tick_from_sql(symbol, 
                       start_date, 
                       start_time = '00:00:00', 
                       batch_size=10000) -> pd.DataFrame:
    """
    :param symbol
    :param start_date
    :param start_time
    :param batch_size
    """
    url = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    con = sqlalchemy.create_engine(url)
    table = f"Q_TICK_{symbol}"
    sql = f"SELECT id, symbol, date, time," \
          f" CONCAT(date, ' ', time) as ts," \
          f" open, high, low, close, volume," \
          f" open_interest, turnover, last, average, settle," \
          f" pre_close, pre_settle, pre_open_interest," \
          f" ask1_price, ask1_volume, bid1_price, bid1_volume" \
          f" FROM {table}" \
          f" WHERE CONCAT(date, time) >= '{start_date}{start_time}'" \
          f" ORDER BY id limit {batch_size}"
    # print(sql)
    df = pd.read_sql_query(sql, con, index_col='ts')
    df.index = pd.to_datetime(df.index)
    return df


def read_bar_from_sql(symbol, 
                      start_date, 
                      start_time = '00:00:00', 
                      bar_type='SEC', 
                      bar_freq=1, 
                      batch_size=10000) -> pd.DataFrame:
    """
    :param symbol
    :param start_date
    :param start_time
    :param bar_type
    :param bar_freq
    :param batch_size
    """
    url = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    con = sqlalchemy.create_engine(url)
    table = f"Q_BAR_{symbol}_{bar_type}_{bar_freq}"
    sql = f"SELECT id, symbol, date, time," \
          f" CONCAT(date, ' ', time) as ts," \
          f" open, high, low, close, volume," \
          f" ask_price, ask_volume, bid_price, bid_volume" \
          f" FROM {table}" \
          f" WHERE CONCAT(date, time) >= '{start_date}{start_time}'" \
          f" ORDER BY id limit {batch_size}"
    # print(sql)
    df = pd.read_sql_query(sql, con, index_col='ts')
    df.index = pd.to_datetime(df.index)
    return df


def show_bar_candle(title: str, 
                    bar_df: pd.DataFrame, 
                    apds: List[pd.DataFrame] = None, 
                    plot_type: str = 'hollow_and_filled'):
    """
    :param title
    :param bar_df
    :param apds
    :param plot_type
    """
    plot_style = mpf.make_mpf_style(base_mpf_style='yahoo',
                                    edgecolor='black',
                                    gridstyle=':',
                                    y_on_right=False)
    plot_kws = dict(title=title,
                    figsize=(14, 7),
                    figscale=1.2,
                    figratio=(1, 1),
                    tight_layout=True,
                    volume=True,
                    style=plot_style,
                    type=plot_type,
                    xrotation=0,
                    show_nontrading=False,
                    datetime_format='%m-%d %H:%M:%S')

    if apds is not None and len(apds) > 0:
        mpf.plot(bar_df, **plot_kws, addplot=apds)
    else:
        mpf.plot(bar_df, **plot_kws)    

    
def show_bar_volume(df, colume_1='open', colume_2='close'):
    """
    绘制收盘价和买1卖1量, 成交量的关系
    """
    # 整个图的大小
    plt.figure(figsize=(30, 20))

    # 将整个图分成 4*4 个格子，坐标从 0,0 算起
    top1 = plt.subplot2grid((4, 4), (0, 0))
    top1.plot(df[colume_1], label=colume_1)
    plt.title(colume_1)
    plt.legend(loc=2)

    top2 = plt.subplot2grid((4, 4), (0, 1))
    top2.plot(df[colume_2], label=colume_2)
    plt.title(colume_2)
    plt.legend(loc=2)

    # 将整个图分成 4*4 个格子，坐标从 1,0 算起
    buttom1 = plt.subplot2grid((4, 4), (1, 0))
    buttom1.plot(df['ask_volume'], label='ask_volume')
    buttom1.plot(df['bid_volume'], label='bid_volume')
    plt.title('ask & bid')
    plt.legend(loc=2)

    # 将整个图分成 4*4 个格子，坐标从 1,0 算起
    buttom2 = plt.subplot2grid((4, 4), (1, 1))
    buttom2.plot(df['volume'], label='volume')
    plt.title('volume')
    plt.legend(loc=2)

    # 子图之间的水平间距
    plt.subplots_adjust(hspace=0.2)
    plt.show();

    
def concat_shift(df, periods, columns) -> pd.DataFrame:
    """
    将下一个时间periods的量合并到当前行中，返回DataFrame
    """
    # 列名后缀
    col_postfix = '_' + str(periods)
    
    # 计算和下一个时间periods的差异量生产df2
    df2 = df[columns].shift(-periods)
    
    # 指定df2的列名
    df2.columns = [c + col_postfix for c in columns]
    # print(df_.columns)

    # 合并df和df2, 并返回
    return pd.concat([df, df2], axis=1)


def batch_concat_shift(df, batch_size, columns) -> pd.DataFrame:
    """
    将下N个时间的量合并到当前行中，返回DataFrame
    """
    df2 = df.copy()
    for i in range(1, batch_size + 1):
        df2 = concat_shift(df2, i, columns)
    return df2


def concat_diff(df, periods, columns) -> pd.DataFrame:
    """
    将下一个时间periods的差异量合并到当前行中，返回DataFrame
    """
    # 列名后缀
    col_postfix = '_' + str(periods)
    
    # 计算和下一个时间periods的差异量生产df2
    df2 = df[columns].diff(periods)
    
    # 指定df2的列名
    df2.columns = [c + col_postfix for c in columns]
    # print(df_.columns)

    # 合并df和df2, 并返回
    return pd.concat([df, df2], axis=1)


def display_diff(df, periods):
    col_postfix = '_' + str(periods)
    # 整个图的大小
    plt.figure(figsize=(12, 8))

    # 将整个图分成 6*4 个格子，坐标从 0,0 算起，合并2行4列
    top = plt.subplot2grid((6, 4), (0, 0), rowspan=2, colspan=4)
    top.plot(df['close' + col_postfix], label='close' + col_postfix)
    plt.title('close' + col_postfix)
    plt.legend(loc=2)

    # 将整个图分成 6*4 个格子，坐标从 2,0 算起，合并2行4列
    buttom = plt.subplot2grid((6, 4), (2, 0), rowspan=2, colspan=4)
    # buttom.plot(df['volume'], label='volume')
    buttom.plot(df['ask_volume' + col_postfix], label='ask_volume' + col_postfix)
    buttom.plot(df['bid_volume' + col_postfix], label='bid_volume' + col_postfix)
    plt.title('ask & bid')
    plt.legend(loc=2)

    # 子图之间的水平间距
    plt.subplots_adjust(hspace=0.8)