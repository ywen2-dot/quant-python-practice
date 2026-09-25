import pandas as pd
from sqlalchemy import create_engine
from sympy.physics.units import amount
import numpy as np
pd.set_option('expand_frame_repr', False)
#======参数设置======
initial_capital=100000.0
#每次买入最多初始资金的百分之10，包含买入费用
position_size_rate=0.1
#最多同时持有3只股票
max_position=3
#简化费用：手续费
fee_rate=0.0005
#买入股数按100股取整
lot_size=100
#确认zagzig的幅度
zigzag_rate=0.09
#准备信号的有效窗口
setup_valid_days=10
#最近多少个交易日出现过MACD金叉
macd_valid_days=10
#布林带的宽度
bb_std_multiple=0.5
#同一天买入信号过多时，优先处理排在前面的股票
stock_list = [
    "sh600000",
    "sh600004",
    "sh600006",
    "sh600007",
    "sh600008",
    "sh600009",
    "sh600016",
    "sh600030",
    "sh600276",
    "sh600519",
]
#创建连接数据库
engine=create_engine('sqlite:////Users/yuhanwen/Desktop/量化交易/yfinance crash course/量化入门/1.Python股票量化投资系统课程/第四课 构建自己的股票数据库/stock.db')
def prepare_stock_data(target_stock):
    df = pd.read_sql(
        f"""
        SELECT *
        FROM stock_500_daily
        WHERE 股票代码 = '{target_stock}'
        """,
        engine,
    )
    if df.empty:
        raise ValueError("没有找到这只股票")
    #吧数据库中的中文列改名为程序使用的英文列名字
    df=df.rename(columns={
        '股票代码':'code',
        '股票名称':'name',
        '交易日期':'date',
        '开盘价':'open',
        '最高价':'high',
        '最低价':'low',
        '收盘价':'close',
        '成交量':'volume',
        '前收盘价':'pre_close',
        '成交额':'deal_volume',
    })
    #无法识别的日期转换为缺失值
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )
    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    # 把价格和成交量转换为数值
    df[numeric_columns] = df[numeric_columns].apply(
        pd.to_numeric,
        errors="coerce",
    )
    # 删除关键数据缺失的记录
    df = df.dropna(
        subset=["date", *numeric_columns]
    )
    # 一个交易日只保留一条记录
    df = df.drop_duplicates(
        subset="date",
        keep="last",
    )
    # 按日期从早到晚排列
    df = df.sort_values("date")
    df = df.reset_index(drop=True)
    #========计算MACD=======
    df['EM12']=df['close'].ewm(span=12,adjust=False).mean()
    df['EM26']=df['close'].ewm(span=26,adjust=False).mean()
    df['DIF']=df['EM12']-df['EM26']
    df['DEA']=df['DIF'].ewm(span=9,adjust=False).mean()
    df['MACD']=2*(df['DIF']-df['DEA'])
    #========计算布林带=======
    # 得到中轨
    df['BB_middle'] = df['close'].rolling(20).mean()
    # 标准差：衡量价格有多分散
    df['BB_std'] = df['close'].rolling(20).std()
    # 计算上轨和下轨
    df['BB_upper'] = df['BB_middle'] + bb_std_multiple * df['BB_std']
    df['BB_lower'] = df['BB_middle'] - bb_std_multiple* df['BB_std']


    #========MACD条件=========
    #DIF在DEA上方
    df['macd_above']=df['DIF']>df['DEA']
    df['macd_low_strong']=df['macd_above']&(df['DIF']<0)
    #上一个交易日DIF是否在DEA的上方
    df['macd_above_yesterday']=df['macd_above'].shift(1,fill_value=False)
    #昨天不在上方，今天在上方表示出现金叉
    df['macd_buy_signal']=df['macd_above']&(df['macd_above_yesterday']==False)
    #包含当天，最近10个交易日是否出现过金叉
    df['macd_buy_recent']=df['macd_buy_signal'].rolling(macd_valid_days,min_periods=1).max().astype(bool)
    #=========布林带条件========
    #收盘在上轨之上
    df['bb_buy_signal']=(df['close']>df['BB_upper'])
    df['bb_sell_signal']=(df['close']<df['BB_lower'])
    df['sell_signal']=df['bb_sell_signal']
    #==========zagzig确认信号==========
    df['zigzag_buy_signal']=False
    #0初始方向为确定
    #1 上升波段 寻找最高点
    #-1 下降波段，寻找最低点
    direction=0
    highest_price=float(df.at[0,'close'])
    lowest_price=float(df.at[0,'close'])
    for i in range(1,len(df)):
        close_price=float(df.at[i,'close'])
        if direction==0:
            highest_price=max(highest_price,close_price)
            lowest_price=min(lowest_price,close_price)
            rise_from_low=close_price/lowest_price-1
            fall_from_high=close_price/highest_price-1
            if rise_from_low>=zigzag_rate:
                df.at[i,'zigzag_buy_signal']=True
                direction=1
                highest_price=close_price
            elif fall_from_high<=-zigzag_rate:
                direction=-1
                lowest_price=close_price
        elif direction==1:
            highest_price=max(highest_price,close_price)
            fall_from_high=close_price/highest_price-1
            if fall_from_high<=-zigzag_rate:
                direction=-1
                lowest_price=close_price
        elif direction == -1:
            lowest_price = min(lowest_price, close_price)
            rise_from_low = close_price / lowest_price - 1
            if rise_from_low >= zigzag_rate:
                df.at[i, "zigzag_buy_signal"] = True
                direction = 1
                highest_price = close_price
