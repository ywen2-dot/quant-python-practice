import pandas as pd
pd.set_option('expand_frame_repr',False)
df=pd.read_excel(
    'sh600000_近三年日行情.xlsx',
    parse_dates=['交易日期'],
    index_col='股票代码'
)
print(df.head())