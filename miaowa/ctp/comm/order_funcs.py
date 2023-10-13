# coding: utf-8

import numpy as np
import pandas as pd
import sqlalchemy
import matplotlib as plt
import matplotlib.pyplot as plt

MYSQL_HOST = "ctp-mysql"
MYSQL_PORT = 3306
MYSQL_USER = "miaowa"
MYSQL_PASS = "pass1234"
MYSQL_DB = "miaowadb"

def read_order_from_sql(symbol, 
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
    table = f"R_TICK_{symbol}"
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