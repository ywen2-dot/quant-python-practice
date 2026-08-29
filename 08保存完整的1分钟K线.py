from sqlalchemy import create_engine
import pandas as pd
import yfinance as yf
from datetime import datetime
pd.set_option('expand_frame_repr', False)
#基本设置
symbol='600000.SS'
engine=create_engine('sqlite:///stock.db')
stock=yf.Ticker(symbol)


#获取最近一天的股票数据
minute_df=stock.history(
    period='1d',
    interval='1m',
    auto_adjust=False,
    timeout=60
)
# 判断是否成功
if minute_df.empty:
    print('没有获取到分钟线')
    engine.dispose()
    raise SystemExit
# 把时间索引变成普通列
minute_df = minute_df.reset_index()

# 添加股票代码
minute_df["股票代码"] = symbol

# 添加抓取时间
minute_df["抓取时间"] = datetime.now()

# 时间统一成字符串
minute_df["Datetime"] = (
    minute_df["Datetime"]
    .astype(str)
    .str.strip()
)
# 读取数据库中原来的分钟K线
old_minute = pd.read_sql_query(
    "SELECT * FROM minute_kline",
    engine
)


# 统一旧数据的时间格式
old_minute["Datetime"] = (
    old_minute["Datetime"]
    .astype(str)
    .str.strip()
)


# 删除本次抓取内部的重复分钟
minute_df = minute_df.drop_duplicates(
    subset=["股票代码", "Datetime"],
    keep="last"
)

# 制作旧数据清单
old_keys = set(
    zip(
        old_minute["股票代码"].astype(str),
        old_minute["Datetime"].astype(str)
    )
)

# 保存真正的新数据
new_rows = []

# 遍历本次新抓取的数据
for _, row in minute_df.iterrows():
    key = (
        str(row["股票代码"]),
        str(row["Datetime"])
    )

    if key not in old_keys:
        new_rows.append(row)
        old_keys.add(key)

new_minute = pd.DataFrame(new_rows)
#b=保存分钟数据
if new_minute.empty:
    print('没有新的分钟K线,不需要保存')
else:
    new_minute.to_sql(
        'minute_kline',
        engine,
        if_exists='append',
        index=False
    )
    print("分钟K线保存成功")
#查看数据库结果
saved_minute=pd.read_sql_query(
    "SELECT * FROM minute_kline",
    engine
)
print(saved_minute.tail(10))