#=========组合信号===========
    #最近的窗口内是否出现过低点确认信号
    df['zigzag_low_signal']=df['zigzag_buy_signal'].rolling(setup_valid_days,min_periods=1).max().astype(bool)
    #低点确认后，MACD满足零轴下方强势条件
    df['long_setup_signal']=df['zigzag_low_signal']&df['macd_low_strong']
    #准备阶段红折线出现后附图MACD强势可以持续即可
    df['long_setup_recent']=df['long_setup_signal'].rolling(setup_valid_days,min_periods=1).max().astype(bool)
    # 保留原来的组合买入条件
    df["buy_signal"] = (df["long_setup_recent"]& df["macd_buy_recent"]& df["bb_buy_signal"])
    #=====次日高开确认
    #当前日期的前一天的收盘价
    df['previous_close']=df['close'].shift(1)
    #昨天收盘是否产生买入卖出信号
    yesterday_buy_signal=df['buy_signal'].shift(1,fill_value=False)
    yesterday_sell_signal=df['sell_signal'].shift(1,fill_value=False)
    #昨天有收盘信号并且高开才买入
    df['buy_signal_for_today']=yesterday_buy_signal&(df['open']>df['previous_close'])
    #卖出
    df['sell_signal_for_today']=yesterday_sell_signal&(df['open']<df['previous_close'])
    # 删除数据不足的行
    df = df.dropna(
        subset=["BB_middle", "BB_upper", "BB_lower"]
    ).copy()
    df=df.set_index('date')
    return df
#=========准备所有股票的数据===========
stock_data={}
try:
    for stock_code in stock_list:
        stock_df = prepare_stock_data(stock_code)
        stock_data[stock_code]=stock_df#把数据保存到字典中
    print(
        f"数据准备完成：{stock_code}, "
        f"共{len(stock_df)}行"
    )
finally:
    engine.dispose()
#========统一回测==========
#找到所有股票共同覆盖的日期范围
start_date=max(df.index.min() for df in stock_data.values())
#找到最晚的日期
end_date = min(df.index.max() for df in stock_data.values())
#检查日期是否有效
if start_date>end_date:
    raise ValueError('这写股票没有共同的数据覆盖')
#收集回测日期
all_dates=set()
for stock_df in stock_data.values():
    #收集共同区间内出现的日期
    dates=stock_df.loc[start_date:end_date].index
    all_dates.update(dates)
