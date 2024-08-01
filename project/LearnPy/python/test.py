# -*- coding: utf-8 -*-
import pyupbit
import json
import requests
import time
from datetime import datetime

class manageJson:
    def __init__(self) -> None:
        pass

    # Load result_queue from a file when the program starts
    def load_result_queue():
        try:
            with open('result_queue.json', 'r') as f:
                result_queue = json.load(f)
                for order in list(result_queue):
                    print("road :",order['market'])
        except FileNotFoundError:
            result_queue = []
        return result_queue

    # Save result_queue to a file
    def save_result_queue(result_queue):
        with open('result_queue.json', 'w') as f:
            json.dump(result_queue, f)

    def load_counters():
        try:
            with open('counters.json', 'r') as f:
                counters = json.load(f)
                win_count = counters['win_count']
                lose_count = counters['lose_count']
                result_KRW = counters['result_KRW']
        except FileNotFoundError:
            win_count = 0
            lose_count = 0
            result_KRW = 0
        return win_count, lose_count, result_KRW # 반환 값을 한번에 여러 개로 반환할 수 있다

    # Save win_count, lose_count, and result_KRW to a file
    def save_counters(win_count, lose_count, result_KRW):
        with open('counters.json', 'w') as f:
            json.dump({'win_count': win_count, 'lose_count': lose_count, 'result_KRW': result_KRW}, f)

def loginUpbit():
    accesskey = "아이디" 
    secretkey = "암호"   
    upbit = pyupbit.Upbit(accesskey, secretkey)

#원화 마켓 코인 리스트를 불러오는 함수
def fetch_krw_coin_list():
    time.sleep(0.5)
    tickers = pyupbit.get_tickers(fiat="KRW")
    return tickers

def check_chart_pattern(coin):
    try:
        time.sleep(0.25)
        df = pyupbit.get_ohlcv(coin, interval="minute240", count=5)
        if df is None:
            return False
        if df['close'].iloc[-4] > df['open'].iloc[-4] and \
           df['close'].iloc[-3] < df['open'].iloc[-3] and \
           df['close'].iloc[-2] > df['open'].iloc[-2] and \
           df['close'].iloc[-3] > df['open'].iloc[-4] and \
           df['close'].iloc[-2] > df['open'].iloc[-3] and \
           df['close'].iloc[-2] > df['close'].iloc[-4]:
            return True
    except Exception as e:
        print(f"Error checking chart pattern for {coin}: {e}")
    return False

    
#코인 구매 함수
def buy_coin(coin, buy_amount):
    try:
        time.sleep(0.5)
        result = upbit.buy_market_order(coin, buy_amount)
        order_detail = upbit.get_order(result['uuid'])
        while order_detail['state'] not in ['cancel', 'done']:  # 주문이 취소되거나 완료될 때까지
            time.sleep(0.5)  # 1초마다
            order_detail = upbit.get_order(result['uuid'])  # 주문 상세 정보를 업데이트합니다.
        return order_detail  # 완료된 주문 상세 정보를 반환합니다.
    except Exception as e:
        print(f"Error buying coin {coin}: {e}")
        return None

def sell_coin(coin, sell_amount):
    try:
        time.sleep(0.5)
        result = upbit.sell_market_order(coin, sell_amount)
        order_detail = upbit.get_order(result['uuid'])
        while order_detail['state'] not in ['cancel', 'done']:  # 주문이 취소되거나 완료될 때까지
            time.sleep(0.5)  # 1초마다
            order_detail = upbit.get_order(result['uuid'])  # 주문 상세 정보를 업데이트합니다.
        return order_detail  # 완료된 주문 상세 정보를 반환합니다.
    except Exception as e:
        print(f"Error selling coin {coin}: {e}")
        return None

def get_current_price_with_retry(market, max_retries=3):
    for i in range(max_retries):
        try:
            time.sleep(0.7)
            return pyupbit.get_current_price(market)
        except requests.exceptions.SSLError as e:
            print(f"SSL Error on try {i+1}: {e}")
            time.sleep(3)  # Wait for 5 seconds before retrying
        except requests.exceptions.ConnectionError as e:
            print(f"Connection Error on try {i+1}: {e}")
            time.sleep(3)  # Wait for 5 seconds before retrying
    return None  # Return None if all retries failed

def buyProcess(result_queue, buy_amount, executed):
    # ---------------------구매 로직---------------------
    current_minute = datetime.now().minute  # 현재 시간의 분 저장
    current_hour = datetime.now().hour      # 현재 시간의 시간 저장
    if current_minute == 4 and current_hour in [1, 5, 9, 13, 17, 21]:   # 원하는 시간(시,분)이 되었는지 검사
        if not executed:
            coin_list = fetch_krw_coin_list()
            for coin in coin_list:
                if coin == "KRW-USDT":
                    continue
                if check_chart_pattern(coin):
                    time.sleep(0.25)
                    balance = upbit.get_balance("KRW")
                    if balance > buy_amount:
                        result = buy_coin(coin, buy_amount)
                        if result:
                            result_queue.append(result)
                            save_result_queue(result_queue)
                            print("buy coin :", str(result['trades'][0]['market']), " price :", str(result['trades'][0]['price']))
                    else:
                        break
            print("end order")
            executed = True
    else:
        executed = False
    
    return executed

def sellProcess(result_queue, win_count, lose_count, result_KRW):
    # ---------------------판매 로직---------------------
    if result_queue:
        for order in list(result_queue):
            # 주문 상세 정보 조회
            current_price = get_current_price_with_retry(order['market'])
            if current_price is None:
                print("Failed to get current price after maximum retries. Skipping this order.")
                continue
            current_trades = order['trades']
            profit = (current_price - float(current_trades[0]['price'])) / float(current_trades[0]['price']) * 100
            if profit >= 2.45 or profit <= -4.8:
                if profit >= 2.45:
                    win_count += 1
                elif profit <= -4.8:
                    lose_count += 1
                sell_result = sell_coin(order['market'], float(order['executed_volume']))
                if sell_result:
                    result_queue.remove(order)
                    save_result_queue(result_queue)
                    coin_profit = (float(sell_result['trades'][0]['price']) - float(current_trades[0]['price'])) * float(order['executed_volume'])
                    result_KRW += coin_profit
                    save_counters(win_count, lose_count, result_KRW)
                    print("sell :", str(sell_result['market']), " coin_profit :", coin_profit)
                    print("result_KRW : ", result_KRW)
                    print("win :", str(win_count), "lose :", str(lose_count), "ratio : ", str(win_count / (lose_count + win_count) * 100), "%")
    else:
        time.sleep(1)  # 60초 마다 반복 실행

#메인 트레이딩 루프
def mainProcess():
    result_queue = load_result_queue()                  # 과거 트레이딩 결과값 불러옴
    win_count, lose_count, result_KRW = load_counters() # 과거 트레이딩 승률과 수익률 불러옴
    buy_amount = 130000     # 구매량 조절 변수
    executed = False        # 루프 횟수 조절 ()

    while True:
        try:
            executed = buyProcess(result_queue, buy_amount, executed)   # 구매 프로세스

            sellProcess(result_queue, win_count, lose_count, result_KRW)    # 판매 프로세스
        
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(1)

if __name__ == '__main__':
    loginUpbit()
    mainProcess()
