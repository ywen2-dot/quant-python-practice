
print(list(range(10)))
print(list(range(2,6)))
#for循环语句
for code in ['sh600000','sz400000','hz090999','sh600000']:
    print(code)


# 计算
sum_result = 0
for number in range(101):
    sum_result += number
    print(number,sum_result)

#案例3 批量判断股票代码所在的交易所
code_list=['sh200001','sh600002','sh600003','sh600004','sh600005','sh600006','sh600007','sz00001','sz4400000','hk700004']
for code in code_list:
    if code.startswith('sh'):
        print(code,'上交所')
    elif code.startswith('sz'):
        print(code,'深交所')
    else:
        print(code,'不属于任何所')

code_list=['sh200001','sh600002','sh600003','sh600004','sh600005','sh600006','sh600007','sz00001','sz4400000','hk700004']
for code in code_list:
    if code.startswith('sh'):
        print(code,'上交所')
        continue
    if code.startswith('sz'):
        print(code,'深交所')
        continue
    print(code,'不属于任何所')

    # 案例 遍历一个dict中的所有的元素
    var_dict={
        'name':'上证指数',
        'code':'sh00001',
        'open':'3058.8',
        'close':'3058.8',
        'high':'3058.8',
        'low':'3058.8',
        'volume':'3058.8',
    }
    for key in var_dict.keys():
        print(key,':',var_dict[key])

#案例4 for循环的高级写法
change_list_rounded=[0.012234,0.4832741,0.02727483]
change_list=[]
for change in change_list_rounded:
    change_list_rounded=(round(change,2))
    change_list.append(change_list_rounded)
print(change_list)
