class_name="泻羽"
code="12345"
print('what is up')
print('waht\'s up\t')
print('\\')
print(r'what\'s up')
#自付窜中的加减
str1='abc'
str2='def'
print(str1+str2)
print(str2)
#字符串的乘法
print(str1*3)
print('*'*30)
# startwith,endswith
stock_code='sh600000'
print(stock_code.startswith('sh'))
print(stock_code.startswith('s'))
print(stock_code.startswith('d'))
print(stock_code.endswith('0'))
# 判断
name='谢雨'
print('谢' in name)
print('羽' in name)
# 替换
stock_code='sh00001'
stock_code=stock_code.replace('sh00001','sz00002')
print(stock_code)
#split操作
info='sh600000,sz00001,sh60004'
print(info.split(','),type(info.split(',')))
print(info.split(',')[0])
print(info.split('sh60004'))
#组合
list_var=['我','呀','有','每','你','有','喊']
print(list_var)
print(''.join(list_var))
#去空格
phone=' 188 199 100 '
print(phone)
print(phone.strip())
#字符串中选取特定的字符,把字符当作list
name='行不行量化课程'
print(name[0])
print(name[:3])
print(name[3:])
print(len(name))
print(name[-1])




