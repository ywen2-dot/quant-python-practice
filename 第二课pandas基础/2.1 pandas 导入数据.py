
import pandas as pd
df=pd.read_excel(
    'sh600000_近三年日行情.xlsx',
    parse_dates=['交易日期'],
    index_col='交易日期'
    #usecols=['交易日期','收盘价'],
)
print(df.head())

