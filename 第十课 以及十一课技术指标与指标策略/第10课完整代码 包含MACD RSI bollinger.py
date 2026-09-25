from pickle import HIGHEST_PROTOCOL
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import mplfinance as mpf
from pygments.lexer import inherit
from sqlalchemy import create_engine,text
pd.set_option('expand_frame_repr', False)
#设置参数
target_stock='sh600000' #回测的代码
initial_capital=100000
stop_loss_rate=0.08
take_profit_rate=0.15
fee_rate=0.0005
show_days=720
zigzag_rate=0.09
strategy_name='combination'
setup_valid_days=10#金叉后最多等待多少个交易日出现布林带突破
#读取获取数据
#连接
engine=create_engine('sqlite:////Users/yuhanwen/Desktop/量化交易/yfinance crash course/量化入门/1.Python股票量化投资系统课程/第四课 构建自己的股票数据库/stock.db')
#查询数据
df=pd.read_sql(f"""
        select * from stock_500_daily 
        where 股票代码='{target_stock}'
        """,engine)

#如果没有这只股票就停止程序
if df.empty:
    raise ValueError('没有找到这只股票')
#查看读取结果
df=df.rename(columns={
    '股票代码':'code',
    '股票名称':'name',
    '交易日期':'date',
    '开盘价':'open',
    '最高价':'high',
    '最低价':'low',
    '收盘价':'close',
    '成交量':'volume',
    '前收盘价':'pre_close',
    '成交额':'deal_volume'
})
print(df.head())
# ==================== 3. 清洗数据 ====================

df["date"] = pd.to_datetime(df["date"])

numeric_columns = [
    "open",
    "high",
    "low",
    "close",
    "volume",
]

df[numeric_columns] = df[numeric_columns].apply(
    pd.to_numeric,
    errors="coerce",
)

df = df.dropna(
    subset=["date", *numeric_columns]
)

df = df.drop_duplicates(
    subset="date",
    keep="last",
)

df = df.sort_values("date")
df = df.reset_index(drop=True)
##计算趋势均线
#MA5:最近5,20天收盘价平均值
df['MA5']=df['close'].rolling(5).mean()
df['MA20']=df['close'].rolling(20).mean()
#=================
#4计算MACD
#=================
#计算12日指数移动平均线
df['EMA12']=df['close'].ewm(span=12,adjust=False).mean()
#计算26日的EMA
df['EMA26']=df['close'].ewm(span=26,adjust=False).mean()
#计算DIF
df['DIF']=df['EMA12']-df['EMA26']
#计算DEA 他是DIF的9日指数移动平均线
df['DEA']=df['DIF'].ewm(span=9,adjust=False).mean()
#计算MACD柱
df['MACD']=2*(df['DIF']-df['DEA'])
#=============
#计算布林带
#==============
#得到中轨
df['BB_middle']=df['MA20']
#标准差：衡量价格有多分散
df['BB_std']=df['close'].rolling(20).std()
#计算上轨和下轨
df['BB_upper']=df['BB_middle']+0.5*df['BB_std']
df['BB_lower']=df['BB_middle']-0.5*df['BB_std']
#删除数据不足的行
df = df.dropna(
    subset=["BB_middle", "BB_upper", "BB_lower"]
).reset_index(drop=True)
#==================
#MACD金叉和死叉信号
#==================
df['macd_above']=df['DIF']>df['DEA']
df['macd_strong']=df['macd_above']
df['macd_low_strong']=(df['macd_strong']&(df['DIF']<0))
#取出上一个交易日的状态
df['macd_above_yesterday']=(df['macd_above'].shift(1,fill_value=False))
#判断金叉
df['macd_buy_signal']=(df['macd_above']==True)&(df['macd_above_yesterday']==False)
df['macd_sell_signal']=(df['macd_above']==False)&(df['macd_above_yesterday']==True)
df["macd_buy_recent"] = (
    df["macd_buy_signal"]
    .rolling(10, min_periods=1)
    .max()
    .astype(bool)
)

