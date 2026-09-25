import pandas as pd
import mplfinance as mpf
from pygments.lexer import inherit
from sqlalchemy import create_engine
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
#4计算MACD
#计算12日指数移动平均线
df['EMA12']=df['close'].ewm(span=12,adjust=False).mean()
#计算26日的EMA
df['EMA26']=df['close'].ewm(span=26,adjust=False).mean()
#计算DIF
df['DIF']=df['EMA12']-df['EMA26']
#计算DEA 他是DIF的9日指数移动平均线
df['DEA']=df['DIF'].ewm(span=9,adjust=False).mean()
#计算MACD柱
df['MACD']=2*df['DIF']-df['DEA']
print(df[[
    'date',
    'close',
    'EMA12',
    'EMA26',
    'DIF',
    'DEA',
    'MACD',
]].tail(10))
#准备绘图数据
plot_df=df.tail(show_days).copy()
plot_df=plot_df.set_index('date')
plot_df=plot_df.rename(columns={
    'open':'Open',
    'high':'High',
    'low':'Low',
    'close':'Close',
    'volume':'Volume',
})
#MACD大于等于0时显示绿柱，否则显示红柱
macd_colors=['green' if value >=0 else 'red'
             for value in plot_df['MACD']]
#6设置附加图形
additional_plots=[
    #在第二个面板绘制DIF
    mpf.make_addplot(
        plot_df['DIF'],
        panel=2,
        color='blue',
        width=1,
        ylabel='MACD',
    ),
    mpf.make_addplot(
        plot_df['DEA'],
        panel=2,
        color='orange',
        width=1,

    ),
    mpf.make_addplot(
        plot_df['MACD'],
        panel=2,
        type='bar',
        color=macd_colors,
        alpha=0.6,
    ),
]
#7设置K线颜色
market_colors=mpf.make_marketcolors(
    up='green',
    down='red',
    inherit=True,
)
chart_style=mpf.make_mpf_style(
    marketcolors=market_colors,
    gridstyle='--',
)
#8绘制图表
mpf.plot(
    plot_df,
    type='candle',
    volume=True,
    addplot=additional_plots,
    style=chart_style,
    title=f"{target_stock} MACD",
    ylabel="Price",
    ylabel_lower="Volume",
    panel_ratios=(3, 1, 1),
    figsize=(14, 9),
)