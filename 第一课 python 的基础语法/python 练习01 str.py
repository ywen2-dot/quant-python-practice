name='5️11111'
code='123'
print('我有一只大西瓜')
print('what\'s up')
#字符串中的加减法
a='abc'
b='def'
print(a+b,type(a+b))
#字符串中的乘法
print(a*3)
print('*'*28)
#字符串中的start.with,end.with
stock_code='sh600000'
print(stock_code.startswith('0'))
print(stock_code.endswith('sh'))
#判断
print('写' in name)
print('毛' in name )
#替换replace语法
stock_new_code=stock_code.replace('sh','sz')
print(stock_new_code)
#split操作，就是分组操作
info='sh600000,sz50000,ch789766'
print(info.split(','),type(info.split(',')))
print(info.split('ch789766'))
print(info.split(',')[0])
#组合
#var='sh600000,sz50000,ch789766'
#print(''.join(var))
var='sh600000','sz50000','ch789766'
print(''.join(var))
#去空格
phone=' 18 19 20 '
print(phone)
print(phone.strip())
#字符串中选取特定字符
name_1='哈哈哈哈我能你'
print(name_1[0])
print(name_1[-1])
print(name_1[2])
print(name_1[3])
print(len(name_1[3]))
