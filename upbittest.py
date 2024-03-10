# UPbit test code
import pyupbit

# datafram type
# df = pyupbit.get_ohlcv("KRW-BTC", count=7)
# print(df)

# print(pyupbit.get_tickers(fiat="KRW"))

print(pyupbit.get_current_price("KRW-BTC"))

print(pyupbit.get_current_price(["KRW-BTC", "KRW-ETH"]))