def get_price(stock_code):

    return stock_code,'股票的价格是45'
print(get_price('sh000000'))

def price_var(var_1,var2=8):
    print(var_1,var2)
    return '我是两个变脸的返回值'
price_var('woshiyige',1111)


def nihao(var_1,var_2):
    print(var_1+var_2)
    return var_1 + var_2
nihao(3,2)