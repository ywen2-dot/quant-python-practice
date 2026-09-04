import pandas as pd
pd.set_option('expand_frame_repr', False)
df=pd.read_excel(
    'A股近3年日线数据_10只股票.xlsx',
)
# 数据筛选，根据指定的条件,筛选出相关数据
#print(df[df['股票代码']=='600900.SH'].index)
#print(df[df['股票代码'].isin(['600519.SH','sh00001'])])
print(df[(df['收盘价']<2000) & (df['股票代码']=='600519.SH')])
