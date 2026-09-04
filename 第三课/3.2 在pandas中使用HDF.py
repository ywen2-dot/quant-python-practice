
import pandas as pd
pd.set_option('expand_frame_repr', False)
df=pd.read_csv(
    'sh600000.csv',

)
#print(df.head())
df['date']=pd.to_datetime(df['date'])
#df.set_index('date',inplace=True)
#print(df)
#周期转换方法
#rule_type='1W'
#period_df=df[['close']].resample(rule=rule_type).last()
#print(period_df.head(20))
#开，搞，低价格，成交量
#period_df['high']=df['high'].resample(rule=rule_type).max()
#period_df['open']=df['open'].resample(rule=rule_type).first()
#period_df['low']=df['low'].resample(rule=rule_type).min()
#period_df['volume']=df['volume'].resample(rule=rule_type).sum()
#print(period_df)
#第二种方法
rule_type='1W'
period_df=df.resample(rule=rule_type,on='date',label='left').agg(
    {
        'open':'first',
        'high':'max',
        'low':'min',
        'close':'last',
        'volume':'sum',
    }
)
period_df=period_df[['open','high','low','close','volume']]
print(period_df)
#去除不要的数据
period_df.dropna(subset=['open'],inplace=True)
print(period_df)