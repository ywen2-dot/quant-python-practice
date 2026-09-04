#字典的基本用法
dict_var={}
print(dict_var)
code={
    "天河机场":'sh600000',
    '泸州老窖':'sz400000',
    '长电科技':'sh689000'
}
print(code)
#获取列表中的数值
print(code['天河机场'])
print(code['泸州老窖'])
print(code['长电科技'])
#增加字典
code['莲花味精']='sh500000'
print(code)
#判断和输出字典中的全部值
print('长电科技' in code)
print('泸州老窖' in code)
print('不差钱' in code)
print('天河机场' in code)
print(code.keys())