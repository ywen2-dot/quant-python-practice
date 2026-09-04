import pandas as pd
pd.set_option('expand_frame_repr',False)
df=pd.read_excel(
    'A股近3年日线数据_10只股票.xlsx'

)

#排序函数
#print(df.sort_values(by=['交易日期'], ascending=True))
#print(df.sort_values(by=['交易日期','股票代码'], ascending=[True,True]))
#两个df上下合并操作,append
print(df.columns.tolist())
df1=df.iloc[5:15][['交易日期','股票代码','收盘价','成交量（手）']]
print(df1)
df2=df.iloc[0:10][['交易日期','股票代码','收盘价','成交量（手）']]
print(df2)
print(pd.concat([df1,df2]))
df3=pd.concat([df1,df2],ignore_index=True)
print(df3)

#对数据去重
df3.drop_duplicates(
    subset=['交易日期','股票代码'],
    keep='first',
    inplace=True
)
print(df3)
#常用其他的函数
#df.reset_index(inplace=True,drop=False)
#df=df.rename(columns={'收盘价':'close','最低价':'low'})
#print(df.empty)
#df=pd.DataFrame()
#print(df.empty)
print(df.T)
print(df.head())