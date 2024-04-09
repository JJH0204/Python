from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By  # 요소를 찾는 방법을 지정하는 데 사용됩니다.
from selenium.webdriver.common.keys import Keys  # 키보드 키를 사용하기 위한 모듈입니다.
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select


import urllib.parse

import os
import time
import random

from py_Json import json

def readJson():
    with open('project/AutoTicketing/login_config.json', 'r') as file:        # json 로그인 정보 가져오기
        config = json.load(file)
    return config

def initDriver(config):
    # 브라우저 꺼짐 방지
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    # 크롬 드라이버 위치 설정
    driver_path = config['driver_path']
    service = Service(executable_path=driver_path)

    # 드라이버 생성
    driver = webdriver.Chrome(options=chrome_options, service=service)

    # 브라우저 사이즈
    driver.set_window_size(config['window_size']['width'], config['window_size']['length'])

    # 웹페이지가 로드될 때까지 2초를 대기
    driver.implicitly_wait(time_to_wait=2)  

    # 인터파크 접속
    driver.get(url=config['search_Site'])
    return driver

def loginInterpark(driver, pageLodeWait, config):
    # Step-2: 로그인
    login_link =pageLodeWait.until(EC.presence_of_element_located((By.XPATH, "//ul[contains(@class, 'header_myMenu__h7hl8')]//a[@href='javascript:;']")))
    login_link.click()

    # 웹페이지가 로드될 때까지 2초를 대기
    driver.implicitly_wait(time_to_wait=2)  

    # json에 정의한 로그인 정보를 가져와 로그인 시도
    login_type = config['login_type']       

    # Step-2.1: 일반 로그인
    if login_type == "local":
        username_input = pageLodeWait.until(EC.presence_of_element_located((By.ID, "userId")))
        password_input = pageLodeWait.until(EC.presence_of_element_located((By.ID, "userPwd")))

        username_input.send_keys(config['credentials']['id'])
        password_input.send_keys(config['credentials']['password'])
        password_input.send_keys(Keys.ENTER)

    # Step-2.2: SNS 로그인 (카카오)
    elif login_type == "kakao":
        kakaoLogin_link = pageLodeWait.until(EC.presence_of_element_located((By.CLASS_NAME, "kakao")))
        kakaoLogin_link.click()
        
        username_field = pageLodeWait.until(EC.presence_of_element_located((By.ID, "loginId--1")))
        username_field.send_keys(config['social']['kakao']['id'])
        
        password_field = pageLodeWait.until(EC.presence_of_element_located((By.ID, "password--2")))
        password_field.send_keys(config['social']['kakao']['password'])
        
        kakaoLogin_button = pageLodeWait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn_g.highlight.submit")))
        kakaoLogin_button.click()

        continue_button = pageLodeWait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn_agree")))
        continue_button.click()

    # Step-2.3: SNS 로그인 (네이버)
    # elif login_type == "naver":
    #     naverLogin_link = driver.find_element(By.CLASS_NAME, "naver")
    #     naverLogin_link.click()

    # Step-2.3: SNS 로그인 (애플)
    # elif login_type == "apple":
    #     appleLogin_link = driver.find_element(By.CLASS_NAME, "apple")
    #     appleLogin_link.click()
    
    # 웹페이지가 로드될 때까지 2초를 대기
    driver.implicitly_wait(time_to_wait=2)
    
    return

