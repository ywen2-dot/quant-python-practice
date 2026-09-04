import random
def buy():
    random_number=random.random()
    print(random_number)
    if random_number<=0.5:
        print('成功买入')
    else:
        print('买入失败')

buy()