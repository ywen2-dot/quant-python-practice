import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
pd.set_option('expand_frame_repr', False)
engine = create_engine(
    'sqlite:////Users/yuhanwen/Desktop/量化交易/yfinance crash course/量化入门/1.Python股票量化投资系统课程/第四课 构建自己的股票数据库/stock.db'
)

selected = pd.read_sql("select * from stock_500_stock_selected", con=engine)
target_code = selected.loc[0, "股票代码"]
target_name = selected.loc[0, "股票名称"]
df = pd.read_sql(
    f"""
    select 股票代码, 股票名称, 交易日期, 收盘价, 涨跌幅, MA5, MA20
    from stock_500_daily_cumulative
    where 股票代码 = '{target_code}'
    order by 交易日期
    """,
    con=engine
)
df["交易日期"] = pd.to_datetime(df["交易日期"])
df = df.dropna(subset=["MA5", "MA20", "涨跌幅"]).reset_index(drop=True)

df["position"] = 0
df.loc[df["MA5"] > df["MA20"], "position"] = 1

df["position_yesterday"] = df["position"].shift(1).fillna(0)
print(df.head(30))
#计算策略收益率
df['market_return']=df['涨跌幅']
df['strategy_return']=df['market_return']*df['position_yesterday']
#计算累积收益
df['market_cum_return']=(1+df['market_return']).cumprod()-1
df['strategy_cum_return']=(1+df['strategy_return']).cumprod()-1
print(df.tail(30))
#画两个线图
plt.figure(figsize=[12,6])
df['trade_date']=df['交易日期']
plt.plot(df['trade_date'],df['market_cum_return'],label='buy_and_hold')
plt.plot(df['trade_date'],df['strategy_return'],label='mean_strategy')
plt.title(f"{target_code} {target_name} cumulative return")
plt.xlabel("trade_date")
plt.ylabel("cumulative_return")
plt.legend()
plt.grid(True)
plt.show()
print(df[["strategy_return", "strategy_cum_return"]].tail(20))