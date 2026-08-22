import pandas as pd
df=pd.read_csv('sh600000.csv')
df['date']=pd.to_datetime(df['date'])
df.set_index('date',inplace=True)
rule_type='1W'
#计算周收盘价
# week_df=df[['close']].resample(rule=rule_type).last()
# #计算周收盘价最大值
# week_df['high']=df['high'].resample(rule=rule_type).max()
# # 周开盘价
# week_df['open'] = df['open'].resample(rule=rule_type).first()
# #周最低价
# week_df['low'] = df['low'].resample(rule=rule_type).min()
#周成交量
print(df.head())
week_df = df.resample(
    rule=rule_type,

    label='left'
).agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
})
week_df=week_df[['open','high','low','close','volume']]
week_df.dropna(
    subset=['open'],
    inplace=True
)
print(week_df)