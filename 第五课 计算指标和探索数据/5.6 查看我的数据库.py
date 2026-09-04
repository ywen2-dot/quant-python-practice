import pandas as pd
from sqlalchemy import create_engine
engine=create_engine('sqlite:////Users/yuhanwen/Desktop/量化交易/yfinance crash course/自学量化/1.Python股票量化投资系统课程/第四课 构建自己的股票数据库/stock.db')
#查看我数据库
tables=pd.read_sql(  """
    select name
    from sqlite_master
    where type = 'table'
    """,
    con=engine)
print(tables)