#止损控制
#买入价格
entry_price=20
#止损比例
stop_loss_rate=0.08
#当前价格
current_price=18.7
#计算止损价格
stop_price=entry_price*(1-stop_loss_rate)
#判断是否触发止损
stop_signal=current_price<stop_price

print(f'买入价格：{entry_price}')
print(f'止损比例：{stop_loss_rate}')
print(f'当前价格：{current_price}')
print(f'止损价格：{stop_price:.2f}')
print(f'是否触发止损：{stop_signal}')