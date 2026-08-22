import pandas as pd
pd.set_option('expand_frame_repr',False)
df=pd.read_hdf(
    '全部股票数据.h5',
    key='stock_data'
)
# print(df.head())
# print(df.groupby('交易日期'))
# print(df.groupby('股票代码').size())
# print(df.groupby('交易日期').get_group('2021-08-12'))
# print(df.groupby('股票代码').describe())
# print(df.groupby('股票代码').head(3))
# print(df.groupby('股票代码').tail(3))
# print(df.groupby('股票代码').last(3))
#对每组计算最大值
print(df.groupby('股票代码')[['收盘价','成交量']].max())
print(df.groupby('股票代码')[['收盘价','成交量']].mean())
print(df.groupby('股票代码')[['收盘价','成交量']].sum())
print(df.groupby('股票代码')[['成交量']].rank(pct=True))
#遍历每个分组
for x,y in df.groupby('股票代码'):
    print(x)
    print(y)