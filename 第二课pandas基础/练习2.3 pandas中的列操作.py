import pandas as pd
pd.set_option('expand_frame_repr', False)

#导入数据
df=pd.read_excel(
    'sh600000_近三年日行情.xlsx',
    #index_col='交易日期'
)

# print(df['交易日期']+pd.Timedelta(hours=15))
# print(df['收盘价']*100)
# print(df[['收盘价','成交量']])
# print(df.head())
#新增列
df['交易日期2']=df['交易日期']+pd.Timedelta(hours=2)
df['上交所']='上交所'
print(df.head())
print(df['收盘价'].mean())
print(df[['收盘价','开盘价']].mean())
print(df['最高价'].max())
print(df['最高价'].std())
print(df['最高价'].min())
print(df['最高价'].count())
print(df['最高价'].median())
df['最高价'].quantile(0.25)
print(df['最高价'].describe())