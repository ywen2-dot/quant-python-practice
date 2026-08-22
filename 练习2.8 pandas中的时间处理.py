import pandas as pd
pd.set_option('expand_frame_repr',False)
df=pd.read_excel(
    'sh600000_近三年日行情.xlsx',
    parse_dates=['交易日期']
)
print(df.head())
print(df['交易日期'])
print(type(df['交易日期']))
print(df['交易日期'].dt.year)
print(df['交易日期'].dt.day)
print(df['交易日期'].dt.dayofweek)