#==============
#生成布林带信号
#===============
df['close_yesterday']=(df['close'].shift(1))
df['BB_lower_yesterday']=(df['BB_lower'].shift(1))
df['BB_upper_yesterday']=(df['BB_upper'].shift(1))
#昨天未突破上轨，今天收盘突破上轨
df['bb_buy_signal']=df['close']>df['BB_upper']
#昨天未突破下轨，今天收盘突破下轨
# 收盘价跌破布林带下轨，就卖出
df["bb_sell_signal"] = (
    df["close"] < df["BB_lower"]
)
#创建ZIGZAG记录列
#保留已经确认的波段高点或低点
df['zigzag_pivot']=np.nan
df['zigzag_pivot_type']=""
df['zigzag_sell_signal']=False
df['zigzag_buy_signal']=False
#===============
#计算Zigzag
#===============
#direction的含义，0处于初始阶段，1处于上升波段，在寻咋搞掂 ，-1处于波段下降，正在寻找最低点
direction=0
#记录观察到的最高价格以及位置
highest_price=df.at[0,'close']
highest_index=0
#记录观察到的最低价格以及位置
lowest_price=df.at[0,'close']
lowest_index=0
#开始逐日检查
for i in range(1,len(df)):
    close_price=df.at[i,'close']
    #尚未确认最初方向
    if direction==0:
        if close_price>highest_price:#出现更高的价格，更新后选高点
            highest_price=close_price
            highest_index=i
        if  close_price<lowest_price:#出现更低的价格，更新后选低点
            lowest_price=close_price
            lowest_index=i
        #从候选低点上涨5%，确认此前的低点
        rise_from_low=close_price/lowest_price-1
        #从候选高点下跌，确认此前的高点
        fall_from_high=close_price/highest_price-1
        if rise_from_low>=zigzag_rate:
            df.at[lowest_index,'zigzag_pivot']=lowest_price
            df.at[lowest_index,'zigzag_pivot_type']='low'
            df.at[i,'zigzag_buy_signal']=True
            #上升波段寻找最高点
            direction=1
            highest_price=close_price
            highest_index=i
        elif fall_from_high<=-zigzag_rate:
            df.at[highest_index,'zigzag_pivot']=highest_price
            df.at[highest_index,'zigzag_pivot_type']='high'
            #高点在今天 得到确认
            df.at[i,'zigzag_sell_signal']=True
            #接下来进入下降波段，开始寻找低点
            direction=-1
            lowest_price=close_price
            lowest_index=i
    elif direction == 1:
        if close_price > highest_price:
            highest_price = close_price
            highest_index = i
        #计算价格相对候选高点的跌幅
        fall_from_high = close_price/highest_price-1
        #从最高点回落5%，确认此前的波段高点
        if fall_from_high<=-zigzag_rate:
            df.at[highest_index,'zigzag_pivot']=highest_price
            df.at[highest_index,'zigzag_pivot_type']='high'
            df.at[i,'zigzag_sell_signal']=True
            #转入下降波段
            direction = -1
            lowest_price = close_price
            lowest_index = i
            # 当前处于下降波段
    elif direction == -1:

        # 继续下跌时更新候选低点
        if close_price < lowest_price:
            lowest_price = close_price
            lowest_index = i
        rise_from_low = close_price/lowest_price-1
        #从最低点上涨5%，确认此前的波段低点
        if rise_from_low>=zigzag_rate:

            df.at[
                lowest_index,
                "zigzag_pivot",
            ] = lowest_price

            df.at[
                lowest_index,
                "zigzag_pivot_type",
            ] = "low"

            # 买入信号放在确认日
            df.at[
                i,
                "zigzag_buy_signal",
            ] = True

            # 转入上升波段
            direction = 1

            highest_price = close_price
            highest_index = i
