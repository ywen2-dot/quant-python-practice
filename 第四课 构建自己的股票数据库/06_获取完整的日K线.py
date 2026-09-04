import pandas as pd
import yfinance as yf
from pyspark.examples.src.main.python.als import update
from sqlalchemy import create_engine
from datetime import datetime
import shutil
from sqlalchemy.dialects.mssql.information_schema import columns

pd.set_option('expand_frame_repr', False)
#创建数据库连接
engine=create_engine('sqlite:///stock.db')
#设置股票代码
symbol='600000.SS'
#添加股票查询
stock=yf.Ticker(symbol)
#获取2024年至今的全部日K
history_daily=stock.history(
    start='2024-01-01',
    interval='1d',
    auto_adjust=False,
    timeout=60
)
#判断是否获取到数据
if history_daily.empty:
    print('没有获取到数据')
else:
    history_daily=history_daily.reset_index()
    #日期只保留年月日并保存成字符串窜
    history_daily['Date']=(history_daily['Date'].astype(str).str.strip().str[:10])
    #添加股票代码
    history_daily['股票代码']=symbol
    #添加本次抓取时间
    history_daily['抓取时间']=datetime.now()
    #9只保留需要的字段
    history_daily=history_daily[["Date",
                             "股票代码",
                             "Open",
                             "High",
                             "Low",
                             "Close",
                             "Volume",
                             "抓取时间"]]
    #10 查看结果
    print('历史日K线总条数',len(history_daily))
    print('04年的前几根K线',history_daily.head(3))
    print('最新几根K线',history_daily.tail(5))
#读取数据库中原有的日K线
old_daily=pd.read_sql_query(
    'select * from daily_kline',
    engine
)


#同一数据库中的日期格式
old_daily['Date']=(old_daily['Date'].astype(str).str.strip().str[:10])
print('数据库中原有的数据数量',len(old_daily))
#找出数据库中没有的新数据
old_keys=set(
    zip(
        old_daily['股票代码'].astype(str),
        old_daily['Date']
    )
)
new_keys=list(
    zip(
        history_daily['股票代码'].astype(str),
        history_daily['Date']
    )
)
history_daily['是否已经存在']=[
    key in old_keys
    for key in new_keys
]
new_daily=history_daily[history_daily['是否已经存在']==False].copy()
new_daily=new_daily.drop(columns=['是否已经存在'])
#保存数据
if new_daily.empty:
    print('没有更新数据，不需要保存')
    engine.dispose()
    raise SystemExit
else:
    new_daily.to_sql(
        'daily_kline',
        engine,
        index=False,
        if_exists='append',
    )
    print('新增日K数量',len(new_daily))
    print('保存K线数据成功')

# 查看保存结果
updated_daily = pd.read_sql_query(
    "SELECT * FROM daily_kline",
    engine
)

print(updated_daily.tail(5))
engine.dispose()
