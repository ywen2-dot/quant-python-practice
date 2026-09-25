import pandas as pd
from sqlalchemy import create_engine
import numpy as np
pd.set_option('expand_frame_repr', False)
import matplotlib.pyplot as plt
#连接数据库
engine=create_engine('sqlite:////Users/yuhanwen/Desktop/量化交易/yfinance crash course/量化入门/1.Python股票量化投资系统课程/第四课 构建自己的股票数据库/stock.db')
#读取股票数据,选取3只股票
df=pd.read_sql(
    """
    select 股票代码 from stock_500_daily_cumulative
    group by 股票代码
    order by 股票代码
    limit 3
    """
    ,engine
)
target_code=df['股票代码'].astype(str).tolist()
print('本次回测股票')
print(target_code)
#3.仓位
#风险与仓位参数
initial_capital=100000
risk_rate_per_trade=0.01    #单只股票最多承受帐户1%风险
stop_loss_rate=0.08 #止损8%
take_profit_rate=0.15#止盈
fee_rate=0.0005  #单边手续费

max_weight_per_shock=0.20  #单只股票最高只能占20%
max_total_weight=0.6   #股票总仓位最高60%
#理论仓位
weight_by_risk=risk_rate_per_trade/stop_loss_rate
weight_each=min(
    weight_by_risk,
    max_weight_per_shock,

)
weights={code:weight_each for code in target_code}
stock_weight=sum(weights.values())
#分别计算每只股票的策略收益
stock_returns={}
trade_counrs={}
for code in target_code:
    stock_df=pd.read_sql(
    f"""
    select * from stock_500_daily_cumulative
    where 股票代码='{code}'
    order by 交易日期
    """
        ,engine
    )
    if stock_df.empty:
        raise ValueError(f'没有找到股票{code}的数据')
    #吧交易日期转换成日期格式
    stock_df['交易日期']=pd.to_datetime(stock_df['交易日期'])
    #MA5，MA20m没有数据的不能参与
    stock_df=stock_df.dropna(subset=['涨跌幅','MA5','MA20']).reset_index(drop=True)
    # MA5 上穿 MA20 后买入；下穿后卖出
    stock_df["ma_position"] = (
            stock_df["MA5"] > stock_df["MA20"]
    ).astype(int)

    stock_df["ma_position_yesterday"] = (
        stock_df["ma_position"].shift(1).fillna(0)
    )

    stock_df["buy_signal"] = (
            (stock_df["ma_position"] == 1)
            & (stock_df["ma_position_yesterday"] == 0)
    ).astype(int)

    stock_df["sell_signal"] = (
            (stock_df["ma_position"] == 0)
            & (stock_df["ma_position_yesterday"] == 1)
    ).astype(int)
    #加入止损，止盈后的实际仓位
    stock_df['position']=0
    entry_price=None
    for i in range(len(stock_df)):
        close_price=stock_df.at[i,'收盘价']
        if entry_price is None:
            if stock_df.at[i, "buy_signal"] == 1:
                stock_df.at[i, "position"] = 1
                entry_price = close_price
        else:
            hit_stop_price=(close_price<=entry_price*(1-stop_loss_rate))
            hit_take_profit = (
                    close_price
                    >= entry_price * (1 + take_profit_rate)
            )
            ma_sell=stock_df.at[i,'sell_signal']==1
            if hit_stop_price and hit_take_profit and ma_sell:
                stock_df.at[i,'position'] = 0
                entry_price = 1
            else:
                stock_df.at[i,'position'] = 0
    stock_df["position_yesterday"] = (
        stock_df["position"].shift(1).fillna(0)
    )

    stock_df["trade_flag"] = (
        stock_df["position"].diff().abs().fillna(stock_df["position"])
    )
    #计算这只股票的策略每日收益率
    stock_df['strategy_return']=stock_df['涨跌幅']*stock_df['position_yesterday']-stock_df['trade_flag']*fee_rate
    #只保留组合需要的两列
    one_stock_return=stock_df[['交易日期','strategy_return']].rename(columns={
        'strategy_return':f"{code}_strategy_return"
    })
    #保存这只股票的每日策略收益
    stock_returns[code]=one_stock_return
#合并这几个股票
portfolio_df=None
for code in target_code:
    if portfolio_df is None:
        portfolio_df=stock_returns[code]
    else:
        portfolio_df=portfolio_df.merge(
            stock_returns[code],
            on='交易日期',
            how='inner'
        )
portfolio_df=portfolio_df.sort_values('交易日期').reset_index(drop=True)
#计算组合每日收益率
portfolio_df['组合收益率']=0.0
for code in target_code:
    return_column=f'{code}_strategy_return'
    portfolio_df['组合收益率']+=portfolio_df[return_column]*weights[code]
#计算组合累计收益率和净值
portfolio_df['组合累计收益率']=(1+portfolio_df['组合收益率']).cumprod()-1
#设初始净值设为1
portfolio_df['组合净值']=(1+portfolio_df['组合累计收益率'])
#计算组合回测指标
total_return=(portfolio_df['组合累计收益率'].iloc[-1])
annual_return=(1+total_return)**(252/len(portfolio_df))-1
annual_volatility=portfolio_df['组合收益率'].std()*np.sqrt(252)
sharpe_ratio=annual_return/annual_volatility if annual_volatility !=0 else 0
#净值
running_max=portfolio_df['组合净值'].cummax()
drawdown=portfolio_df['组合净值']/running_max-1
max_drawdown=drawdown.min()
# =========================
# 9. 打印回测结果
# =========================

print("\n组合回测结果")
print(f"回测交易日：{len(portfolio_df)}")
print(f"组合总收益：{total_return:.2%}")
print(f"组合年化收益：{annual_return:.2%}")
print(f"组合年化波动率：{annual_volatility:.2%}")
print(f"组合夏普比率：{sharpe_ratio:.2f}")
print(f"组合最大回撤：{max_drawdown:.2%}")


# =========================
# 10. 查看部分数据
# =========================

print("\n组合数据前 5 行：")
print(portfolio_df.head())

print("\n组合数据最后 5 行：")
print(portfolio_df.tail())

# =========================
# 11. 绘制组合净值曲线
# =========================

plt.figure(figsize=(12, 6))

plt.plot(
    portfolio_df["交易日期"],
    portfolio_df["组合净值"],
    label="portfolio_net_value"
)

plt.title("Multi-stock Portfolio Backtest")
plt.xlabel("trade_date")
plt.ylabel("portfolio_net_value")
plt.legend()
plt.grid(True)

plt.show()