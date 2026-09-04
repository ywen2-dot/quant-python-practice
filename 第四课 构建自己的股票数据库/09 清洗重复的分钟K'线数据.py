import pandas as pd
import shutil
from sqlalchemy import create_engine

engine = create_engine("sqlite:///stock.db")

# 先备份数据库
shutil.copy2(
    "stock.db",
    "stock_before_minute_cleanup.db"
)

# 读取分钟K线
minute = pd.read_sql_query(
    "SELECT * FROM minute_kline",
    engine
)

print("清理前数量：", len(minute))

# 删除重复分钟
clean_minute = minute.drop_duplicates(
    subset=["股票代码", "Datetime"],
    keep="last"
).copy()

print("清理后数量：", len(clean_minute))

# 替换原来的分钟K线表
clean_minute.to_sql(
    "minute_kline",
    engine,
    if_exists="replace",
    index=False
)

print("分钟K线清理完成")

engine.dispose()