import pandas as pd
pd.set_option('expand_frame_repr', False)

#导入数据
df=pd.read_excel(
    'sh600000_近三年日行情.xlsx',
    #index_col='交易日期'
)

#列操作 列的加减乘除
#print(df['交易日期']+ pd.Timedelta(hours=15))
#print(df['收盘价']*100)
#print(df[['收盘价','成交量']])
#print(df['收盘价']*df['成交量'])
#新增一列
#df['交易日期2']=df['交易日期']+pd.Timedelta(hours=15)
#df['交易所']='上交所'
#====统计函数
#print(df['收盘价'].mean())
#print(df[['最高价','最低价']].mean(axis=1))
#print(df['最高价'].max())
#print(df['最低价'].min())
#print(df['收盘价'].std)
#print(df['收盘价'].count())
#print(df['收盘价'].median())
#print(df['收盘价'].quantile(0.25))
#print(df['收盘价'].describe())

#===shift函数，删除列的方法
#df['下周期收盘价']=df['收盘价'].shift()
#del df['下周期收盘价']
#df['涨跌']=df['收盘价'].diff(3)
#df=df.drop(['涨跌'],axis=1,inplace=False)
df['涨跌幅']=df['收盘价'].pct_change(1)
#===cum(cumulative)类函数
#print(df.head())
#df['累计成交量']=df['成交量'].cumsum()

#print(df[['交易日期','成交量','累计成交量','涨跌幅']])
#print((df['涨跌幅']+1.0).cumprod())
df['收盘价排名']=df['收盘价'].rank(ascending=False)
df['涨跌幅排名']=df['涨跌幅'].rank(ascending=False,pct=True)
print(df['收盘价'].value_counts())
print(df.head())