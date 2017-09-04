#!/usr/bin/python
# -*- coding: utf-8 -*-

from huobi.Util import *
from huobi import HuobiService
import sys, time, datetime
import numpy as np
import talib

COINTYPE_BTC = 1
COINTYPE_LTC = 2
MIN_UNIT_BTC = 0.0001
MIN_UNIT_LTC = 0.0001

def doWork():
    period_window = 14
    standard_deviation_range = 2
    bbands_opt_width_m = 60
    prices = np.array(HuobiService.get4hHistoryPrice(COINTYPE_LTC, period_window + bbands_opt_width_m), dtype=float)
    if len(prices) < period_window + bbands_opt_width_m:
        print("bar的数量不足，等待下一根bar...")
        return
    upper, middle, lower = talib.BBANDS(prices, timeperiod=period_window, nbdevup=standard_deviation_range, nbdevdn=standard_deviation_range, matype=talib.MA_Type.SMA)
    current_price = HuobiService.getCurrentPrice(COINTYPE_LTC)
    print("当前价格为：%s，上轨为：%s，下轨为：%s" % (current_price, upper[-1], lower[-1]))
    if current_price < lower[-1]:
        print("价格穿越下轨，产生卖出信号")
        account_info = HuobiService.getAccountInfo(ACCOUNT_INFO)
        if float(account_info['available_ltc_display']) > MIN_UNIT_LTC:
            print("正在卖出，卖出数量为%s" % account_info['available_ltc_display'].encode("utf-8"))
            print HuobiService.sellMarket(COINTYPE_LTC, account_info['available_ltc_display'], None, None, SELL_MARKET)
        else:
            print("仓位不足，无法卖出")
    elif current_price > upper[-1]:
        print("价格穿越上轨，产生买入信号")
        account_info = HuobiService.getAccountInfo(ACCOUNT_INFO)
        if float(account_info['available_cny_display']) > MIN_UNIT_LTC * current_price:
            print("正在买入，下单金额为%s元" % account_info['available_cny_display'].encode("utf-8"))
            print HuobiService.buyMarket(COINTYPE_LTC, account_info['available_cny_display'], None, None, BUY_MARKET)
        else:
            print("现金不足，无法下单")
    else:
        print("无交易信号，进入下一根bar")

def waitTime():
    current_time = datetime.datetime.now()
    wait_time = current_time + datetime.timedelta(hours = 4)
    if current_time.hour >= 0 and current_time.hour < 4:
        wait_time = wait_time.replace(hour = 4, minute = 0, second = 10, microsecond = 0)
    elif current_time.hour >= 4 and current_time.hour < 8:
        wait_time = wait_time.replace(hour = 8, minute = 0, second = 10, microsecond = 0)
    elif current_time.hour >= 8 and current_time.hour < 12:
        wait_time = wait_time.replace(hour = 12, minute = 0, second = 10, microsecond = 0)
    elif current_time.hour >= 12 and current_time.hour < 16:
        wait_time = wait_time.replace(hour = 16, minute = 0, second = 10, microsecond = 0)
    elif current_time.hour >= 16 and current_time.hour < 20:
        wait_time = wait_time.replace(hour = 20, minute = 0, second = 10, microsecond = 0)
    else:
        wait_time = wait_time.replace(hour = 0, minute = 0, second = 10, microsecond = 0)
    print("当前时间：%s" % current_time.strftime("%Y-%m-%d %H:%M:%S"))
    print("将于%s开始运行" % wait_time.strftime("%Y-%m-%d %H:%M:%S"))
    sys.stdout.flush()
    time.sleep((wait_time - current_time).seconds)

if __name__ == "__main__":
    while True:
        waitTime()
        try:
            doWork()
        except:
            print("发生异常")
