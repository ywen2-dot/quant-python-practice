import pandas as pd
pd.set_option('expand_frame_repr',False)

df=pd.read_excel(
    'A股近3年日线数据_10只股票.xlsx'

)
#排序函数
# print(df.sort_values(['交易日期'],ascending=True))
# print(df.sort_values(['交易日期','股票代码'],ascending=[True,True]))

print(df.columns.tolist())
df1=df.iloc[0:10,1:3]
df2=df.iloc[10:15,1:3]
df3=pd.concat([df1,df2],ignore_index=True)
print(df3)
 #删除重复值
df3.drop_duplicates(
    subset=['交易日期'],
    keep='first',
    inplace=True
)
df=df.rename(columns={
       '收盘价': 'close',
       '最低价': 'low'
 })
print(df)