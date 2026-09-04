from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


pd.set_option("expand_frame_repr", False)

# 1. 连接你的数据库
engine = create_engine("sqlite:///stock.db")

# 2. 你的500只股票csv所在文件夹
csv_folder = Path(
    "/Users/yuhanwen/Desktop/量化交易/yfinance crash course/自学量化/1.Python股票量化投资系统课程/第三课 pandas高阶/baostock_500_stocks_5y/daily"
)

# 3. 找到这个文件夹里所有csv文件
csv_files = sorted(csv_folder.glob("*.csv"))

print("找到csv文件数量：", len(csv_files))

# 4. 用来装所有股票数据
all_data = []

# 5. 一个一个读取csv
for file in csv_files:
    print("正在读取：", file.name)

    df = pd.read_csv(file)

    all_data.append(df)

# 6. 把500个表合并成一个大表
stock_500_daily = pd.concat(
    all_data,
    ignore_index=True
)

# 7. 统一日期和股票代码格式
stock_500_daily["交易日期"] = (
    stock_500_daily["交易日期"]
    .astype(str)
    .str.strip()
)

stock_500_daily["股票代码"] = (
    stock_500_daily["股票代码"]
    .astype(str)
    .str.strip()
)

# 8. 删除重复数据
stock_500_daily = stock_500_daily.drop_duplicates(
    subset=["股票代码", "交易日期"],
    keep="last"
)

# 9. 按股票代码和交易日期排序
stock_500_daily = stock_500_daily.sort_values(
    ["股票代码", "交易日期"]
)

print("合并后的总行数：", len(stock_500_daily))
print(stock_500_daily.head())
print(stock_500_daily.tail())

# 10. 保存到数据库的新表
stock_500_daily.to_sql(
    "stock_500_daily",
    engine,
    if_exists="replace",
    index=False
)

print("500只股票日线数据导入完成")

# 11. 检查数据库结果
check_count = pd.read_sql_query(
    "select count(*) as 数据总数 from stock_500_daily",
    engine
)

check_stock_count = pd.read_sql_query(
    "select count(distinct 股票代码) as 股票数量 from stock_500_daily",
    engine
)

check_date = pd.read_sql_query(
    "select min(交易日期) as 最早日期, max(交易日期) as 最新日期 from stock_500_daily",
    engine
)

print(check_count)
print(check_stock_count)
print(check_date)

engine.dispose()