#===========生成zigzag显示线============
#复制已经确认的zigzag转折点
df['zigzag_line']=df['zigzag_pivot'].copy()
#在相邻转折点之间进行线性插值
df['zigzag_line']=df['zigzag_line'].interpolate(
    method='linear',
    limit_area='inside',
)
#==========生成多指标组合信号=======
#最近setup_valid_days天内是否出现过zigzag低点
df['zigzag_low_recent']=df['zigzag_buy_signal'].rolling(setup_valid_days,min_periods=1).max().astype(bool)
#形成准备完成信号
df['long_setup_signal']=df['zigzag_low_recent']&df['macd_low_strong']
#准备信号在未来仍然有效
df["long_setup_recent"] = (
    df["long_setup_signal"]
    .rolling(setup_valid_days, min_periods=1)
    .max()
    .astype(bool)
)
#真正的买入条件
df['combination_buy_signal']=df['long_setup_recent']&df['macd_buy_recent']&df['bb_buy_signal']
#卖出条件
df["combination_sell_signal"] = (df["bb_sell_signal"])
#===========选择回测指标======
df['buy_signal']=False
df['sell_signal']=False
if strategy_name == "macd":
    df["buy_signal"] = df["macd_buy_signal"]
    df["sell_signal"] = df["macd_sell_signal"]
elif strategy_name == "bollinger":
    df["buy_signal"] = df["bb_buy_signal"]
    df["sell_signal"] = df["bb_sell_signal"]
elif strategy_name == "zigzag":
    df["buy_signal"] = df["zigzag_buy_signal"]
    df["sell_signal"] = df["zigzag_sell_signal"]
elif strategy_name == "combination":
    df["buy_signal"] = df["combination_buy_signal"]
    df["sell_signal"] = df["combination_sell_signal"]
else:
    raise ValueError('strategy name error')
#今天收盘看到信号，不能假设今天已经买入
#昨天产生的买入,卖出信号，推迟到今天开盘执行
df['buy_signal_candidate_for_today'] = (
    df['buy_signal'].shift(1, fill_value=False).astype(bool)
)
df['sell_signal_candidate_for_today'] = (df['sell_signal'].shift(1, fill_value=False).astype(bool))
#今天开盘必须高于昨天收盘，才允许买入，开盘必须创新低才卖出
df['previous_close'] = df['close'].shift(1)
df['open_above_prev_close'] = (
    df['open'] > df['previous_close']
).fillna(False)
df['open_below_prev_close'] = (df['open']<df['previous_close'])
df['buy_signal_for_today'] = (
    df['buy_signal_candidate_for_today']
    & df['open_above_prev_close']
)
#昨天产生的卖出信号，推迟到今天开盘执行
df['sell_signal_for_today'] =(df['sell_signal_candidate_for_today']&df['open_below_prev_close']
    )
# 只查看真正可能执行交易的日期
signal_check = df.loc[
    df["buy_signal_candidate_for_today"]
    | df["sell_signal_for_today"],
    [
        "date",
        "previous_close",
        "open",
        "open_above_prev_close",
        "buy_signal",
        "buy_signal_candidate_for_today",
        "buy_signal_for_today",
        "sell_signal",
        "sell_signal_for_today",
    ],
]

print("\n信号日与成交日检查：")
print(signal_check.to_string(index=False))
#==========执行交易策略==========
df['position']=0
df['trade_action']=""
position=0
for i in range(1,len(df)):
    if position==0 and df.at[i,'buy_signal_for_today']:
        position=1
        df.at[i,'trade_action']="buy"
    elif position==1 and df.at[i,'sell_signal_for_today']:
        position=0
        df.at[i,'trade_action']="sell"
    #每天保存收盘后的持仓
    df.at[i,'position']=position

