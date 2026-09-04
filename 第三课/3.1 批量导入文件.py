import pandas as pd
import os
pd.set_option('expand_frame_repr', False)

#df=pd.read_csv(
    #'/Users/yuhanwen/Desktop/量化交易/yfinance crash course/刑不行量化/1.Python股票量化投资系统课程/第三课 pandas高阶/baostock_500_stocks_5y/daily/sh600004.csv',
    #parse_dates=['交易日期'],
#)
#print(df.head())
#批量导入函数
file_location='/Users/yuhanwen/Desktop/量化交易/yfinance crash course/刑不行量化/1.Python股票量化投资系统课程/第三课 pandas高阶/baostock_500_stocks_5y/daily'
#for root,dirs,files in os.walk(file_location):
    #print('当前文件夹:',root)
    #print('包含的文件夹:',dirs)
    #print('包含的文价:',files)

#exit()
#批量读取文件
file_list=[]
for root,dirs,files in os.walk(file_location):
       for filename in files:
           if filename.endswith('.csv'):
               file_path=os.path.join(root,filename)
               file_path=os.path.abspath(file_path)
               file_list.append(file_path)
print(file_list)
#遍历文件名
all_data=[]
for fp in sorted(file_list):
    print(fp)
    df=pd.read_csv(fp)
    all_data.append(df)
all_data=pd.concat(all_data)
print(all_data)
print(len(all_data))
#存入HDF文件中
all_data.to_hdf(
    "全部股票数据.h5",
    key="stock_data",
    mode="w"
)

exit()