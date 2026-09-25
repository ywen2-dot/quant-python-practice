import pandas as pd
from requests.packages import target
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import numpy as np

pd.set_option('expand_frame_repr', False)
#连接数据库
engine=create_engine('sqlite:////Users/yuhanwen/Desktop/量化交易/yfinance crash course/量化入门/1.Python股票量化投资系统课程/第四课 构建自己的股票数据库/stock.db')
#读取数据
selected=pd.read_sql('select * from stock_500_stock_selected',engine)
target_code=selected.loc[0,'股票代码']
target_name=selected.loc[0,'股票名称']
#选出这只股票
df=pd.read_sql(
    f"""
    select * from stock_500_daily_cumulative
        where 股票代码='{target_code}'
        order by 交易日期
    """

,engine)
#处理交易日期
df['交易日期']=pd.to_datetime(df['交易日期'])
#处理空缺值
df=df.dropna(subset=['MA5','MA20']).reset_index(drop=True)
#增加position列,并且判断是否持仓
df['position']=0
df.loc[df['MA5']>df['MA20'],'position']=1
#计算昨天的仓位
df['position_yesterday']=df['position'].shift(1).fillna(0)
#定义买跟卖的信号
df['buy_signal']=((df['position']==1) &( df['position_yesterday']==0)).astype(int)
df['sell_signal']=((df['position']==0) & (df['position_yesterday']==1)).astype(int)
print(df.head())
#计算策略收益
df['market_return']=df['涨跌幅']
df['strategy_return']=df['market_return']*df['position_yesterday']
#计算两者的累积收益
df['market_cum_return']=(1+df['market_return']).cumprod()-1
df['strategy_cum_return']=(1+df['strategy_return']).cumprod()-1
print(df.head())
#画两个线图
plt.figure(figsize=(12,8))
df['trade_date']=df['交易日期']
plt.plot(df['trade_date'],df['market_cum_return'],label='buy_and_hold')
plt.plot(df['trade_date'],df['strategy_cum_return'],label='mean_strategy')
plt.legend(loc='best')
plt.grid(True)
plt.show()
#判断今天是否交易
df['trade_flag']=df['position'].diff().abs().fillna(0)
#设置手续费
fee_rate=0.00005
#计算交易手续费
df['transaction_fee']=df['trade_flag']*fee_rate
#扣除手续费后的策略收益
df['strategy_return_net']=df['strategy_return']-df['transaction_fee']
#策略扣除手续费后的累计收益
df['strategy_cum_return_net']=(1+df['strategy_return_net']).cumprod()-1
#将累计收益变成净值
net_value=1+df['strategy_cum_return_net']
#记录历史最高净值
df['running_max']=net_value.cummax()
#计算回撤
df['drawdown']=net_value/df['running_max']-1
#计算最大回撤
max_drawdown=df['drawdown'].min()
#策略最后一天的收益
total_return_strategy=df['strategy_cum_return_net'].iloc[-1]
#计算年化收益率
annual_return=(1+total_return_strategy)**(252/len(df))-1
#计算年化波动率
annual_volatility=df['strategy_return_net'].std()* np.sqrt(252)
#夏普比率
sharpe_ratio=annual_volatility/annual_volatility if annual_volatility!=0 else 0
trade_count=df['trade_date'].count()
print(f"股票：{target_code} {target_name}")
print(f"策略总收益：{total_return_strategy:.2%}")
print(f"策略年化收益：{annual_return:.2%}")
print(f"最大回撤：{max_drawdown:.2%}")
print(f"夏普比率：{sharpe_ratio:.2f}")
print(f"交易次数：{trade_count}")
# 打印回测结果