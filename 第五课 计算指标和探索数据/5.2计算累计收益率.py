from sqlalchemy import create_engine
import pandas as pd
#连接数据库
engine=create_engine('sqlite:////Users/yuhanwen/Desktop/量化交易/yfinance crash course/自学量化/1.Python股票量化投资系统课程/第四课 构建自己的股票数据库/stock.db')
#读取数据表
stock_daily=pd.read_sql('select * from stock_500_daily_ma',con=engine)
#转换交易日期
stock_daily['交易日期']=pd.to_datetime(
    stock_daily['交易日期']
)
#转换收盘价
stock_daily['收盘价']=pd.to_numeric(stock_daily['收盘价'])
#按股票代码和日期排序
stock_daily=stock_daily.sort_values(['股票代码','交易日期']).reset_index(drop=True)
#计算每天的收益率
stock_daily['累计收益率']=(stock_daily.groupby('股票代码')['涨跌幅'].transform(lambda x: (1+x.fillna(0)).cumprod()-1))
#转换成百分比
stock_daily['累计收益百分比']=(stock_daily['累计收益率']*100)
#查看浦发银行后面10条数据)
print(stock_daily[stock_daily['股票代码']=='sh600000'][[
    "交易日期",
    "收盘价",
    "涨跌幅",
    "涨幅比例",
    "累计收益百分比"
]].tail(10))
#保存成新表
stock_daily.to_sql('stock_500_daily_cumulative',con=engine,if_exists='replace',index=False)
print('累计收益率保存成功')