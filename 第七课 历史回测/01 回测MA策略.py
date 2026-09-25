import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

pd.set_option("expand_frame_repr", False)

# 1. 连接数据库
engine = create_engine(
    "sqlite:////Users/yuhanwen/Desktop/量化交易/yfinance crash course/"
    "量化入门/1.Python股票量化投资系统课程/"
    "第四课 构建自己的股票数据库/stock.db"
)

# 2. 读取候选股票池中的第一只股票
selected = pd.read_sql(
    "select * from stock_500_stock_selected",
    con=engine
)

target_code = selected.loc[0, "股票代码"]
target_name = selected.loc[0, "股票名称"]

# 3. 读取该股票的日线和均线数据
df = pd.read_sql(
    f"""
    select 股票代码, 股票名称, 交易日期, 收盘价, 涨跌幅, MA5, MA20
    from stock_500_daily_cumulative
    where 股票代码 = '{target_code}'
    order by 交易日期
    """,
    con=engine
)

engine.dispose()

df["交易日期"] = pd.to_datetime(df["交易日期"])
df = df.dropna(subset=["涨跌幅", "MA5", "MA20"]).reset_index(drop=True)

# 4. 生成策略持仓
# MA5 在 MA20 上方：持有股票，position = 1
# MA5 在 MA20 下方：空仓，position = 0
df["position"] = 0
df.loc[df["MA5"] > df["MA20"], "position"] = 1

# 今天的涨跌幅由昨天收盘后的仓位决定，避免未来函数
df["position_yesterday"] = df["position"].shift(1).fillna(0)

# 5. 计算策略毛收益
df["market_return"] = df["涨跌幅"]
df["strategy_return"] = (
    df["market_return"] * df["position_yesterday"]
)
#判断今天是否已经交易
df['trade_flag']=df['position'].diff().abs().fillna(0)
#设置手续费
fee_rate=0.0005
#如果今天发生买入或者卖出，就扣一次手续费
df['transaction_cost']=df['trade_flag']*fee_rate
#扣除手续费后的真实策略收益
df['strategy_return_net']=df['strategy_return']-df['transaction_cost']
#买入并持有的累积收益
df['market_cum_return']=(1+df['market_return']).cumprod()-1
#策略扣费后的累积收益
df['strategy_cum_return']=(1+df['strategy_return_net']).cumprod()-1
#将累积收益变成净值
net_value=1+df['strategy_cum_return']
#记录历史最高净值
df['running_max']=net_value.cummax()
#计算回测
df['drawdown']=net_value/df['running_max']-1
#计算最大回测
max_drawdown=df['drawdown'].min()
#策略最后一天的总收益，总收益
total_return=df['strategy_cum_return'].iloc[-1]
#年化收益,把整个期间的收益则算成一年的收益
annual_return=(1+total_return)**(252/len(df))-1
#计算年波动率
annual_volatility=df['strategy_return_net'].std()*np.sqrt(252)
#夏普比率
sharpe_ratio=annual_return/annual_volatility if annual_volatility !=0 else 0
trade_count = int(df["trade_flag"].sum())
# 总交易次数，买入和卖出都算一次

print(f"股票：{target_code} {target_name}")
print(f"策略总收益：{total_return:.2%}")
print(f"策略年化收益：{annual_return:.2%}")
print(f"最大回撤：{max_drawdown:.2%}")
print(f"夏普比率：{sharpe_ratio:.2f}")
print(f"交易次数：{trade_count}")
# 打印回测结果