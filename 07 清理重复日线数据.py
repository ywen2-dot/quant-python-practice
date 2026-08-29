import pandas as pd
import shutil
from sqlalchemy import create_engine
engine=create_engine('sqlite:///stock.db')
#备份原数据库
shutil.copy2(
    'stock.db',
    'stock_before_cleanup.db'
)
#读取日线数据
daily = pd.read_sql_query(
    "SELECT * FROM daily_kline",
    engine
)
#同一日线数据
daily["Date"] = (
    daily["Date"]
    .astype(str)
    .str.strip()
    .str[:10]
)
print('清理前数量',len(daily))
#删除重复数据
clean_daily=daily.drop_duplicates(
    subset=['股票代码','Date'],
    keep='first'
).copy()
print("清理后数量：", len(clean_daily))
#用清理后的数据替换原来的旧K线表
clean_daily.to_sql(
    'daily_kline',
    engine,
    index=False,
    if_exists='replace'
)