#========计算策略收益=======
df['cash']=np.nan
df['shares']=np.nan
df['capital']=np.nan
cash=float(initial_capital)
shares=0
for i in range(1,len(df)):
    open_price=float(df.at[i,'open'])
    close_price=float(df.at[i,'close'])
    buy_today=bool(df.at[i,'buy_signal_for_today'])
    sell_today=bool(df.at[i,'sell_signal_for_today'])
    if cash>0 and shares==0 and buy_today:
        shares=cash/(open_price*(1+fee_rate))
        cash=0
        df.at[i,'trade_action']="buy"
        df.at[i,'trade_price']=open_price
    elif shares>0 and sell_today:
        cash=shares*open_price*(1-fee_rate)
        shares=0.0
        df.at[i,'trade_action']="sell"
        df.at[i,'trade_price']=open_price
    df.at[i,'position']=int(shares>0)
    df.at[i, "cash"] = cash
    df.at[i,'shares'] = shares
    df.at[i, "capital"] = cash + shares * close_price
df["equity"] = df["capital"] / initial_capital
df['strategy_return']=(df['capital'].pct_change().fillna(0))
#==========检查每笔真实交易==========

trade_log = df.loc[
    df["trade_action"] != "",
    [
        "date",
        "previous_close",
        "open",
        "close",
        "buy_signal_for_today",
        "sell_signal_for_today",
        "trade_action",
        "trade_price",
        "cash",
        "shares",
        "capital",
    ],
].copy()

print("\n每笔真实交易记录：")
print(trade_log.to_string(index=False))
#======计算绩效指标========
df['running_max']=df['equity'].cummax().clip(lower=1)
#计算回测
df['drawdown']=df['equity']/df['running_max']-1
#最大回测
max_drawdown=df['drawdown'].min()
#计算总收益
total_return=df['equity'].iloc[-1]-1
#买入并持有基准
buy_hold_return=df['close'].iloc[-1]/df['close'].iloc[0]-1
print(f"策略总收益率：{total_return:.2%}")
print(f"买入并持有收益率：{buy_hold_return:.2%}")
#年化收益
annual_return=df['equity'].iloc[-1]**(252/len(df))-1
#年化波动率
annual_volatility=df['strategy_return'].std()*np.sqrt(252)
#平均每天赚多少还有收益波动率
daily_mean=df['strategy_return'].mean()
daily_std=df['strategy_return'].std()
#夏普比率
sharpe_ratio=daily_mean/daily_std*np.sqrt(252) if daily_std>0 else np.nan
#统计买入次数
buy_count=(df['trade_action']=='buy').sum()
#统计卖出次数
sell_count=(df['trade_action']=='sell').sum()

# ==================== 18. 输出回测结果 ====================

