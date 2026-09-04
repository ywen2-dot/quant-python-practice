# dict介绍 使用一对大括号就可以了
dict_var={}
print(dict_var)
#成对的对象，一个是key 一个是value
dict_var={
    'sh00001':'上证指数',
    'sz00001':'平安银行',
    'sh60000':'浦发银行'
}
print(dict_var)
#字典是没有顺序的 在一个dict中不可能存在两个 根据KEY的值获得对应的值
print(dict_var['sh00001'])
print(dict_var['sz00001'])

#增加
dict_var['sh600004']='白云机场'
print(dict_var)
dict_var['sh600004']='白云'
print(dict_var)
# 判断一个KEY是不是在dict里面
print('sh60000' in dict_var)
#输出一个dict中所有的key和value
dict_var.keys()
print(dict_var.keys())
# dict就是一种映射的关系，不能一对多，但是不能多对一


