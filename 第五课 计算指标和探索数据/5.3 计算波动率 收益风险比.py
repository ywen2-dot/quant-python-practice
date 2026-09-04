import pandas as pd
from sqlalchemy import create_engine
pd.set_option('expand_frame_repr', False)
#连接数据库
engine=create_engine('sqlite:////Users/yuhanwen/Desktop/量化交易/yfinance crash course/自学量化/1.Python股票量化投资系统课程/第四课 构建自己的股票数据库/stock.db')
#读取数据
stock_daily=pd.read_sql(
    'select * from stock_500_daily_cumulative',con=engine
)
print(stock_daily)
#转换日期格式
stock_daily['交易日期']=pd.to_datetime(stock_daily['交易日期'])
#确保涨跌幅是数字
stock_daily['涨跌幅']=pd.to_numeric(stock_daily['涨跌幅'])
#确保累计收益率是数字
stock_daily['累计收益率']=pd.to_numeric(stock_daily['累计收益率'])
#按照股票代码和日期排序
stock_daily=stock_daily.sort_values(['股票代码','交易日期']).reset_index(drop=True)
#每只股票计算波动率
risk_summary=(stock_daily.groupby(['股票代码','股票名称']).agg(平均日收益率=('涨跌幅','mean'),日波动率=('涨跌幅','std'),最后累计收益率=('涨跌幅','last')).reset_index())
print(risk_summary)
risk_summary['收益风险比']=risk_summary['平均日收益率']/risk_summary['日波动率']
#计算年化波动率
risk_summary['年化波动率']=risk_summary['日波动率']*(252**0.5)
#转换成百分数
risk_summary['年化波动率百分比']=risk_summary['年化波动率']*100
#按照累计收益率从高到低
risk_summary=risk_summary.sort_values('最后累计收益率',ascending=False)
print(risk_summary.head(5))
#看平均日收益率最高的股票
risk_summary=risk_summary.sort_values('平均日收益率',ascending=False)
print(risk_summary.head(5))
#看日波动率最低的票子
risk_summary=risk_summary.sort_values('日波动率',ascending=True)
print(risk_summary.head(5))
#看风险收益最高的票子
risk_summary=risk_summary.sort_values('收益风险比',ascending=False)
print(risk_summary.head(5))
#按累计收益率排名
risk_summary=risk_summary.sort_values('累计收益率',ascending=False)
print(risk_summary.head(5))
#保存表
risk_summary.to_sql('stock_500_risk_summary',con=engine,if_exists='replace',index=False)
print('风险指标保存成功')