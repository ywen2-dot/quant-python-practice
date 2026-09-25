#止盈控制
#买入价格
entry_price=20
#止盈比例
take_profit_rate=0.08
#当前价格
current_price=18.7
#计算止损价格
take_profit_price=entry_price*(1+take_profit_rate)
# 判断是否触发止盈
take_profit_signal = current_price >= take_profit_price

print(f"买入价格：{entry_price:.2f} 元")
print(f"止盈比例：{take_profit_rate:.2%}")
print(f"止盈价格：{take_profit_price:.2f} 元")
print(f"当前价格：{current_price:.2f} 元")
print(f"是否触发止盈：{take_profit_signal}")