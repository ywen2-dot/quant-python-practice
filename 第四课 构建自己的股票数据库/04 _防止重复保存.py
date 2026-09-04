import sqlite3
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
pd.set_option('expand_frame_repr', False)

symbol='600000.SS'
#连接sql用于保存数据
engine=create_engine('sqlite:///stock.db')
#sqlite3连接，用于查询数据
conn=sqlite3.connect('stock.db')
#创建yahoo finance对象
stock=yf.Ticker(symbol)
#获取分钟和日K线数据
minute_df=stock.history(
    period='1d',
    interval='1m',
    auto_adjust=False,
    timeout=60
)
#获取日线数据
daily_df=stock.history(
    period='5d',
    interval='1d',
    auto_adjust=False,
    timeout=60
)
#只保留最后一根
latest_minute=minute_df.tail(1).copy()
#把时间索引换成普通列
latest_minute=latest_minute.reset_index()
#添加股票代码
latest_minute['股票代码']=symbol
#添加本次抓取时间
latest_minute['抓取时间']=datetime.now()
#把时间转换成文字，方便比较
latest_minute['Datetime']=latest_minute['Datetime'].astype(str)
#读取数据库中原来的分钟数据
old_minute=pd.read_sql_table(
    'minute_kline',
    engine
)
#数据库里面的时间也转换成文字
old_minute['Datetime']=old_minute['Datetime'].astype(str)
#取出最新的分钟K线时间
new_time=latest_minute.loc[0,'Datetime']
#取出股票代码
# 从最新一分钟K线中取出股票代码
new_symbol = latest_minute.loc[0, "股票代码"]
# 从最新一分钟K线中取出时间
new_time = latest_minute.loc[0, "Datetime"]
#检查相同的股票，相同的时间是否数据已经存在
if ((old_minute['Datetime']==new_symbol)&old_minute['Datetime']==new_time).any():
    print('这跟K线已经保存过了')
else:
    latest_minute.to_sql(
        'minute_kline',
        engine,
        if_exists='append',
        index=False,
    )
    print('最新一分钟K线保存成功')
print(new_time)
print(minute_df.tail(1))
#获取日K
print(daily_df.tail(1))
if daily_df.empty:
    print("没有获取到日K线数据")
else:
    #取最新的一根日K线
    latest_daily=daily_df.tail(1).copy()
    #吧日期索引变成普通列
    latest_daily=latest_daily.reset_index()
    #添加股票代码
    latest_daily['股票代码']=symbol
    #s数据库里面的数据转换成文字
    latest_daily["Date"] = (
        latest_daily["Date"]
        .astype(str))
#添加程序抓取时间
latest_daily['抓取时间']=datetime.now()
#读取数据库中原来的日线数据
old_daily = pd.read_sql_table(
    "daily_kline",
    engine
)
# 取出新日线的日期
new_date = latest_daily.loc[0, "Date"]

print("本次检查的日线日期：", new_date)

# 检查股票代码是否相同
same_code = old_daily["股票代码"] == symbol

# 检查日期是否相同
same_date = old_daily["Date"] == new_date

# 两个条件同时满足，说明重复
is_duplicate = (
        same_code & same_date
).any()

if is_duplicate:
    print("这根日 K 线已经保存过，不再重复保存")

else:
    latest_daily.to_sql(
        "daily_kline",
        engine,
        if_exists="append",
        index=False
    )

    print("最新日 K 线保存成功")