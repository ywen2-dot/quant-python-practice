import math
#帐户总资金
initial_capital=100000
#单笔交易最多承担帐户资金的1%风险
risk_rate=0.01
#买入价格
entry_price=20
#止损比例
stop_loss_rate=0.08
#A股一手通常是100股
lot_size=100
#计算止损价格
stop_price=entry_price*(1-stop_loss_rate)
#计算这次最多允许亏损多少钱
risk_amount=initial_capital*risk_rate
#计算每股最多亏损多少钱
risk_per_share=entry_price-stop_price
#计算理论上可以买多少gu
raw_shares=risk_amount/risk_per_share
#按蒸熟手买入，向下取整
shares=int(raw_shares//lot_size)*lot_size
#计算实际买入金额
position_value=shares*entry_price
#计算实际仓位比例
position_rate=position_value/initial_capital
#计算促发止损是的实际亏损
actual_max_loss=shares*risk_per_share
#计算实际风险占帐户比例
actual_risk_rate=actual_max_loss/initial_capital

# 10. 打印结果
print(f"账户总资金：{initial_capital:.2f} 元")
print(f"单笔风险比例：{risk_rate:.2%}")
print(f"买入价格：{entry_price:.2f} 元")
print(f"止损比例：{stop_loss_rate:.2%}")
print(f"止损价格：{stop_price:.2f} 元")
print(f"最多允许亏损：{risk_amount:.2f} 元")
print(f"每股可能亏损：{risk_per_share:.2f} 元")
print(f"理论买入数量：{raw_shares:.2f} 股")
print(f"实际买入数量：{shares} 股")
print(f"实际买入金额：{position_value:.2f} 元")
print(f"实际仓位比例：{position_rate:.2%}")
print(f"触发止损时实际亏损：{actual_max_loss:.2f} 元")
print(f"实际风险比例：{actual_risk_rate:.2%}")