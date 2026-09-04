#导库
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
pd.set_option('expand_frame_repr', False)
engine=create_engine('sqlite:////Users/yuhanwen/Desktop/量化交易/yfinance crash course/自学量化/1.Python股票量化投资系统课程/第四课 构建自己的股票数据库/stock.db')
#读取数据
selected=pd.read_sql('select * from stock_500_stock_selected',con=engine)
print(selected.head())
#挑选一只股票出来
target_name=selected.loc[0,'股票名称']
target_code=selected.loc[0,'股票代码']
#读取这只股票的历史数据

stock_daily=pd.read_sql(
    f'''
    select * from stock_500_daily_cumulative 
    where 股票代码='{target_code}'
    order by 交易日期
    ''',
    con=engine
)

print(stock_daily.head())
#把交易日期转换一下
stock_daily['交易日期']=pd.to_datetime(stock_daily['交易日期'])
#画第一张图
plt.figure(figsize=(12,6))
plt.plot(
    stock_daily['交易日期'],
    stock_daily['收盘价'],
    label='close_price'
)
#画均线的图
plt.plot(
    stock_daily['交易日期'],
    stock_daily['MA5'],
    label='MA5'
)
plt.plot(
    stock_daily['交易日期'],
    stock_daily['MA20'],
    label='MA20'
)
plt.title('study')
plt.xlabel("trade_date")
plt.ylabel("price")
plt.legend()
plt.grid(True)
plt.show()
