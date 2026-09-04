import pandas as pd
pd.set_option('display.max_columns', None)
from sqlalchemy import create_engine
#连接数据库
engine=create_engine('sqlite:////Users/yuhanwen/Desktop/量化交易/yfinance crash course/自学量化/1.Python股票量化投资系统课程/第四课 构建自己的股票数据库/stock.db')
#从数据库中读取数据
stock_daily=pd.read_sql(
    "select 股票代码,股票名称,交易日期,收盘价 from stock_500_daily",
        engine
)
#把交易日期改成真正的交易日期
stock_daily['交易日期']=pd.to_datetime(stock_daily['交易日期'])
#收盘价改成数字格式
stock_daily['收盘价']=pd.to_numeric(stock_daily['收盘价'],errors='coerce')
# 按股票和日期排序
stock_daily = stock_daily.sort_values(
    ["股票代码", "交易日期"]
).reset_index(drop=True)

# 计算每只股票每天的涨跌幅
stock_daily["涨跌幅"] = (
    stock_daily
    .groupby("股票代码")["收盘价"]
    .pct_change()
)

# 把小数形式转换成百分比
stock_daily["涨幅比例"] = (
    stock_daily["涨跌幅"] * 100
)

#计算5日均线
stock_daily['MA5']=stock_daily.groupby('股票代码')['收盘价'].transform(lambda x: x.rolling(5).mean())
#计算20日均线
stock_daily['MA20']=stock_daily.groupby('股票代码')['收盘价'].transform(lambda x: x.rolling(20).mean())
# 查看数据
print(stock_daily.head(5))
print(stock_daily.tail(3))
#只看浦发银行这一个数据
print(stock_daily[stock_daily['股票代码']=='sh6000000'].tail(5))
#保存计算结果
stock_daily.to_sql(
    "stock_500_daily_return",
    engine,
    if_exists='replace',
    index=False
)
# 第二步：把表改名
with engine.begin() as conn:
    conn.exec_driver_sql("""
        ALTER TABLE stock_500_daily_return
        RENAME TO stock_500_daily_ma
    """)

print("数据已替换，并改名为 stock_500_daily_ma")
