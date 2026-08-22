import pandas as pd
import os
pd.set_option('expand_frame_repr', False)
#df=pd.read_csv('sh600000.csv')
#print(df.head())
file_location='/Users/yuhanwen/Desktop/量化交易/yfinance crash course/刑不行量化/1.Python股票量化投资系统课程/第三课 pandas高阶/baostock_500_stocks_5y/daily'
# for root,dirs,files in os.walk(file_location):
#     print('当前的文件夹',root)
#     print('包含的文件夹',dirs)
#     print('包含的文件',files)
file_list=[]
for root,dirs,files in os.walk(file_location):
    for filename in files:
        if filename.endswith('.csv'):
            file_path=os.path.join(root,filename)
            file_path=os.path.abspath(file_path)
            file_list.append(file_path)

all_date=[]
for fp in file_list:
    print(fp)
    df = pd.read_csv(fp)
    all_date.append(df)
all_date=pd.concat(all_date,ignore_index=True)
print(all_date)
all_date.to_hdf(
    '全部股票数据.h5',
    key='stock_data',
    mode='w'
)
exit()