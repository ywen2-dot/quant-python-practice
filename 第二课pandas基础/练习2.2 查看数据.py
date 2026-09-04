import pandas as pd
from numpy.ma.extras import column_stack

pd.set_option('expand_frame_repr',False)
df=pd.read_excel(
    'sh600000_近三年日行情.xlsx',
    parse_dates=['交易日期'],
    index_col='交易日期'
)
#看数据
# print(df.shape)
# print(df.shape[0])
# print(df.shape[1])
# print(df.columns)
# for col in df.columns:
#     print(col)
# print(df.index)
# for index in df.index:
#     print(index)
# print(df.info)
# print(df.describe())
# print(df.head())
# print(df.tail())
# print(df.dtypes)
# print(df.sample(frac=0.4))
#对print出得数据格式进行修正
# pd.set_option('display.max_columns',100)
# print(df)
#选取特定的列
# print(df['开盘价'])
# print(df[['开盘价','收盘价']])
# print(df.head())
# print(df.loc['2023-08-08'])
# print(df.loc['2023-08-08':'2023-08-10' ])
print(df.iloc[1])
print(df.iloc[1:3])
print(df.iloc[:,1:3])
