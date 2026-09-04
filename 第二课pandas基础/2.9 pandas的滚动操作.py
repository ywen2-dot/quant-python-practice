import pandas as pd
pd.set_option('expand_frame_repr',False)
df=pd.read_excel(
    'sh600000_近三年日行情.xlsx'
)
print(df['收盘价'].mean())
# 如何得到每一天的最近3天的close的均值？计算移动平均线？
#使用rolling函数
#df['收盘价_3天均值']=df['收盘价'].rolling(3).mean()
#print(df)
#df['收盘价_3天最大值']=df['收盘价'].rolling(3).max()
#print(df)
#df['收盘价_3天最小值']=df['收盘价'].rolling(3).min()
#print(df)
#df['收盘价_3天最小值']=df['收盘价'].rolling(3).std()
#如果想要计算每一天从一开始至今的均值
#df['收盘价_至今的均值']=df['收盘价'].expanding().mean()
#print(df)
#print(df['收盘价'].mean())
df['收盘价_至今最大值']=df['收盘价'].expanding().max()
#print(df)
#===输出到本地文件
print(df)
df.to_excel('output.xlsx',index=False)