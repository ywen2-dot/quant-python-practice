#移动止损
#买入价格
entry_price=20
#持仓期间出现过的最高价格
highest_price=25
#移动止损比例
trailing_stop_loss=0.08
#当前价格
current_price=22.5
#根据最高价计算移动止损价格
trailing_stop_price=highest_price*(1-trailing_stop_loss)
#判断是否触发止损
trailing_stop_signal=(current_price<=trailing_stop_price)
print(f"买入价格：{entry_price:.2f} 元")
print(f"持仓最高价格：{highest_price:.2f} 元")
print(f"移动止损比例：{trailing_stop_loss:.2%}")
print(f"移动止损价格：{trailing_stop_price:.2f} 元")
print(f"当前价格：{current_price:.2f} 元")
print(f"是否触发移动止损：{trailing_stop_signal}")