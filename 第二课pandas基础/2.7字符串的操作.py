import pandas as pd
pd.set_option('expand_frame_repr',False)
df=pd.read_excel(
    'A股近3年日线数据_10只股票.xlsx'
)
#字符串处理
print(df['股票代码'].str[:2])
print(df['股票代码'].str.upper())
print(df['股票代码'].str.lower())
print(df['股票代码'].str.len())
print(df['股票代码'].str.strip())
print(df['股票代码'].str.contains('SH'))
print(df['股票代码'].str.replace('SH','sz'))
