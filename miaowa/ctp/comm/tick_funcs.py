# coding: utf-8

import numpy as np
import pandas as pd
import sqlalchemy
import matplotlib as plt
import matplotlib.pyplot as plt


def read_tick_from_sql(symbol, start_date, batch_size=10000) -> pd.DataFrame:
    """
    """
    url = "mysql+pymysql://miaowa:pass1234@localhost:3306/miaowadb"
    con = sqlalchemy.create_engine(url)
    table = f"Q_TICK_{symbol}"
    sql = f"SELECT id, symbol, date, time," \
          f" CONCAT(date, ' ', time) as ts," \
          f" open, high, low, close, volume," \
          f" open_interest, turnover, last, average, settle," \
          f" pre_close, pre_settle, pre_open_interest," \
          f" ask1_price, ask1_volume, bid1_price, bid1_volume" \
          f" FROM {table}" \
          f" WHERE date >= '{start_date}'" \
          f" ORDER BY id limit {batch_size}"
    df = pd.read_sql_query(sql, con, index_col='ts')
    df.index = pd.to_datetime(df.index)
    return df


def show_tick_volume(df):
    """
    绘制收盘价和买1卖1量，成交量的关系
    """
    # 整个图的大小
    plt.figure(figsize=(30, 20))

    # 将整个图分成 4*4 个格子，坐标从 0,0 算起
    top1 = plt.subplot2grid((4, 4), (0, 0))
    top1.plot(df['close'], label='close')
    plt.title('close')
    plt.legend(loc=2)

    top2 = plt.subplot2grid((4, 4), (0, 1))
    top2.plot(df['close'], label='close')
    plt.title('close')
    plt.legend(loc=2)

    # 将整个图分成 4*4 个格子，坐标从 1,0 算起
    buttom1 = plt.subplot2grid((4, 4), (1, 0))
    buttom1.plot(df['ask1_volume'], label='ask1_volume')
    buttom1.plot(df['bid1_volume'], label='bid1_volume')
    plt.title('ask1 & bid1')
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
    buttom.plot(df['ask1_volume' + col_postfix], label='ask1_volume' + col_postfix)
    buttom.plot(df['bid1_volume' + col_postfix], label='bid1_volume' + col_postfix)
    plt.title('ask1 & bid1')
    plt.legend(loc=2)

    # 子图之间的水平间距
    plt.subplots_adjust(hspace=0.8)