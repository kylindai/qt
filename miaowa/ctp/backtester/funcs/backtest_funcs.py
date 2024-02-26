# coding: utf-8

import numpy as np
import pandas as pd
import sqlalchemy
import matplotlib as plt
import matplotlib.pyplot as plt
import mplfinance as mpf

from typing import List, Tuple

MYSQL_HOST = "ctp-mysql"
MYSQL_PORT = 3306
MYSQL_USER = "miaowa"
MYSQL_PASS = "pass1234"
MYSQL_DB = "miaowadb"


BAR_COLUMNS = ['open', 'high', 'low', 'close', 'volume']
ORDER_COLUMNS = ['insert_time', 'price', 'volume', 'direction', 'offset', 'order_type', 'order_source', 'order_status']
TRADE_COLUMNS = ['insert_time', 'price', 'volume', 'direction', 'offset', 'trade_type', 'trade_source']
BAR_TRADE_COLUMNS = ['open', 'high', 'low', 'close', 'volume', 'price', 'direction', 'offset']
JOIN_BAR_COLUMNS = ['close']
JOIN_TRADE_COLUMNS = ['price', 'volume', 'direction', 'offset']


def read_backtest_from_sql(backtest_id):
    """
    :param backtest_id
    """
    url = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    con = sqlalchemy.create_engine(url)
    table = "T_BACKTEST"
    sql = f"SELECT * FROM {table}" \
          f" WHERE id = {backtest_id}"
    # print(sql)
    df = pd.read_sql_query(sql, con, index_col='id')
    return df
    

def read_bar_from_sql(backtest_id, symbol, bar_type, bar_freq) -> pd.DataFrame:
    """
    :param backtest_id
    :param symbol
    :param bar_type
    :param bar_freq
    """
    url = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    con = sqlalchemy.create_engine(url)
    table = f"Q_BAR_{symbol}_{bar_type}_{bar_freq}"
    sql = f"SELECT b.id, b.symbol, b.date, b.time," \
          f" CONCAT(b.date, ' ', b.time) as ts," \
          f" b.open, b.high, b.low, b.close, b.volume," \
          f" b.ask_price, b.ask_volume, b.bid_price, b.bid_volume" \
          f" FROM T_BACKTEST a, {table} b" \
          f" WHERE a.id = {backtest_id}" \
          f" AND CONCAT(b.date, b.time) >= CONCAT(a.bar_date_start, a.bar_time_start)" \
          f" AND CONCAT(b.date, b.time) <= CONCAT(a.bar_date_end, a.bar_time_end)" \
          f" ORDER BY b.date, b.time"
    # print(sql)
    df = pd.read_sql_query(sql, con, index_col='ts')
    df.index = pd.to_datetime(df.index)
    return df


def read_order_from_sql(backtest_id: int, direction: str = None, offset: str = None) -> pd.DataFrame:
    """
    :param backtest_id
    """
    url = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    con = sqlalchemy.create_engine(url)
    direction_cond = f" AND direction = '{direction}'" if direction else ""
    offset_cond = f" AND offset = '{offset}'" if offset else ""
    sql = f"SELECT id, broker_id, user_id," \
          f" trading_day, settlement_id, front_id, session_id, request_id," \
          f" CONCAT(insert_date, ' ', insert_time) as ts," \
          f" insert_date, insert_time, update_time, cancel_time," \
          f" symbol, price, volume, direction, offset," \
          f" order_id, order_ref, order_seq," \
          f" order_type, order_source, order_status" \
          f" FROM T_ORDER" \
          f" WHERE settlement_id = {backtest_id}" \
          f" {direction_cond}" \
          f" {offset_cond}" \
          f" ORDER BY ts"
    # print(sql)
    df = pd.read_sql_query(sql, con, index_col='ts')
    df.index = pd.to_datetime(df.index)
    return df


def read_orders_from_sql(backtest_id: int) -> List[pd.DataFrame]:
    """
    :param backtest_id
    """
    df = read_order_from_sql(backtest_id)
    df_long_open   = df.query("direction == 'LONG' & offset == 'OPEN'")
    df_long_close  = df.query("direction == 'LONG' & offset == 'CLOSE'")
    df_short_open  = df.query("direction == 'SHORT' & offset == 'OPEN'")
    df_short_close = df.query("direction == 'SHORT' & offset == 'CLOSE'")
    return (df_long_open, df_long_close, df_short_open, df_short_close)


def read_trade_from_sql(backtest_id: int, direction: str = None, offset: str = None) -> pd.DataFrame:
    """
    :param backtest_id
    :param direction
    :param offset
    """
    url = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    con = sqlalchemy.create_engine(url)
    direction_cond = f" AND direction = '{direction}'" if direction else ""
    offset_cond = f" AND offset = '{offset}'" if offset else ""
    sql = f"SELECT id, broker_id, user_id," \
          f" trading_day, settlement_id, trade_id, trade_seq," \
          f" CONCAT(trade_date, ' ', trade_time) as ts," \
          f" trade_date, trade_time, trade_type, trade_source," \
          f" symbol, price, volume, direction, offset," \
          f" order_ref, order_sys_id" \
          f" FROM T_TRADE" \
          f" WHERE settlement_id = {backtest_id}" \
          f" {direction_cond}" \
          f" {offset_cond}" \
          f" ORDER BY ts"
    # print(sql)
    df = pd.read_sql_query(sql, con, index_col='ts')
    df.index = pd.to_datetime(df.index)
    return df


def read_trades_from_sql(backtest_id: int) -> List[pd.DataFrame]:
    """
    :param backtest_id
    """
    df = read_trade_from_sql(backtest_id)[TRADE_COLUMNS]
    df_long_open   = df.query("direction == 'LONG' & offset == 'OPEN'")
    df_long_close  = df.query("direction == 'LONG' & offset == 'CLOSE'")
    df_short_open  = df.query("direction == 'SHORT' & offset == 'OPEN'")
    df_short_close = df.query("direction == 'SHORT' & offset == 'CLOSE'")
    return (df_long_open, df_long_close, df_short_open, df_short_close)


def merge_bar_trade_df(bar_df: pd.DataFrame, trade_df: pd.DataFrame) -> pd.DataFrame:
    """
    :param bar_df
    :param trade_df
    """
    return pd.merge(bar_df[JOIN_BAR_COLUMNS], 
                    trade_df[JOIN_TRADE_COLUMNS], 
                    how='outer', 
                    left_index=True, 
                    right_index=True)


def join_bar_trade_df(bar_df: pd.DataFrame, trade_df: pd.DataFrame) -> pd.DataFrame:
    """
    :param bar_df
    :param trade_df
    """
    if trade_df is not None and len(trade_df.index) > 0:
        return bar_df[JOIN_BAR_COLUMNS].join(trade_df[JOIN_TRADE_COLUMNS])
    return bar_df[JOIN_BAR_COLUMNS]


def display_bar_candle(title: str, 
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
