import pandas as pd
pd.set_option('expand_frame_repr', False)
df=pd.read_hdf(
    '全部股票数据.h5',
    key='sh600000'
)
print(df.head())