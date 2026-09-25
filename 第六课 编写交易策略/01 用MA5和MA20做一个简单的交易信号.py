import pandas as pd
from sqlalchemy import create_engine
pd.set_option('expand_frame_repr',False)

# 连接数据库
engine = create_engine(
    "sqlite:////Users/yuhanwen/Desktop/量化交易/yfinance crash course/量化入门/1.Python股票量化投资系统课程/第四课 构建自己的股票数据库/stock.db"
)

# 读取候选股票池
selected = pd.read_sql("select * from stock_500_stock_selected", con=engine)
print(selected.head())
#选出第一支股票
target_code=selected.loc[0,'股票代码']
target_name=selected.loc[0,'股票名称']
#读取这只股票
df=pd.read_sql(
    f'''
    select 股票代码,股票名称,交易日期,收盘价,MA5,MA20,累计收益率
    from stock_500_daily_cumulative
    where 股票代码='{target_code}'
    order by 交易日期
    '''

, con=engine)
print(df.head())
#日期转换成真正的时间格式
df['交易日期']=pd.to_datetime(df['交易日期'])
#去掉前面还没算出来的空值
df=df.dropna(subset=['MA5','MA20']).reset_index(drop=True)
#position=1表示MA5在MA20上方，偏向持有
#position=0表示MA5在MA20下方，偏向空仓
df['postion']=0
df.loc[df['MA5']>df['MA20'],'postion']=1
#看今天和昨天postion有没有变化
df['yesterday_postion']=df['postion'].shift(1).fillna(0)
print(df.head())
#今天刚从0变成1，就是买入信号
df['buy_signal']=((df['postion']==1 & (df['yesterday_postion']==0))).astype(int)
#今天从1变成0，就是卖出信号
df['sell_signal']=((df['postion']==0 & (df['yesterday_postion']==1))).astype(int)
#看前30行的结果
print(df.head(30))
#看买入日期
print('买入日期：')
print(df.loc[df['buy_signal']==1,'交易日期'])
print(df.loc[df['sell_signal']==0,'交易日期'])
