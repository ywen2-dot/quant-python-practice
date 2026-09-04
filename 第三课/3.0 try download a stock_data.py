import pandas as pd
import baostock as bs
login_result=bs.login()
print(login_result.error_code)
print(login_result.error_msg)
result=bs.query_history_k_data_plus(
    'sh.600000',
    fields='date,code,open,high,low,close,preclose,volume,amount',
    start_date='2019-01-01',
    end_date='2019-12-31',
    frequency='D',
    adjustflag='3'
)
rows=[]
while login_result.error_code =='0' and result.next():
    row=result.get_row_data()
    rows.append(row)
df=pd.DataFrame(rows,columns=result.fields)
print(df.head())
df.to_csv('sh600000.csv',index=False,encoding='utf-8-sig')

bs.logout()