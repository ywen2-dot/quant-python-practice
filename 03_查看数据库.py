#打开stock.db，里面查看有哪些表，每张表有多少条数据
import sqlite3
import pandas as pd
pd.set_option('expand_frame_repr', None)
#打开数据库
conn=sqlite3.connect('stock.db')
#查询数据库中有哪些表
tables=pd.read_sql(
    'select name from sqlite_master'
    ,conn
)
print(tables)
#查看minute_kline表
print('\nminute_kline表:')
minute_kline=pd.read_sql(
    'select count(*) as 数据数量 from minute_kline'
    ,conn
)
print('minute_kline的数据条数')
print(minute_kline)
#最近5条数据
minute_date=pd.read_sql(
    ' select *  from minute_kline order by rowid desc limit 5'

    ,conn

)
print('minute_kline最新5条数据')
print(minute_kline)
#查看daily_kline表
print('\ndaily_kline表:')
daily_count=pd.read_sql(
    'select count(*) as 数据数量 from daily_kline'
    ,conn
)
print('daily_kline的数据条数')
print(daily_count)
#最近5条数据
daily_date=pd.read_sql(
    ' select *  from daily_kline order by rowid desc limit 5'

    ,conn

)
print('daily_kline最新5条数据')
print(daily_date)
#关闭数据库连接
conn.close()