import yfinance as yf
#浦发银行
symbol='600000.SS'
stock=yf.Ticker(symbol)
#获取最近一天的1分钟K线
minute_df=stock.history(
    period='1d',
    interval='1m',
    auto_adjust=False,
    timeout=60
)
#获取日线数据
daily_df=stock.history(
    period='5d',
    interval='1d',
    auto_adjust=False,
    timeout=60
)
print('日线数据行数',len(daily_df))
print('分钟数据行数',len(minute_df))
if minute_df.empty:
    print('没有获取到1分钟的数据')
else:
    print('\n最新一根1分钟K线：')
    print(minute_df.tail(1))
if daily_df.empty:
    print('没有获取到一天的数据')
else:
    print('\n最新一根dayK线')
    print(daily_df.tail(1))