#日期去重后，从早到晚排列
all_dates=sorted(all_dates)
if not all_dates:
    raise ValueError('回测区间内没有可交易的日期')
#========样本划分内和样本外=========
#用百分之70的日期作为样本内的数据
split_index=int(len(all_dates)*0.7)
in_sample_end=all_dates[split_index-1]
out_sample_start=all_dates[split_index]
in_sample_dates=[]
for current_date in all_dates:
    if current_date<=in_sample_end:
        in_sample_dates.append(current_date)
# 样本外日期
out_of_sample_dates = [
        current_date
        for current_date in all_dates
        if current_date >= out_sample_start
]
#=======统一账户========
def run_portfolio_backtest(test_dates,period_name):
    cash=initial_capital
    #持仓
    positions={}
    #保存持仓股票最近已知的收盘价
    last_price={}
    #记录交易
    trade_records=[]
    #保存每日账户资产
    portfolio_records=[]
    #每次建仓后的股票预算
    position_budget=initial_capital*position_size_rate
    #=========按日期执行组合交易========
    for current_date in test_dates:
        #当前日期实际存在的行情
        today_rows={}
        for stock_code in stock_list:
            stock_df = stock_data[stock_code]
            if current_date in stock_df.index:
                today_rows[stock_code]=stock_df.loc[current_date]
        #记录今天卖出的股票，避免当天又买回来
        sold_today=set()
        #=======遍历当前持仓
        for stock_code in list(positions):
            if stock_code not in today_rows:
                continue
            #取出行情跟持仓信息
            row=today_rows[stock_code]
            holding=positions[stock_code]
            #当天没有卖出信息
            if not bool(row['sell_signal_for_today']):
                continue
            #买入当日不允许卖出
            if current_date<=holding['buy_date']:
                continue
            #取得当天的开盘价
            sell_price=float(row['open'])
            #检查卖出价是否有效
            if sell_price<=0:
                continue
            #取出持有股数
            shares=holding['shares']
            #计算卖出金额
            amount=shares*sell_price
            fee=amount*fee_rate
            #卖出后现金增加
            cash +=amount-fee
            #保存卖出记录
            trade_records.append(
                {
                    "date": current_date,
                    'code': stock_code,
                    'name':row['name'],
                    'action': 'sell',
                    'price': sell_price,
                    'shares': shares,
                    'amount': amount,
                    'fee': fee,
                    'cash_after': cash,
                }
            )
            # 删除这只股票的持仓
            del positions[stock_code]
            sold_today.add(stock_code)
    #========再检查有没有需要买入的股票=========
        for stock_code in stock_list:
            if len(positions)>=max_position:
                break
            #已经持有就不重复买入
            if stock_code in positions:
                continue
            #今天刚刚卖出，今天不再买入
            if stock_code in sold_today:
                continue
            #今天没有行情
            if stock_code not in today_rows:
                continue
            row=today_rows[stock_code]
            #判断今天有信号是否高开并且可以买入
            if not bool(row['buy_signal_for_today']):
                continue
            #确定买入价格
            buy_price=float(row['open'])
            #检查买入价格
            if buy_price<=0:
                continue
            #计算可以买多少
            budget=min(position_budget,cash)
            #计算购买一手股票需要的总资金
            one_lot_cost=(buy_price*lot_size*(1+fee_rate))
            #只能购买完整的手数
            lots=int(budget//one_lot_cost)
            #连一手都买不起
            if lots<1:
                continue
            shares=lots*lot_size
            amount=shares*buy_price
            fee=amount*fee_rate
            total_cost=amount+fee
            #扣除买入成本
            cash -= total_cost
            positions[stock_code]={
                'shares': shares,
                'buy_date': current_date,
            }
            #保存买入记录
            trade_records.append(
                {
                    "date": current_date,
                    'code': stock_code,
                    'name':row['name'],
                    'action': 'buy',
                    'price': buy_price,
                    'shares': shares,
                    'amount': amount,
                    'fee': fee,
                    'cash_after': cash,
                }
            )
            #收盘后更新价格
        for stock_code,row in today_rows.items():
            last_price[stock_code]=float(row['close'])
        stock_value=0.0
        #计算持仓股票的市值
        for stock_code,holding in positions.items():
            #检查有没有价格
            if stock_code not in last_price:
                continue
            close_price=last_price[stock_code]
            stock_value+=(holding['shares']*close_price)
        #计算帐户总资产
        total_value=cash+stock_value
        #保存当天帐户情况
        portfolio_records.append(
            {
                "date": current_date,
                'cash': cash,
                'stock_value': stock_value,
                'total_value': total_value,
                'positions_count': len(positions),
            }
        )
        #=======整理回测结果=========
    portfolio_df=pd.DataFrame(portfolio_records)
    portfolio_df = portfolio_df.set_index("date")
    portfolio_df['equity']=(portfolio_df['total_value']/initial_capital)
    #计算每日收益率
    portfolio_df['daily_return']=(portfolio_df['total_value'].pct_change())
    first_date = portfolio_df.index[0]
    portfolio_df.loc[first_date, "daily_return"] = (
        portfolio_df["total_value"].iloc[0] / initial_capital - 1
    )
    #计算历史最高净值
    portfolio_df['running_max']=(portfolio_df['equity'].cummax().clip(lower=1.0))
    #计算回撤
    portfolio_df['drawdown']=(portfolio_df['equity']/portfolio_df['running_max'])-1
    #计算最终资产和总收益率
    print("当前持仓：", positions)
    print("最近价格：", last_price)

    bad_rows = portfolio_df[
        portfolio_df[
            ["cash", "stock_value", "total_value"]
        ].isna().any(axis=1)
    ]

    print("出现缺失值的账户记录：")
    print(bad_rows)
    final_capital = float(portfolio_df["total_value"].iloc[-1])
    total_return = (final_capital / initial_capital - 1)
    #最大回撤
    max_drawdown = float(portfolio_df["drawdown"].min())
    trading_days = len(portfolio_df)
    #计算年度收益率
    annual_return = ((final_capital / initial_capital)** (252 / trading_days)- 1)
    #平均每日收益率和波动率
    daily_mean = (portfolio_df["daily_return"].mean())
    daily_std = (portfolio_df["daily_return"].std())
    #年度波动率
    annual_volatility = (daily_std * np.sqrt(252))
    #计算夏普比率
    sharpe_ratio = (daily_mean*np.sqrt(252)/daily_std) if daily_std!=0 else 0
    trade_df = pd.DataFrame(
        trade_records,
        columns=[
            "date",
            "code",
            "name",
            "action",
            "price",
            "shares",
            "amount",
            "fee",
            "cash_after",
        ],
    )

    buy_count = int(
        (trade_df["action"] == "buy").sum()
    )

    sell_count = int(
        (trade_df["action"] == "sell").sum()
    )

    total_fees = float(
        trade_df["fee"].sum()
    )

    return {
        "period_name": period_name,
        "final_capital": final_capital,
        "total_return": total_return,
        "max_drawdown": max_drawdown,
        "buy_count": buy_count,
        "sell_count": sell_count,
        "total_fees": total_fees,
    }
in_sample_result = run_portfolio_backtest(
    in_sample_dates,
    "样本内",
)
out_of_sample_result = run_portfolio_backtest(
    out_of_sample_dates,
    "样本外",
)
print(
    f"样本内总收益率："
    f"{in_sample_result['total_return']:.2%}"
)
print(f"样本外总收益率："
      f"{out_of_sample_result['total_return']:.2%}"
)

print("\n========== 样本内和样本外比较 ==========")

print(
    f"样本内最终资金："
    f"{in_sample_result['final_capital']:.2f}元"
)

print(
    f"样本外最终资金："
    f"{out_of_sample_result['final_capital']:.2f}元"
)

print(
    f"样本内总收益率："
    f"{in_sample_result['total_return']:.2%}"
)

print(
    f"样本外总收益率："
    f"{out_of_sample_result['total_return']:.2%}"
)

print(
    f"样本内最大回撤："
    f"{in_sample_result['max_drawdown']:.2%}"
)

print(
    f"样本外最大回撤："
    f"{out_of_sample_result['max_drawdown']:.2%}"
)

print(
    f"样本内买入次数："
    f"{in_sample_result['buy_count']}"
)

print(
    f"样本外买入次数："
    f"{out_of_sample_result['buy_count']}"
)
#=========测试手续费==================================
#保存原来的手续费
original_fee_rate=fee_rate
#准备测试三种手续费
fee_rates=[0,0.0005,0.001]
fee_results=[]
for test_fee_rate in fee_rates:
    fee_rate=test_fee_rate
    #重新回测
    result=run_portfolio_backtest(
        all_dates,f'手续费{test_fee_rate:.4%}',
    )
    fee_results.append({
        'fee_rate': test_fee_rate,
        'total_return': result['total_return'],
        'max_drawdown': result['max_drawdown'],
        'buy_count': result['buy_count'],
        'sell_count': result['sell_count'],
        'total_fees': result['total_fees'],
    })
#恢复原来的手续费
fee_rate=original_fee_rate
#把测试结果变成表格
fee_result_df=pd.DataFrame(fee_results)
# 把小数收益率转换成百分比
fee_result_df["total_return"] = (
    fee_result_df["total_return"] * 100
).round(2)

fee_result_df["max_drawdown"] = (
    fee_result_df["max_drawdown"] * 100
).round(2)

fee_result_df["fee_rate"] = (
    fee_result_df["fee_rate"] * 100
).round(4)
print('\n==========手续费敏感性测试==========')
print(fee_result_df)
#===================测试zigzag参数======================
#保存原来的zigzag参数
original_zigzag_rate=zigzag_rate
#准备测试的参数
zigzag_rates=[0.07,0.08,0.09,0.10,0.11]
#保存每组的测试结果
zigzag_results=[]
for test_zigzag_rate in zigzag_rates:
    zigzag_rate=test_zigzag_rate
    #清空之前的准备好的数据
    stock_data={}
    #重新计算10只股票的指标和信号
    for stock_code in stock_list:
        stock_df=prepare_stock_data(stock_code)
        stock_data[stock_code]=stock_df
    result=run_portfolio_backtest(in_sample_dates,f'zigzag{test_zigzag_rate:.4%}')

    zigzag_results.append(
        {
            "zigzag_rate": test_zigzag_rate,
            "total_return": result["total_return"],
            "max_drawdown": result["max_drawdown"],
            "buy_count": result["buy_count"],
            "sell_count": result["sell_count"],
        }
    )
    # 恢复原来的ZigZag参数
    zigzag_rate = original_zigzag_rate

    # 检查参数有没有成功恢复
    print("恢复后的ZigZag参数：", zigzag_rate)

    # 清空最后一次11%参数生成的数据
    stock_data = {}

    # 使用原来的9%参数重新计算股票数据
    for stock_code in stock_list:
        stock_df = prepare_stock_data(stock_code)
        stock_data[stock_code] = stock_df
    # 把测试结果转换成表格
    zigzag_result_df= pd.DataFrame(
    zigzag_results
        )
    # 转换为百分比显示
    zigzag_result_df["zigzag_rate"] = (
            zigzag_result_df["zigzag_rate"] * 100
    ).round(2)

    zigzag_result_df["total_return"] = (
            zigzag_result_df["total_return"] * 100
    ).round(2)

    zigzag_result_df["max_drawdown"] = (
            zigzag_result_df["max_drawdown"] * 100
    ).round(2)
print('\n======zigzag参数稳定性测试=========')
print(zigzag_result_df)
#=========测试信号有效期========
#保存原来的参数
# ==================== 第14课第三节：测试准备信号有效期 ====================

# 保存原来的参数
original_setup_valid_days = setup_valid_days
# 准备测试三个有效期
setup_days_list = [5,10,15,]
# 保存每次测试的结果
setup_results = []
for test_setup_days in setup_days_list:
    # 使用当前测试的有效期
    setup_valid_days = test_setup_days
    # 清空按照旧参数计算好的股票数据
    stock_data = {}
    # 按照新参数重新计算10只股票
    for stock_code in stock_list:
        stock_df = prepare_stock_data(stock_code)
        stock_data[stock_code] = stock_df
    # 只使用样本内数据回测
    result = run_portfolio_backtest(
        in_sample_dates,
        f"准备信号有效期 {test_setup_days}天",
    )
    # 保存当前参数的测试结果
    setup_results.append(
        {
            "setup_valid_days": test_setup_days,
            "total_return": result["total_return"],
            "max_drawdown": result["max_drawdown"],
            "buy_count": result["buy_count"],
            "sell_count": result["sell_count"],
        }
    )
# 恢复原来的参数
setup_valid_days = original_setup_valid_days
# 清空测试参数对应的数据
stock_data = {}
# 使用原参数重新准备股票数据
for stock_code in stock_list:
    stock_df = prepare_stock_data(stock_code)
    stock_data[stock_code] = stock_df
# 把测试结果转换为表格
setup_result_df = pd.DataFrame(
    setup_results
)
# 把收益率转换成百分比
setup_result_df["total_return"] = (
    setup_result_df["total_return"] * 100
).round(2)
# 把最大回撤转换成百分比
setup_result_df["max_drawdown"] = (
    setup_result_df["max_drawdown"] * 100
).round(2)
print(
    "\n========== 准备信号有效期测试 =========="
)
print(
    setup_result_df.to_string(
        index=False
    )
)
# ==================== 测试MACD金叉有效期 ====================

# 保存原来的MACD有效期
original_macd_valid_days = macd_valid_days
# 准备测试的参数
macd_days_list = [5,10,15,]
# 保存每次测试结果
macd_results = []
for test_macd_days in macd_days_list:
    # 使用当前测试参数
    macd_valid_days = test_macd_days
    # 清空按照旧参数计算的数据
    stock_data = {}
    # 重新计算10只股票的指标和信号
    for stock_code in stock_list:
        stock_df = prepare_stock_data(stock_code)
        stock_data[stock_code] = stock_df
    # 只使用样本内日期回测
    result = run_portfolio_backtest(
        in_sample_dates,
        f"MACD有效期 {test_macd_days}天",
    )
    # 保存当前参数的测试结果
    macd_results.append(
        {
            "macd_valid_days": test_macd_days,
            "total_return": result["total_return"],
            "max_drawdown": result["max_drawdown"],
            "buy_count": result["buy_count"],
            "sell_count": result["sell_count"],
        }
    )
# 恢复原来的MACD有效期
macd_valid_days = original_macd_valid_days
# 清空最后一组参数对应的数据
stock_data = {}
# 按原来的参数重新准备股票数据
for stock_code in stock_list:
    stock_df = prepare_stock_data(stock_code)
    stock_data[stock_code] = stock_df
# 把测试结果转换成表格
macd_result_df = pd.DataFrame(
    macd_results
)
# 将总收益率转换为百分比
macd_result_df["total_return"] = (
    macd_result_df["total_return"] * 100
).round(2)
# 将最大回撤转换为百分比
macd_result_df["max_drawdown"] = (
    macd_result_df["max_drawdown"] * 100
).round(2)
print(
    "\n========== MACD金叉有效期测试 =========="
)
print(
    macd_result_df.to_string(
        index=False
    )
)
# ==================== 测试布林带宽度 ====================
# 保存原来的布林带参数
original_bb_std_multiple = bb_std_multiple
# 准备测试的布林带宽度
bb_multiple_list = [0.3,0.5,0.7,1.0,]
# 保存每一次测试结果
bb_results = []
for test_bb_multiple in bb_multiple_list:
    # 使用当前测试的布林带参数
    bb_std_multiple = test_bb_multiple
    # 清空按照旧参数计算的数据
    stock_data = {}
    # 重新计算10只股票的数据和信号
    for stock_code in stock_list:
        stock_df = prepare_stock_data(stock_code)
        stock_data[stock_code] = stock_df
    # 只在样本内测试参数
    result = run_portfolio_backtest(
        in_sample_dates,
        f"布林带宽度 {test_bb_multiple}",
    )
    # 保存本次测试结果
    bb_results.append(
        {
            "bb_std_multiple": test_bb_multiple,
            "total_return": result["total_return"],
            "max_drawdown": result["max_drawdown"],
            "buy_count": result["buy_count"],
            "sell_count": result["sell_count"],
        }
    )
# 恢复原来的布林带参数
bb_std_multiple = original_bb_std_multiple
# 清空最后一次测试对应的数据
stock_data = {}
# 按照原参数重新计算股票数据
for stock_code in stock_list:
    stock_df = prepare_stock_data(stock_code)
    stock_data[stock_code] = stock_df
# 把测试结果转换成表格
bb_result_df = pd.DataFrame(
    bb_results
)
# 把收益率转换成百分比
bb_result_df["total_return"] = (
    bb_result_df["total_return"] * 100
).round(2)
# 把最大回撤转换成百分比
bb_result_df["max_drawdown"] = (
    bb_result_df["max_drawdown"] * 100
).round(2)
print(
    "\n========== 布林带宽度测试 =========="
)
print(
    bb_result_df.to_string(
        index=False
    )
)
# ==================== 比较原参数和候选参数 ====================
# ---------- 1. 测试原参数组合 ----------
zigzag_rate = 0.09
setup_valid_days = 10
macd_valid_days = 10
bb_std_multiple = 0.5
# 清除之前参数对应的数据
stock_data = {}
# 使用原参数重新计算10只股票
for stock_code in stock_list:
    stock_df = prepare_stock_data(stock_code)
    stock_data[stock_code] = stock_df
# 回测原参数组合
original_result = run_portfolio_backtest(
    in_sample_dates,
    "原参数组合",
)
# ---------- 2. 测试候选参数组合 ----------
zigzag_rate = 0.09
setup_valid_days = 5
macd_valid_days = 5
bb_std_multiple = 0.5
# 清除原参数计算的数据
stock_data = {}
# 使用候选参数重新计算10只股票
for stock_code in stock_list:
    stock_df = prepare_stock_data(stock_code)
    stock_data[stock_code] = stock_df
# 回测候选参数组合
candidate_result = run_portfolio_backtest(
    in_sample_dates,
    "候选参数组合",
)
# ---------- 3. 整理比较结果 ----------
parameter_comparison = [
    {
        "parameter_set": "原参数",
        "zigzag_rate": 0.09,
        "setup_valid_days": 10,
        "macd_valid_days": 10,
        "bb_std_multiple": 0.5,
        "total_return": original_result["total_return"],
        "max_drawdown": original_result["max_drawdown"],
        "buy_count": original_result["buy_count"],
        "sell_count": original_result["sell_count"],
    },
    {
        "parameter_set": "候选参数",
        "zigzag_rate": 0.09,
        "setup_valid_days": 5,
        "macd_valid_days": 5,
        "bb_std_multiple": 0.5,
        "total_return": candidate_result["total_return"],
        "max_drawdown": candidate_result["max_drawdown"],
        "buy_count": candidate_result["buy_count"],
        "sell_count": candidate_result["sell_count"],
    },
]
comparison_df = pd.DataFrame(
    parameter_comparison
)
# 收益率转换成百分比
comparison_df["total_return"] = (
    comparison_df["total_return"] * 100
).round(2)
# 最大回撤转换成百分比
comparison_df["max_drawdown"] = (
    comparison_df["max_drawdown"] * 100
).round(2)
print(
    "\n========== 参数组合样本内比较 =========="
)
print(
    comparison_df.to_string(
        index=False
    )
)
# ---------- 4. 恢复原参数 ----------
zigzag_rate = 0.09
setup_valid_days = 10
macd_valid_days = 10
bb_std_multiple = 0.5
stock_data = {}
for stock_code in stock_list:
    stock_df = prepare_stock_data(stock_code)
    stock_data[stock_code] = stock_df
# ==================== 参数组合样本外验证 ====================

# ---------- 1. 原参数的样本外回测 ----------
zigzag_rate = 0.09
setup_valid_days = 10
macd_valid_days = 10
bb_std_multiple = 0.5

# 清空原来的股票数据
stock_data = {}

# 使用原参数重新计算信号
for stock_code in stock_list:
    stock_df = prepare_stock_data(stock_code)
    stock_data[stock_code] = stock_df
print("\n原参数样本外测试：")
print("zigzag_rate =", zigzag_rate)
print("setup_valid_days =", setup_valid_days)
print("macd_valid_days =", macd_valid_days)
print("bb_std_multiple =", bb_std_multiple)
print("样本外开始日期 =", out_of_sample_dates[0])
print("样本外结束日期 =", out_of_sample_dates[-1])
# 使用样本外日期回测
original_out_result = run_portfolio_backtest(
    out_of_sample_dates,
    "原参数样本外",
)
# ---------- 2. 候选参数的样本外回测 ----------
zigzag_rate = 0.09
setup_valid_days = 5
macd_valid_days = 5
bb_std_multiple = 0.5
# 清空原参数对应的数据
stock_data = {}
# 使用候选参数重新计算信号
for stock_code in stock_list:
    stock_df = prepare_stock_data(stock_code)
    stock_data[stock_code] = stock_df
print("\n原参数样本外测试：")
print("zigzag_rate =", zigzag_rate)
print("setup_valid_days =", setup_valid_days)
print("macd_valid_days =", macd_valid_days)
print("bb_std_multiple =", bb_std_multiple)
print("样本外开始日期 =", out_of_sample_dates[0])
print("样本外结束日期 =", out_of_sample_dates[-1])
# 使用样本外日期回测
candidate_out_result = run_portfolio_backtest(
    out_of_sample_dates,
    "候选参数样本外",
)

# ---------- 3. 汇总样本内和样本外结果 ----------
final_comparison = [
    {
        "parameter_set": "原参数",
        "in_sample_return": original_result["total_return"],
        "out_sample_return": original_out_result["total_return"],
        "in_sample_drawdown": original_result["max_drawdown"],
        "out_sample_drawdown": original_out_result["max_drawdown"],
        "in_sample_buys": original_result["buy_count"],
        "out_sample_buys": original_out_result["buy_count"],
    },
    {
        "parameter_set": "候选参数",
        "in_sample_return": candidate_result["total_return"],
        "out_sample_return": candidate_out_result["total_return"],
        "in_sample_drawdown": candidate_result["max_drawdown"],
        "out_sample_drawdown": candidate_out_result["max_drawdown"],
        "in_sample_buys": candidate_result["buy_count"],
        "out_sample_buys": candidate_out_result["buy_count"],
    },
]
final_comparison_df = pd.DataFrame(
    final_comparison
)
# 收益率转换成百分比
final_comparison_df["in_sample_return"] = (
    final_comparison_df["in_sample_return"] * 100
).round(2)
final_comparison_df["out_sample_return"] = (
    final_comparison_df["out_sample_return"] * 100
).round(2)
# 最大回撤转换成百分比
final_comparison_df["in_sample_drawdown"] = (
    final_comparison_df["in_sample_drawdown"] * 100
).round(2)
final_comparison_df["out_sample_drawdown"] = (
    final_comparison_df["out_sample_drawdown"] * 100
).round(2)
print(
    "\n========== 参数组合最终比较 =========="
)
print(
    final_comparison_df.to_string(
        index=False
    )
)

# ---------- 4. 恢复原参数 ----------
zigzag_rate = 0.09
setup_valid_days = 10
macd_valid_days = 10
bb_std_multiple = 0.5
stock_data = {}
for stock_code in stock_list:
    stock_df = prepare_stock_data(stock_code)
    stock_data[stock_code] = stock_df
