print(list(range(10)))
print(list(range(1,10)))
#循环语句‘
for code in ['sz100000','sh600000','sh600001','zx789290']:
    print(code)
#计算
total_result=0
for sum_result in range(101):
    total_result +=sum_result
    print(total_result)
#批量判断交易所
code_list=['sh200001','sh600002','sh600003','sh600004','sh600005','sh600006','sh600007','sz00001','sz4400000','hk700004']
for code in code_list:
    if code.startswith('sh'):
        print(code,'上交所')
    elif code.startswith('sz'):
        print(code,'深交所')
    else:
        print(code,'不属于任何所')
#另外一种方法
code_list=['sh200001','sh600002','sh600003','sh600004','sh600005','sh600006','sh600007','sz00001','sz4400000','hk700004']
for code in code_list:
    if code.startswith('sh'):
        print(code,'上交所')
        continue
    if code.startswith('sz'):
        print(code,'深交所')
        continue
    print(code,'交易所不存在')
#遍历
var_dict={
    'name': '上证指数',
    'code': 'sh00001',
    'open': '3058.8',
    'close': '3058.8',
    'high': '3058.8',
    'low': '3058.8',
    'volume': '3058.8',
}
for key in var_dict.keys():
    print(key,var_dict[key])