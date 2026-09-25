import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import mplfinance as mpf
from fontTools.subset import subset
from pyspark.sql.connect.functions import column
from sqlalchemy import create_engine
from matplotlib.lines import Line2D
pd.set_option('expand_frame_repr', False)
#设置参数
target_stock='sh600000' #回测的代码
initial_capital=100000
stop_loss_rate=0.08
take_profit_rate=0.15
fee_rate=0.0005
show_days=180
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
#4 清洗数据
#把交易日期转换成日期类型
df['date']=pd.to_datetime(df['date'])
#需要转换成数值型的列
numeric_columns=[
    'open',
    'low',
    'high',
    'close',
    'volume',
    'pre_close',
    'deal_volume',
    'volume',
]
print(type(df))
#把价格和成交量转换成数值
for columns in numeric_columns:
    df[columns]=pd.to_numeric(df[columns], errors='coerce')
#删除日期，价格成交量缺失的数据
df=df.dropna(subset=['date',*numeric_columns]).drop_duplicates(subset='date',keep='first')
#从早到晚排序
df=df.sort_values('date')
df=df.reset_index(drop=True)
#5 计算均线
df['MA5']=df['close'].rolling(5).mean()
#计算20日均线
df['MA20']=df['close'].rolling(20).mean()
#删除还没形成的空缺行
df=df.dropna(subset=['MA5','MA20']).reset_index(drop=True)
#6形成金叉和死叉
#MA5高于MA20时为TRUE
df['ma_above']=(df['MA5']>df['MA20']).astype(int)
df['ma_above_yesterday']=df['ma_above'].shift(1).fillna(0)
df['buy_signal']=((df['ma_above']==1) & (df['ma_above_yesterday']==0)).astype(int)
df['sell_signal']=((df['ma_above']==0) & (df['ma_above_yesterday']==1)).astype(int)
#创建交易记录列
df['position']=0
df['trade_action']=""
df['exit_reason']=""
df['entry_reason']=""
print(df.head())
#执行买卖策略
#程序开始前没有持仓
position=0
#程序开始时没有买入价格
entry_price=None
#按日期开始逐步检查
for i in range(len(df)):
    close_price=df.at[i,'close']
    if position==0:
        if df.at[i,'buy_signal']==1:
            position=1
            entry_price=close_price
            df.at[i,'trade_action']='buy'
            df.at[i,'entry_price']=entry_price
    else:
        return_since_entry=close_price/entry_price-1
        hit_stop_loss=return_since_entry<=-stop_loss_rate
        hit_take_profit=return_since_entry>=take_profit_rate
        hit_ma_sell=bool(df.at[i,'sell_signal'])
        if (hit_stop_loss or hit_take_profit or hit_ma_sell):
            position=0
            df.at[i,'trade_action']='sell'
            #判断卖出原因
            if hit_stop_loss:
                df.at[i,'exit_reason']='stop_loss'
            elif hit_take_profit:
                df.at[i,'exit_reason']='take_profit'
            else:
                df.at[i,'exit_reason']='ma_sell'
            entry_price=None
    df.at[i,'position']=position

#9计算策略收益
#计算股票每天的涨跌幅
df['stock_return']=df['close'].pct_change().fillna(0)
#今天的收益由昨天是否持仓决定
df['position_yesterday']=df['position'].shift(1).fillna(0)
#仓位变化时说明有交易
df['trade_count']=(df['position'].diff().abs().fillna(df['position']))
#计算策略纯收益
df['strategy_return']=df['stock_return']*df['position_yesterday']-df['trade_count']*fee_rate
#收益总利润
df['equity']=(1+df['strategy_return']).cumprod()
#帐户资金
df['capital']=(initial_capital*df['equity'])
##计算回测
#计算出现过的最大净值
df['running_max']=df['equity'].cummax()
#计算回测
df['drawdown']=df['equity']/df['running_max']-1
#计算最大回测
max_drawdown=df['drawdown'].min()
###计算回测指标
total_return=df['equity'].iloc[-1]-1
#年化收益率
annual_return=df['equity'].iloc[-1]**(252/len(df))-1
#年化波动率
annual_volatility=df['strategy_return'].std()*np.sqrt(252)
#计算夏普比率
sharpe_ratio= df["strategy_return"].mean() * 252/annual_volatility if annual_volatility!=0 else 0
#统计买入次数
buy_count=(df['trade_action']=='buy').sum()
# 统计卖出次数
sell_count = (
    df["trade_action"] == "sell"
).sum()


# ==================== 12. 输出回测结果 ====================

