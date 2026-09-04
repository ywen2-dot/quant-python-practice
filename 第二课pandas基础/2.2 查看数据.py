import pandas as pd
pd.set_option('expand_frame_repr', False)
df=pd.read_excel(
    'sh600000_近三年日行情.xlsx',
    index_col=2,
    parse_dates=['交易日期'],
    #nrows=15,
)
#print(df.head())
# 看数据
#print(df.shape)
#print(df.shape[0])
#print(df.shape[1])
#print(df.columns)
#for col in df.columns:
    #print(col)
#print(df.index)

#for index in df.index:
    #print(index)
# print(df.dtypes)
#print(df.head())
#print(df.tail())
#print(df.sample(frac=0.4))
#print(df.info())
#print(df.describe())
#对print出的数据格式进行修正
#pd.set_option('display.max_rows', 100)
#print(df)
#选取特定的列
#print(df['开盘价'])
#print(df[['交易日期','开盘价']])
#print(df.loc['2023-08-08'])
#print(df.head())
#print(df.loc['2023-08-10':'2023-08-30'])
#print(df.loc[:,'开盘价':'收盘价'])
#print(df.loc['2023-08-08':'2023-08-14','开盘价':'收盘价'])
print(df.loc['2023-08-08','开盘价'])
#iloc操作：通过position来操作来读取数据
print(df.iloc[0])
print(df.iloc[1:3])
print(df.iloc[:,1:3])
print(df.iloc[:,:])