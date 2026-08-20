#取列表中的数
var_list=[1,3,4,5,6,7,8,9]
print(var_list,type(var_list))
print(var_list[0])
print(var_list[1])
print(var_list[2])
print(var_list[3])
print(var_list[-1])
print(var_list[-2])
#范围的取值
print(var_list[:3])
print(var_list[0:3])
print(var_list[3:])
print(var_list[2:])
print(var_list[1:8:2])
#两个list相加
var_list2=[2,3,5,6,3,2,5]
print(var_list+var_list2)
#判断是否存在这个列表中
var_list3=var_list+var_list2
print(1 in var_list3)
print(2 in var_list3)
print('与' in var_list3)
print('你好' in var_list3)
#判断list中的最大值最小值,还有他的长度
print(len(var_list3))
print(max(var_list3))
print(min(var_list3))
print(var_list3)
#删除元素
del var_list3[0]
print(var_list3)
#用index查找函数
print(var_list3.index(3))
#增加元素
var_list3.append(100)
print(var_list3)
#合并list操作
var_list3.extend([3,'seven'])
print(var_list3)
#逆序
list_var6=[1,3,2,7,8,9,5,6,4,0]
#list_var6.reverse()
#print(list_var6)
#print(sorted(list_var6))
list_var6.sort()
print(list_var6)