print(f"\n股票：{target_stock}")
print(f"股票名称：{df['name'].iloc[0]}")
print(f"回测交易日：{len(df)}")
print(f"买入次数：{buy_count}")
print(f"卖出次数：{sell_count}")
print(f"最终资金：{df['capital'].iloc[-1]:,.2f}元")
print(f"总收益率：{total_return:.2%}")
print(f"年化收益率：{annual_return:.2%}")
print(f"年化波动率：{annual_volatility:.2%}")
print(f"夏普比率：{sharpe_ratio:.2f}")
print(f"最大回撤：{max_drawdown:.2%}")
#13 准备K线数据
##只显示最后189个交易日
plot_df=df.tail(show_days).copy()
plot_df=plot_df.set_index('date')
#改成mplfinance要求的列名
plot_df=plot_df.rename(columns={
    'open':'Open',
    'high':'High',
    'low':'Low',
    'close':'Close',
    'volume':'Volume',
    'pre_close':'Pre-Close',
    'deal_volume':'Deal Volume',
})
#生产买卖标记
#买入点
plot_df['buy_marker']=np.where(
    plot_df['trade_action']=='buy',
    plot_df['Low']*0.98,
    np.nan
)
#均线卖出点
plot_df['sell_marker']=np.where(
    plot_df['trade_action']=='sell',
    plot_df['High']*1.02,
    np.nan
)
# 均线卖出点放在最高价上方
plot_df["ma_sell_marker"] = np.where(
    plot_df["exit_reason"] == "ma_sell",
    plot_df["High"] * 1.02,
    np.nan,
)

# 止损点放在最低价下方
plot_df["stop_loss_marker"] = np.where(
    plot_df["exit_reason"] == "stop_loss",
    plot_df["Low"] * 0.97,
    np.nan,
)

# 止盈点放在最高价上方
plot_df["take_profit_marker"] = np.where(
    plot_df["exit_reason"] == "take_profit",
    plot_df["High"] * 1.03,
    np.nan,
)
#15添加均线
#创建附加图形列表
additional_plots=[
    mpf.make_addplot(
        plot_df['MA5'],
        color='orange',
        width=1,
    ),
    mpf.make_addplot(
        plot_df['MA20'],
        color='red',
        width=1,
    )
]
#16添加买入标记
#最后180天存在买点时才绘制
if plot_df['buy_marker'].notna().any():
    additional_plots.append(mpf.make_addplot(
        plot_df['buy_marker'],
        type='scatter',
        color='green',
        markersize=90,
        marker='^',
        width=1,
    ))
#17添加均线卖出标记
if plot_df['ma_sell_marker'].notna().any():
    additional_plots.append(mpf.make_addplot(
        plot_df['ma_sell_marker'],
        type='scatter',
        color='black',
        markersize=90,
        marker='v',
        width=1,
    ))
#18添加止损标志
if plot_df["stop_loss_marker"].notna().any():

    additional_plots.append(
        mpf.make_addplot(
            plot_df["stop_loss_marker"],
            type="scatter",
            marker="x",
            markersize=90,
            color="red",
        )
    )
#19添加止盈标记
if plot_df["take_profit_marker"].notna().any():

    additional_plots.append(
        mpf.make_addplot(
            plot_df["take_profit_marker"],
            type="scatter",
            marker="*",
            markersize=120,
            color="purple",
        )
    )
#20设置K线颜色
#A股上涨用红色，下跌用绿色
market_colors=mpf.make_marketcolors(
    up='blue',
    down='red',
    inherit=True, #让影线，边框等部分继承相应的涨跌颜色
)
#设置图标样式
chart_style = mpf.make_mpf_style(
    marketcolors=market_colors,
    gridstyle="--",
)
#21绘制K线图
#绘制K线，成交量，均线和交易点
kline_figure,kline_axes=mpf.plot(
    plot_df,
    type='candle',
    volume=True,
    addplot=additional_plots,
    style=chart_style,
    title=f"{target_stock} MA Strategy",
    ylabel="Price",
    ylabel_lower="Volume",
    figsize=(14, 8),
    returnfig=True,
)

#22添加图例
# 手动创建图例内容
legend_items = [
    Line2D(
        [0],
        [0],
        color="orange",
        label="MA5",
    ),
    Line2D(
        [0],
        [0],
        color="blue",
        label="MA20",
    ),
    Line2D(
        [0],
        [0],
        marker="^",
        color="green",
        linestyle="None",
        label="Buy",
    ),
    Line2D(
        [0],
        [0],
        marker="v",
        color="black",
        linestyle="None",
        label="MA Sell",
    ),
    Line2D(
        [0],
        [0],
        marker="x",
        color="red",
        linestyle="None",
        label="Stop Loss",
    ),
    Line2D(
        [0],
        [0],
        marker="*",
        color="purple",
        linestyle="None",
        label="Take Profit",
    ),
]

# 把图例放在K线主图中
kline_axes[0].legend(
    handles=legend_items,
    loc="upper left",
)

# ==================== 23. 绘制资金和回撤 ====================

# 创建上下两张子图
performance_figure, axes = plt.subplots(
    2,
    1,
    figsize=(14, 8),
    sharex=True,
)

# 绘制资金曲线
axes[0].plot(
    df["date"],
    df["capital"],
    color="navy",
    linewidth=1.5,
)

# 设置资金曲线标题
axes[0].set_title("Strategy Capital Curve")

# 设置纵轴名称
axes[0].set_ylabel("Capital")

# 显示网格
axes[0].grid(alpha=0.3)

# 绘制回撤区域
axes[1].fill_between(
    df["date"],
    df["drawdown"],
    0,
    color="red",
    alpha=0.35,
)

# 设置回撤图标题
axes[1].set_title("Strategy Drawdown")

# 设置纵轴名称
axes[1].set_ylabel("Drawdown")

# 设置横轴名称
axes[1].set_xlabel("Date")

# 显示网格
axes[1].grid(alpha=0.3)

# 自动调整图表间距
performance_figure.tight_layout()

# 显示K线图、资金曲线和回撤曲线
plt.show()
