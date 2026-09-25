import code

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
pd.set_option('expand_frame_repr', False)

#1 连接数据库
engine = create_engine('sqlite:////Users/yuhanwen/Desktop/量化交易/yfinance crash course/量化入门/1.Python股票量化投资系统课程/第四课 构建自己的股票数据库/stock.db')
#读取三只股票
codes_df=pd.read_sql(
    """
    select * from stock_500_daily_cumulative
    group by 股票代码
    order by 股票代码
    
    limit 3
    """
    , con=engine)
target_codes=codes_df['股票代码'].astype(str).tolist()
if len(target_codes)==0:
    raise ValueError('没有提取到股票')
print('本次回测的股票代码')
print(target_codes)

#风险与仓位参数
initial_capital=100000
#每只股票最多承受帐户资金的百分之一风险
risk_rate_per_stock=0.01
#止损比例
stop_lose_rate=0.08
#止盈比例
take_profit_rate=0.15
#单边手续费率
fee_rate=0.0005
#单只股票最高仓位
max_weight_per_stock=0.2
#所有股票最高总仓位
max_total_weight=0.6
#根据风险计算理论仓位
weight_by_risk=(
    risk_rate_per_stock/stop_lose_rate
)
#同时满足三个限制
weight_each=min(
    weight_by_risk,
    max_weight_per_stock,
)
weights={
    code:weight_each
    for code in target_codes
}
stock_weight=sum(weights.values())
cash_weight=1-stock_weight
print(f"每只股票仓位：{weight_each:.2%}")
print(f"股票总仓位：{stock_weight:.2%}")
print(f"现金仓位：{cash_weight:.2%}")
# 分别计算每只股票的策略收益
stock_returns={}
trade_counts={}
stop_counts={}
take_profit_counts={}

for code in target_codes:
    stock_df=pd.read_sql(
        f"""
        select * from stock_500_daily_cumulative
        where 股票代码={code}
        order by 交易日期
        """,con=engine
    )
    if stock_df.empty:
        raise ValueError(f'没有找到股票{code}的数据')
    #日期转换
    stock_df['交易日期']=pd.to_datetime(stock_df['交易日期'])
    #数值转换
    for column in ['收盘价','涨跌幅','MA5','MA20']:
        stock_df[column]=pd.to_numeric(stock_df[column],errors='coerce')
    #删除缺失值
    stock_df=stock_df.dropna(subset=['收盘价','涨跌幅','MA5','MA20']).reset_index(drop=True)
    #生成均线策略
    #ma5>ma20
    stock_df['ma_position']=(stock_df['MA5']>stock_df['MA20']).astype(int)
    #前一天的均线状态
    stock_df['ma_position_yesterday']=stock_df['ma_position'].shift(1).fillna(0)
    #增加买入信号
    stock_df['buy_signal']=((stock_df['ma_position']==1) & (stock_df['ma_position_yesterday']==0)).astype(int)
    # MA5 从上方跌到下方，产生卖出信号
    stock_df["sell_signal"] = (
            (stock_df["ma_position"] == 0)
            & (stock_df["ma_position_yesterday"] == 1)
    ).astype(int)
    #加入止盈和止损
    stock_df['position']=0

    entry_price = None
    for i in range(len(stock_df)):
        close_price = stock_df.at[i, '收盘价']
        if entry_price is None:
            if stock_df.at[i, "buy_signal"] == 1:
                stock_df.at[i, "position"] = 1
                entry_price = close_price
        else:
            hit_stop_price = (close_price <= entry_price * (1 -stop_lose_rate))
            hit_take_profit = (
                    close_price
                    >= entry_price * (1 + take_profit_rate)
            )
            ma_sell = stock_df.at[i, 'sell_signal'] == 1
            if hit_stop_price and hit_take_profit and ma_sell:
                stock_df.at[i, 'position'] = 0
                entry_price = 1
            else:
                stock_df.at[i, 'position'] = 0
    stock_df["position_yesterday"] = (
        stock_df["position"].shift(1).fillna(0)
    )

    stock_df["trade_flag"] = (
        stock_df["position"].diff().abs().fillna(stock_df["position"])
    )
    # 计算这只股票的策略每日收益率
    stock_df['strategy_return'] = stock_df['涨跌幅'] * stock_df['position_yesterday'] - stock_df[
        'trade_flag'] * fee_rate
    # 只保留组合需要的两列
    one_stock_return = stock_df[['交易日期', 'strategy_return']].rename(columns={
        'strategy_return': f"{code}_strategy_return"
    })
    # 保存这只股票的每日策略收益
    stock_returns[code] = one_stock_return
# 合并这几个股票
portfolio_df = None
for code in target_codes:
    if portfolio_df is None:
        portfolio_df = stock_returns[code]
    else:
        portfolio_df = portfolio_df.merge(
            stock_returns[code],
            on='交易日期',
            how='inner'
        )
portfolio_df = portfolio_df.sort_values('交易日期').reset_index(drop=True)
# 计算组合每日收益率
portfolio_df['组合收益率'] = 0.0
for code in target_codes:
    return_column = f'{code}_strategy_return'
    portfolio_df['组合收益率'] += portfolio_df[return_column] * weights[code]
# 计算组合累计收益率和净值
portfolio_df['组合累计收益率'] = (1 + portfolio_df['组合收益率']).cumprod() - 1
# 设初始净值设为1
portfolio_df['组合净值'] = (1 + portfolio_df['组合累计收益率'])
# 计算组合回测指标
total_return = (portfolio_df['组合累计收益率'].iloc[-1])
annual_return = (1 + total_return) ** (252 / len(portfolio_df)) - 1
annual_volatility = portfolio_df['组合收益率'].std() * np.sqrt(252)
sharpe_ratio = annual_return / annual_volatility if annual_volatility != 0 else 0
# 净值
running_max = portfolio_df['组合净值'].cummax()
drawdown = portfolio_df['组合净值'] / running_max - 1
max_drawdown = drawdown.min()
# =========================
# 9. 打印回测结果