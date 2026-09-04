#函数的基本定义
def print_two_var(str1,str2='hello world'):
    print(str1)
    print(str2)
    return '我是print_two_var的返回值'
print_two_var('你好 python','你好 量化投资')
print_two_var('你好 量化投资','你好 python')
temp=print_two_var('你好 python','你好 量化投资')
print(temp)
def get_price(stock_code):
    print(stock_code,'的股价是：45')
    return 45
print(get_price('sh00002'))