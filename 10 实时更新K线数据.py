from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime
import yfinance as yf
pd.set_option('expand_frame_repr', False)
engine=create_engine('sqlite:///stock.db')
symbol='600000.SS'
stock=yf.Ticker(symbol)
#查看被保存的分钟数据
saved_minute=pd.read_sql_query(
    'select * from minute_kline',
    engine
)
print(saved_minute)
#查看被保存在daily_kline的日线
saved_daily=pd.read_sql_query(
    'select * from daily_kline',
    engine
)
print(saved_daily)
#重复执行下面缩近代码3次
while True:
    print('开始获取分钟线')
    minute_df=stock.history(
        period='1d',
        interval='1m',
        auto_adjust=False,
        timeout=60
    )
    if minute_df.empty:
        print('没有获取数据')
    else:
        latest=minute_df.tail(1).copy()
        latest=latest.reset_index()
        latest['股票代码']=symbol
        latest['抓取时间']=datetime.now()
        latest['Datetime']=latest['Datetime'].astype(str).str.strip()
        old_minute=pd.read_sql_query(
            "select 股票代码,Datetime from minute_kline order by Datetime desc",
            engine
        )
        old_keys = set(
            zip(
                old_minute["股票代码"].astype(str),
                old_minute["Datetime"].astype(str)
            )
        )
        new_keys=(symbol,str(latest.loc[0,'Datetime']))
        if new_keys not in old_keys:
            latest.to_sql(
                'minute_kline',
                engine,
                if_exists='append',
                index=False
            )
            print('新的数据保存成功')
        else:
            print('没有保存新的数据')


    # 自动获取最新日K线
    print("开始获取最新日K线")

    daily_df = stock.history(
        period="1d",
        interval="1d",
        auto_adjust=False,
        timeout=60
    )

    if daily_df.empty:
        print("没有获取到日K线")

    else:
        # 只取最新的一根日K线
        latest_daily = daily_df.tail(1).copy()

        # 把日期索引变成普通列
        latest_daily = latest_daily.reset_index()

        # 统一日期格式
        latest_daily["Date"] = (
            latest_daily["Date"]
            .astype(str)
            .str.strip()
            .str[:10]
        )

        # 添加股票代码和抓取时间
        latest_daily["股票代码"] = symbol
        latest_daily["抓取时间"] = datetime.now()

        # 读取数据库中已有的日线日期
        old_daily = pd.read_sql_query(
            "select 股票代码, Date from daily_kline",
            engine
        )

        # 统一旧数据日期格式
        old_daily["Date"] = (
            old_daily["Date"]
            .astype(str)
            .str.strip()
            .str[:10]
        )

        # 制作旧数据的唯一标识
        old_keys = set(
            zip(
                old_daily["股票代码"].astype(str),
                old_daily["Date"].astype(str)
            )
        )

        # 制作最新日线的唯一标识
        new_daily_key = (
            symbol,
            str(latest_daily.loc[0, "Date"])
        )

        # 判断是否重复
        if new_daily_key in old_keys:
            print("这根日K线已经存在，不保存")

        else:
            latest_daily.to_sql(
                "daily_kline",
                engine,
                if_exists="append",
                index=False
            )

            print("新的日K线保存成功")


    # 最后再关闭数据库
    engine.dispose()

    print("自动更新结束")
    engine.dispose()
    print('自动更新结束')