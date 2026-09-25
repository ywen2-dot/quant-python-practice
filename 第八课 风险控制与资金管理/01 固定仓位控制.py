import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
pd.set_option('expand_frame_repr', False)
#连接数据库
engine=create_engine('sqlite:////Users/yuhanwen/Desktop/量化交易/yfinance crash course/量化入门/1.Python股票量化投资系统课程/第四课 构建自己的股票数据库/stock.db')
#读取股票数据
select_stocks=pd.read_sql('select * from stock_500_stock_selected',engine)
print(select_stocks.head())
stock_code=select_stocks.loc[0,'股票代码']
stock_name=select_stocks.loc[0,'股票名称']
print(stock_code)
print(stock_name)
#选取一只股票来研究
df=pd.read_sql(
    f"""
    select * from stock_500_daily_cumulative
    where 股票代码='{stock_code}'
    """
    ,engine
)
print(df.head())
#数据清洗
df['交易日期']=pd.to_datetime(df['交易日期'])
df=df.dropna(subset=['涨跌幅','MA5','MA20']).reset_index(drop=True)
#生成交易信号
df['position']=0
df.loc[df['MA5']>df['MA20'],'position']=1
df['yesterday_position']=df['position'].shift(1).fillna(0)
#固定仓位控制
position_size=0.3
df['real_yesterday_position']=df['yesterday_position']*position_size
#计算收益
df['market_return']=df['涨跌幅']
df['strategy_return']=df['real_yesterday_position']*df['market_return']
# 8. 计算手续费
df["trade_flag"] = df["position"].diff().abs().fillna(0)

fee_rate = 0.0005

df["transaction_cost"] = (
    df["trade_flag"] * position_size * fee_rate
)

df["strategy_return_net"] = (
    df["strategy_return"] - df["transaction_cost"]
)

# 9. 计算累计收益
df["market_cum_return"] = (
    (1 + df["market_return"]).cumprod() - 1
)

df["strategy_cum_return_net"] = (
    (1 + df["strategy_return_net"]).cumprod() - 1
)

# 10. 计算最大回撤
net_value = 1 + df["strategy_cum_return_net"]

df["running_max"] = net_value.cummax()

df["drawdown"] = net_value / df["running_max"] - 1

max_drawdown = df["drawdown"].min()

# 11. 回测指标
total_return_strategy = df["strategy_cum_return_net"].iloc[-1]

annual_return = (
    (1 + total_return_strategy) ** (252 / len(df)) - 1
)

annual_volatility = (
    df["strategy_return_net"].std() * np.sqrt(252)
)

sharpe_ratio = (
    annual_return / annual_volatility
    if annual_volatility != 0
    else 0
)

trade_count = int(df["trade_flag"].sum())

# 12. 打印结果
print(f"股票：{stock_code} {stock_name}")
print(f"仓位比例：{position_size:.0%}")
print(f"策略总收益：{total_return_strategy:.2%}")
print(f"策略年化收益：{annual_return:.2%}")
print(f"策略年化波动率：{annual_volatility:.2%}")
print(f"最大回撤：{max_drawdown:.2%}")
print(f"夏普比率：{sharpe_ratio:.2f}")
print(f"交易次数：{trade_count}")

# 13. 画图
plt.figure(figsize=(12, 6))

plt.plot(
    df["交易日期"],
    df["market_cum_return"],
    label="Buy and Hold"
)

plt.plot(
    df["交易日期"],
    df["strategy_cum_return_net"],
    label="MA Strategy 30% Position"
)

plt.title(f"{stock_code} {stock_name} Position Control Backtest")
plt.xlabel("Trade Date")
plt.ylabel("Cumulative Return")
plt.legend()
plt.grid(True)
plt.show()