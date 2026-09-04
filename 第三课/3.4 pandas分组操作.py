import pandas as pd
pd.set_option('expand_frame_repr',False)
df=pd.read_csv(
    'sh600000.csv',
)
#print(df.head())
#常见汇总操作
#print(df.groupby('date'))
#size计算每个group的行数
#print(df.groupby('code').size())
#获取某一个group
#print(df.groupby('date').get_group('2019-01-04'))
#一些常见的操作
#print(df.groupby('code').describe())
#print(df.groupby('code').head(3))
#print(df.groupby('code').tail(3))
#print(df.groupby('code').first(3))
#print(df.groupby('code').last(3))
#将group变量不设置为index
#计算每个group的均值
##print(df.groupby('code')[['close','volume']].max())
#print(df.groupby('code')[['close','volume']].mean())
#每个group的加总
#print(print(df.groupby('code')[['close','volume']].sum()))
#print(df.groupby('code')[['volume']].rank(pct=True))
print(df.groupby('code'))
#for x,y in df.groupby('code'):
   # print(y)
    #print(x)


