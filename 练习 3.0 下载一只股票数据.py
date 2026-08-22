import pandas as pd
import  baostock as bs
login_result=bs.login()
print(login_result.error_code)
print(login_result.error_msg)
result=bs.query_history_k_data_plus(
    code='sh.600000',
    fields='date,code,open,high,low,close,preclose,volume,amount',
    start_date='2019-01-01',
    end_date='2019-12-31',
    frequency='D',
    adjustflag='3'
)
rows=[]
while result.error_code=='0' and result.next():
    rows.append(result.get_row_data())
df=pd.DataFrame(rows,columns=result.fields)
print(df.head())
df.to_csv('sh600000.csv',index=False,encoding='utf-8')
bs.logout()