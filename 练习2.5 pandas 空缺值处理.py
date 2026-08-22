import pandas as pd
df=pd.read_excel(
'A股近3年日线数据_10只股票.xlsx'
)
index=df[df['交易日期'].isin([pd.Timestamp('2023-08-09')])].index
df.loc[index,'月头']=df['交易日期']
#print(df.dropna(how='any'))
#print(df.dropna(subset=['月头','收盘价'],how='any'))
#补全空缺值
df['月头']=df['月头'].fillna(value=df['收盘价'])
print(df)
