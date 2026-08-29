import yfinance as yf
from sqlalchemy import create_engine
from datetime import datetime
#1基本设置
#浦发银行
symbol='600000.SS'
#创建SQLite 数据库连接
engine=create_engine('sqlite:///stock.db')
#创建股票对象
stock=yf.Ticker(symbol)
#获取最近一天的1分钟K线
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
#保存最新的一分钟K线
print('分钟数据行数',len(daily_df))
print('分钟数据行数',len(minute_df))
if minute_df.empty:
    print('没有获取到1分钟的数据')
else:
    #只保留最后一根
    latest_minute=minute_df.tail(1).copy
    #把时间索引换成普通列
    latest_minute=minute_df.reset_index()
    #添加股票代码
    latest_minute['股票代码']=symbol
    #添加本次抓取时间
    latest_minute['抓取时间']=datetime.now()
    #保存到minute.kline表
    latest_minute.to_sql(
        'minute_kline',
        engine,
        if_exists='append',
        index=False,
    )
    print('最新一分钟K线保存成功')
#保存最新的日线
if minute_df.empty:
    print('没有获取到1分钟的数据')
else:
    #只保留最后一根
    latest_minute=minute_df.tail(1).copy()
    #把时间索引换成普通列
    latest_minute=latest_minute.reset_index()
    #添加股票代码
    latest_minute['股票代码']=symbol
    #添加本次抓取时间
    latest_minute['抓取时间']=datetime.now()
    #保存到minute.kline表
    latest_minute.to_sql(
        'minute_kline',
        engine,
        if_exists='append',
        index=False,
    )
    print('最新一分钟K线保存成功')
if daily_df.empty:
    print('没有获取到一天的数据')
else:
    # 只保留最后一根
    latest_daily = daily_df.tail(1).copy()
    # 把时间索引换成普通列
    latest_daily =latest_daily.reset_index()
    # 添加股票代码
    latest_daily['股票代码'] = symbol
    # 添加本次抓取时间
    latest_daily['抓取时间'] = datetime.now()
    # 保存到minute.kline表
    latest_daily.to_sql(
        'daily_kline',
        engine,
        if_exists='append',
        index=False,
    )
    print('最新日K线保存成功')
print('数据库保存完成')