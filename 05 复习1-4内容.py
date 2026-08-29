from sqlalchemy import create_engine
import pandas as pd
import yfinance as yf
pd.set_option('expand_frame_repr', False)
from datetime import datetime
symbol='600000.SS'
#连接数据库
engine=create_engine('sqlite:///stock.db')
#创建股票对象
stock=yf.Ticker(symbol)
#获取yahoo数据
#获取最近一天的数据
minute_df=stock.history(
    period='1d',
    interval='1m',
    auto_adjust=False,
    timeout=60
)
#获取近5日的数据
daily_df=stock.history(
    period='5d',
    interval='1d',
    auto_adjust=False,
    timeout=60
)
print("获取到的分钟数据",minute_df)
print("获取到的天数据",daily_df)
#保存最新一分钟K线
if minute_df.empty:
    print('没有获取到最新的K线')
else:
    #保存最新的一根分钟K线
    latest_minute=minute_df.tail(1).copy()
    #吧datetime换成普通索引
    latest_minute=latest_minute.reset_index()
    #查看实际列名
    print(latest_minute.columns.tolist())
    #添加股票代码
    latest_minute['股票代码']=symbol
    #添加抓取时间
    latest_minute['抓取时间']=datetime.now()
    #吧datetime换成字符串
    latest_minute['Datetime']=latest_minute['Datetime'].astype(str)
    #取出旧的分钟数据
    old_minute=pd.read_sql_table(
        'minute_kline',
        engine
    )
    #同一旧数据时间格式
    old_minute['Datetime']=(old_minute['Datetime']).astype(str)
    #取出新数据的股票代码
    new_symbol=latest_minute.loc[0,'股票代码']
    #取出新数据的K线时间
    new_time=latest_minute.loc[0,'Datetime']
    #检查股票代码，获取时间是否相同
    minute_same_code=(
        old_minute['股票代码']==new_symbol
    )
    minute_same_time=(
        old_minute['Datetime']==new_time
    )
    #股票代码跟时间都一样才能算重复
    minute_is_duplicate=(minute_same_time&minute_same_code).any()
    if minute_is_duplicate:
        print('获取的分K线重复')
    else:
        latest_minute.to_sql(
            'minute_kline',
            engine,
            if_exists='append',
            index=False
        )
        print('分钟K线保存成功')
    print('本次整理后的K线')
    print(latest_minute[["Datetime",
                "股票代码",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
                "抓取时间"]])
    #保存最新日K数据
    # 保存最新一分钟K线
    if daily_df.empty:
        print('没有获取到最新的K线')
    else:
        # 保存最新的一根分钟K线
        latest_daily = daily_df.tail(1).copy()
        # 吧datetime换成普通索引
        latest_daily= latest_daily.reset_index()
        # 查看实际列名
        print(latest_daily.columns.tolist())

        # 添加股票代码
        latest_daily['股票代码'] = symbol
        # 添加抓取时间
        latest_daily['抓取时间'] = datetime.now()
        # 吧datetime换成字符串
        latest_daily['Date'] =latest_daily['Date'].astype(str)
        # 取出旧的分钟数据
        old_daily= pd.read_sql_table(
            'daily_kline',
            engine
        )
        # 同一旧数据时间格式
        old_daily['Date'] = (old_daily['Date']).astype(str)
        # 取出新数据的股票代码
        new_daily_symbol = latest_daily.loc[0, '股票代码']
        # 取出新数据的K线时间
        new_date = latest_daily.loc[0, 'Date']
        # 检查股票代码，获取时间是否相同
        daily_same_code = (
                old_daily['股票代码'] == new_daily_symbol
        )
        daily_same_time = (
                old_daily['Date'] == new_date
        )
        # 股票代码跟时间都一样才能算重复
        daily_is_duplicate = (daily_same_time & daily_same_code).any()
        if daily_is_duplicate:
            print('获取的日K线重复')
        else:
            latest_daily.to_sql(
                'daily_kline',
                engine,
                if_exists='append',
                index=False
            )
            print('riK线保存成功')
        print('本次整理后的K线')
        print(latest_daily[["Date",
                             "股票代码",
                             "Open",
                             "High",
                             "Low",
                             "Close",
                             "Volume",
                             "抓取时间"]])