print(f"\n股票：{target_stock}")
print(f"股票名称：{df['name'].iloc[0]}")
print(f"策略：{strategy_name}")
print(f"ZigZag幅度：{zigzag_rate:.0%}")
print(f"回测交易日：{len(df)}")
print(f"买入次数：{buy_count}")
print(f"卖出次数：{sell_count}")
print(f"最终资金：{df['capital'].iloc[-1]:,.2f}元")
print(f"总收益率：{total_return:.2%}")
print(f"年化收益率：{annual_return:.2%}")
print(f"年化波动率：{annual_volatility:.2%}")
print(f"夏普比率：{sharpe_ratio:.2f}")
print(f"最大回撤：{max_drawdown:.2%}")
#=======准备绘图数据=======
plot_df=df.tail(show_days).copy()
plot_df=plot_df.set_index('date')
plot_df=plot_df.rename(columns={
    "open": "Open",
    "high": "High",
    "low": "Low",
    "close": "Close",
    "volume": "Volume",
})
#实际买入标记
plot_df["buy_marker"] = np.where(
    plot_df["trade_action"] == "buy",
    plot_df["Low"] * 0.98,
    np.nan,
)
#实际卖出标记
plot_df['sell_marker']=np.where(
    plot_df['trade_action']=='sell',
    plot_df['High']*1.02,
    np.nan,
)
macd_colors=[
    'red' if value>=0 else 'green'
    for value in plot_df['MACD']
]
#==========添加指标图形===========
additional_plots=[
    #MA5
    mpf.make_addplot(
        plot_df['MA5'],
        color='orange',
        width=1,
    ),
    #MA20
    mpf.make_addplot(
        plot_df['MA20'],
        color='blue',
        width=1,
    ),
    #布林带上轨
    mpf.make_addplot(
        plot_df['BB_upper'],
        color='gray',
        width=0.8
    ),
    #布林带中轨
    mpf.make_addplot(
        plot_df['BB_middle'],
        color='yellow',
        width=1,
    ),
    #布林带下轨
    mpf.make_addplot(
        plot_df['BB_lower'],
        color='gray',
        width=0.8,
    ),
    # ZIGZAG线
    mpf.make_addplot(
        plot_df['zigzag_line'],
        color='red',
        width=1.8,
    ),
    # MACD的DIF
    mpf.make_addplot(
        plot_df["DIF"],
        panel=2,
        color="blue",
        width=1,
        ylabel="MACD",
    ),

    # MACD的DEA
    mpf.make_addplot(
        plot_df["DEA"],
        panel=2,
        color="orange",
        width=1,
    ),

    # MACD柱
    mpf.make_addplot(
        plot_df["MACD"],
        panel=2,
        type="bar",
        color=macd_colors,
        alpha=0.6,
    ),
]
# 存在买入点时才绘制
if plot_df["buy_marker"].notna().any():

    additional_plots.append(
        mpf.make_addplot(
            plot_df["buy_marker"],
            type="scatter",
            marker="^",
            markersize=90,
            color="green",
        )
    )

# 存在卖出点时才绘制
if plot_df["sell_marker"].notna().any():

    additional_plots.append(
        mpf.make_addplot(
            plot_df["sell_marker"],
            type="scatter",
            marker="v",
            markersize=90,
            color="black",
        )
    )

#==========绘制K线和指标==========
market_colors=mpf.make_marketcolors(
    up='green',
    down='red',
    inherit=True,
)
chart_style = mpf.make_mpf_style(
    marketcolors=market_colors,
    gridstyle="--",
)
#panel 0 :K线和Zigzag
#panel 1:成交量
#panel 2:MACD
mpf.plot(
    plot_df,
    type='candle',
    volume=True,
    addplot=additional_plots,
    style=chart_style,
    title=f"{target_stock} {strategy_name} strategy",
    ylabel="Price",
    ylabel_lower="Volume",
    panel_ratios=(4, 1, 1),
    figsize=(15, 10),
)
#=========绘制资金和回撤========
#创建一个滑步，里面有2行1列的图
figure, axes = plt.subplots(
    2,
    1,
    figsize=(15, 8),
    sharex=True,
)
#在第一张图上画线
axes[0].plot(
    df["date"],
    df["capital"],
    color="navy",
    linewidth=1.5,
)
#给第一张图加标签
axes[0].set_title(
    f"{strategy_name} Strategy Capital Curve"
)
#设置纵轴名
axes[0].set_ylabel("Capital")
axes[0].grid(alpha=0.3)
#第二张图
axes[1].fill_between(
    df["date"],
    df["drawdown"],
    0,
    color="red",
    alpha=0.35,
)
#加标题
axes[1].set_title(
    f"{strategy_name} Strategy Drawdown"
)
#设置第二张图的坐标轴
axes[1].set_ylabel("Drawdown")
axes[1].set_xlabel("Date")
axes[1].grid(alpha=0.3)
figure.tight_layout()

plt.show()
#验证当前的策略
buy_list=df.loc[df["trade_action"] == "buy",
    [
        "date",
        "close",
        "macd_buy_signal",
        "macd_buy_recent",
        "macd_strong",
        "zigzag_low_recent",
        "long_setup_recent",
        "bb_buy_signal",
        "combination_buy_signal",
    ],
]