def searchTicket(driver, pageLodeWait, config):
    # Step-3: 공연 검색
    search_query = config['search_Key']
    search_Type = config['search_Type']
    if search_Type == "search_URL":
        # 검색어가 포함된 URL로 직접 이동 
        encoded_query = urllib.parse.quote(search_query)  # 검색어를 URL 인코딩합니다.
        url = f"https://isearch.interpark.com/result?q={encoded_query}"
        driver.get(url)
        # 위 방법은 완벽하지 않아 추후에 추가 작업이 발생할 수 있다.
    elif search_Type == "search_field":
        # 검색 입력 필드 선택하여 팝업 활성화
        search_field_main = pageLodeWait.until(EC.element_to_be_clickable((By.ID, "inputSearch")))
        search_field_main.click()

        # 팝업 내 검색 입력 필드가 활성화될 때까지 대기
        search_field_popup = pageLodeWait.until(EC.element_to_be_clickable((By.ID, "input_autoKeyword")))

		# 검색 입력 필드에 검색어 입력
        search_field_popup.send_keys(search_query)
        search_field_popup.send_keys(Keys.ENTER)

    # 웹페이지가 로드될 때까지 2초를 대기
    driver.implicitly_wait(time_to_wait=2)

    # 첫번째 페이지를 선택한다.
    links = pageLodeWait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ticketContent"]/div[2]/ul/li/a')))
    links.click()

    # 웹페이지가 로드될 때까지 2초를 대기
    driver.implicitly_wait(time_to_wait=2)

    print(driver.window_handles)
    driver.switch_to.window(driver.window_handles[-1])

    return

# 좌석 탐색
def select(driver, pageLodeWait, config):
    # 페이지가 완전히 로드될 때까지 기다림 (필요에 따라 조정)
    time.sleep(5)

    print(driver.window_handles)
    driver.switch_to.window(driver.window_handles[-1])

    # 좌석 요소를 모두 찾기 (예: 'stySeat' 클래스를 가진 모든 요소)
    # TODO: 자리 찾아서 선택
    seats = driver.find_element(By.XPATH,'//*[@id="Seats"]')

    # 선택할 인원 수 설정
    number_of_seats_to_select = config['number_of_seats_to_select']

    # 선택된 좌석 수를 추적하기 위한 카운터
    selected_seats_count = 0

    # 모든 좌석을 순회하면서 클릭
    for seat in seats:
        try:
            if selected_seats_count < number_of_seats_to_select:
                # 좌석을 클릭
                seat.click()
                selected_seats_count += 1
                time.sleep(1)  # 클릭 사이에 적절한 시간 간격 설정
            else:
                # 원하는 인원 수만큼 좌석을 선택했으므로 반복 종료
                break
        except:
            # 클릭할 수 없는 요소(예: 이미 선택된 좌석)의 경우 예외 처리
            continue
    
    # 웹페이지가 로드될 때까지 2초를 대기
    driver.implicitly_wait(time_to_wait=5)

    # 좌석 모두 선택하면 좌석 선택완료 버튼 누른다.
    select_button = driver.find_element(By.XPATH, '/html/body/form[1]/div/div[1]/div[3]/div/div[4]/a')
    select_button.click()

    return

def ticketingInterpark(driver, pageLodeWait, config):
    # 웹페이지가 로드될 때까지 2초를 대기
    driver.implicitly_wait(time_to_wait=5)

    # 안내 팝업 닫기
    popup_button = driver.find_element(By.XPATH, '//*[@id="popup-prdGuide"]/div/div[3]/div/a')
    popup_button.click()

    # 예매 버튼 누르기
    ticketing_button = driver.find_element(By.XPATH, '//*[@id="productSide"]/div/div[2]/a[1]')
    ticketing_button.click()

    # 웹페이지가 로드될 때까지 2초를 대기
    driver.implicitly_wait(time_to_wait=2)

    # 예매 창으로 이동
    driver.switch_to.window(driver.window_handles[-1])

    # reCAPTCHA 해결까지 대기
    time.sleep(60)

    select(driver, pageLodeWait, config)
    return

def ticketingProcessInterpark():
    # Step-0: Json파일 로드 및 웹 드라이버 실행
    # Step-1: 인터파크 접속
    config = readJson()
    driver = initDriver(config)
    pageLodeWait = WebDriverWait(driver, 30)    # 페이지 로딩 대기 시간
    
    # Step-2: 로그인
    loginInterpark(driver, pageLodeWait, config)

    # Step-3: 공연 검색
    searchTicket(driver, pageLodeWait, config)

    # Step-4: 공연 예매
    ticketingInterpark(driver, pageLodeWait, config)

    driver.quit()

    return

# 이 파이썬 파일을 직접 실행할 때 실행될 main()
if __name__ == "__main__":
    ticketingProcessInterpark()