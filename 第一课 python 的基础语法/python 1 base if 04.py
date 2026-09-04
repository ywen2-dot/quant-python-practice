# 条件语句
name='ST浦发银行'
if name.startswith('ST'):
    print(name,'连续两个会计年度都会出现亏损')
print('继续你的逻辑')
# 多个条件判断
code='sz600000'
if code.startswith('ST'):
    print(code,'上交所')
elif code.startswith('sz'):
    print(code,'深交所')
else:
    print(code,'code不存在')

#高级写法
change=0.1
if change>0.1:
    status='涨停'
else:
    status='没有涨停'
print(change,status)