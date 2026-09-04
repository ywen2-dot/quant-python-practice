import pandas as pd
from sqlalchemy import create_engine

pd.set_option("expand_frame_repr", False)

# 连接数据库
engine = create_engine(
    "sqlite:////Users/yuhanwen/Desktop/量化交易/yfinance crash course/"
    "自学量化/1.Python股票量化投资系统课程/"
    "第四课 构建自己的股票数据库/stock.db"
)

# 读取风险汇总表
risk_summary = pd.read_sql(
    "select * from stock_500_risk_summary",
    con=engine
)

# 查看前5行
print(risk_summary.head())

# 1. 按累计收益率排名
top_return = risk_summary.sort_values(
    "最后累计收益率",
    ascending=False
).head(10)

print("累计收益率最高的前10只股票")
print(top_return)

# 2. 按年化波动率从低到高排名
low_risk = risk_summary.sort_values(
    "年化波动率百分比",
    ascending=True
).head(10)

print("波动率最低的前10只股票")
print(low_risk)

# 3. 按收益风险比排名
top_score = risk_summary.sort_values(
    "收益风险比",
    ascending=False
).head(10)

print("收益风险比最高的前10只股票")
print(top_score)
#筛选条件
good_stocks=risk_summary[(risk_summary['最后累计收益率'])>0 & (risk_summary['年化波动率百分比']<40) & (risk_summary['收益风险比']>0)].copy()
# 筛选后，再按收益风险比从高到低排序
good_stocks=good_stocks.sort_values(
    '收益风险比',
    ascending=False
).reset_index(drop=True)
print('筛选出来的候选股票')
print(good_stocks.head())
#将候选出来的股票存进数据库
good_stocks.to_sql(
    "stock_500_stock_selected",
    con=engine,
    if_exists='replace',
    index=False
)
print('候选股票保存成功')