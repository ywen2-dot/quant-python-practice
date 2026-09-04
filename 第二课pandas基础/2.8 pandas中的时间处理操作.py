import pandas as pd
pd.set_option('expand_frame_repr',False)
df=pd.read_excel(
    'A股近3年日线数据_10只股票.xlsx',
    parse_dates=['交易日期']
)
#====时间处理
#print(df['交易日期'])
#print(type(df['交易日期']))
#print(pd.to_datetime('2026-08-04'))
#print(df['交易日期'].dt.year)
#print(df['交易日期'].dt.week)
#print(df['交易日期'].dt.day)
print(df['交易日期'].dt.dayofyear)
print(df['交易日期'].dt.dayofweeek)
