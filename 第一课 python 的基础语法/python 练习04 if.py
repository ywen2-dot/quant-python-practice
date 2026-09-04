#条件语句
name='ST浦发银行'
if name.startswith('ST'):
    print(name,'连续几个季度都会出现亏损')
print('请你继续你的逻辑')
#多个条件语句判断
code='SH00001'
if code.startswith('SH'):
    print(code,'深交所')
elif code.startswith('SZ'):
    print(code,'上证指数')
else:
    print(code,'code不存在')
# 更多写法
change=0.1
if change>0.1:
    status='涨停'
elif 0<change<0.1:
    status='上涨'
else:
    status='股票会跌'
print(change,status)