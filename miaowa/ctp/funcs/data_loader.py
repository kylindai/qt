import pymysql
import pandas as pd
import io

DbConf = {
    "host": 'localhost',
    "port": 3306,
    "user": 'miaowa',
    "password": 'pass1234',
    "db": 'miaowadb'
}

COLUMNS = ['close', 'volume', 'average', 'ask1_price', 'ask1_volume', 'bid1_price', 'bid1_volume']


def to_tick(r) -> dict:
    return {
        'id': r[0],
        'symbol': r[1],
        'date': r[2],
        'time': r[3],
        '1': r[4],
        '2': r[5],
        '3': r[6],
        '4': r[7],
        '5': r[8],
        '6': r[9],
        '7': r[10],
        '8': r[11],
        '9': r[12],
        '10': r[13],
        '21': r[14],
        '22': r[15],
        '23': r[16],
        '51': r[17],
        '52': r[18],
        '61': r[19],
        '62': r[20]
    }


def to_tick_line(r) -> str:
    t = to_tick(r)
    tick_line = f"{t['id']},{t['symbol']},{t['date']},{t['time']}," \
                f"{t['1']},{t['2']},{t['3']},{t['4']},{t['5']}," \
                f"{t['6']},{t['7']},{t['8']},{t['9']},{t['10']}," \
                f"{t['21']},{t['22']},{t['23']}," \
                f"{t['51']},{t['52']},{t['61']},{t['62']}\n"
    return tick_line


class DataLoader:

    def __init__(self, symbol, trade_date):
        self._symbol = symbol
        self.trade_date = trade_date

    def load_data(self, start_time, batch_size=10000, periods=120, split_ratio=0.2, cat_func=None):
        table = f"TICKER_{self._symbol.replace('.', '_')}_{self.trade_date}"
        sql = f"SELECT id, symbol, date, time," \
              f" open, high, low, close, volume," \
              f" open_interest, turnover, last, average, settle," \
              f" pre_close, pre_settle, pre_open_interest," \
              f" ask1_price, ask1_volume, bid1_price, bid1_volume" \
              f" FROM {table}" \
              f" WHERE time >= '{start_time}'" \
              f" ORDER BY id limit {batch_size}"

        mysql_conn = None
        try:
            mysql_conn = pymysql.connect(host=DbConf['host'],
                                         port=DbConf['port'],
                                         user=DbConf['user'],
                                         password=DbConf['password'],
                                         db=DbConf['db'])

            tick_lines = []
            with mysql_conn.cursor() as cursor:
                cursor.execute(sql)
                rs = cursor.fetchall()
                for r in rs:
                    tick_lines.append(to_tick_line(r))

            # print(tick_lines)
            if tick_lines:
                data_x, data_y = self._read_data(tick_lines, periods, cat_func)
                return self._split_data(data_x, data_y, split_ratio)

        except Exception as e:
            print(e)
        finally:
            if not mysql_conn:
                mysql_conn.close()

    def _read_data(self, tick_lines, concat_periods, cat_func):
        # read csv string to data frame
        df = pd.read_csv(io.StringIO("".join(tick_lines)), index_col=0)
        df.index.name = 'id'
        df.columns = ['symbol', 'date', 'time',
                      'open', 'high', 'low', 'close', 'volume',
                      'open_interest', 'turnover', 'last', 'average', 'settle',
                      'pre_close', 'pre_settle', 'pre_open_interest',
                      'ask1_price', 'ask1_volume', 'bid1_price', 'bid1_volume']

        # raw data
        raw_data = df[COLUMNS]
        
        # data x
        data_x = self._concat_historical_data(raw_data, concat_periods, COLUMNS)
        data_x['change'] = data_x['close'] - data_x[f"close_{concat_periods}"]
        
        # label -- 二分类
        # data_y = data_x['close_diff'].apply(lambda x: 1 if x else 0)
        
        # label -- 多分类
        data_y = data_x['change'] if not cat_func else data_x['change'].apply(lambda x: cat_func(x))
        
        # min value from 0
        min_value = data_y.min()
        if min_value != 0:
            data_y = data_y.apply(lambda x: x - min_value)
        
        # feature remove current columns
        data_x.drop(['change'], axis=1, inplace=True)
        data_x.drop(COLUMNS, axis=1, inplace=True)
        # print('data_x.shape, data_y.shape:', data_x.shape, data_y.shape)
        
        return data_x[1:], data_y[1:]

    def _concat_historical_data(self, df, concat_periods, concat_columns) -> pd.DataFrame:
        df2 = df.copy()
        for i in range(1, concat_periods + 1):
            df2 = self._concat_shift(df2, i, concat_columns)
        return df2

    def _concat_shift(self, df, periods, columns) -> pd.DataFrame:
        """
        将下periods个时间的量合并到当前行中，返回DataFrame
        """
        col_postfix = '_' + str(periods)
        df2 = df[columns].shift(periods)
        df2.columns = [col + col_postfix for col in columns]
        return pd.concat([df, df2], axis=1)

    def _split_data(self, data_x, data_y, split_ratio=0.3):
        # split train and test data
        s = int(data_x.shape[0] * (1 - split_ratio))
        return (data_x[:s], data_y[:s]), (data_x[s:], data_y[s:])