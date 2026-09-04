 #异常处理的一个例子
import random
import time
def buy():
     random_number=random.random()
     print(random_number)
     if random_number<=0.5:
         print('成功买入')
     else:
         print('买入失败')
         raise ValueError('程序报错')

buy()
try_max_count=5
try_count=0
while True:
    try:
        buy()
    except Exception as e:
        print(e)
        print('警告，下单出错了，请停止一秒再尝试')
        time.sleep(1)
        try_count +=1
        if try_count>=try_max_count:
            print('超过最大尝试次数，下单失败，通知XXX来看')
            break
        else:
           continue
    else:
        try_count=0
        print("下单成功")
        break