list_var=[]
print(list_var,type(list_var))
list_var1=[1,3,4,5,6,7,8,9]
print(list_var1,type(list_var1))
print(list_var1[0])
print(list_var1[2])
print(list_var1[1])
print(list_var1[5])
print(list_var1[-1])
# 取list中的一窜数字
print(list_var1[3:5])
print(list_var1[3:])
print(list_var1[:5])
print(list_var1[3:6:2])#取每2个元素中的第一个

#======list的常见操作：两个list想加
list_var2=[1,'2',3,4,5,6,7,8,9,0]
print(list_var1+list_var2)
# 判断一个元素是否在这个list中
list_var3=[1,'2',3,4,5,6,7,8,9,0]
print(1 in list_var3)
print(100 in list_var3)

# 判断这个list中的长度
print(len(list_var3))

#判断这个list中的最大的元素
print(max(list_var1))
print(min(list_var1))

# 删除在list中的元素
list_var4=[1,2,3,4,5,6,7,8,9,0]
del list_var4[0]
print(list_var4)
#查找list中的某一个元素
list_var5=[1,2,3,4,5,6,7,8,9,0]
print(list_var5.index(4))
#增加元素
list_var5.append([100])
print(list_var5)
#合并List操作
list_var5.extend([6,'seven'])
print(list_var5)
#逆序
list_var6=[1,3,2,7,8,9,5,6,4,0]
#list_var6.reverse()
#print(list_var6)
#list_var6.sort()
#print(list_var6)
print(sorted(list_var6))
print(list_var6)

