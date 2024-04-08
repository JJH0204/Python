from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By  # 요소를 찾는 방법을 지정하는 데 사용됩니다.
from selenium.webdriver.common.keys import Keys  # 키보드 키를 사용하기 위한 모듈입니다.
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import json
import urllib.parse

import os
import time

with open('project/AutoTicketing/login_config.json', 'r') as file:        # json 로그인 정보 가져오기
    config = json.load(file)

# Step-1: 인터파크 접속
driver_path = 'project/AutoTicketing/chromedriver.exe'
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service)

driver.get('https://www.interpark.com/')

# Step-2: 로그인
login_link = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//ul[contains(@class, 'header_myMenu__h7hl8')]//a[@href='javascript:;']")))
login_link.click()

login_type = config['login_type']       # json에 정의한 로그인 정보를 가져와 로그인 시도

# Step-2.1: 일반 로그인
if login_type == "local":
    username_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "userId")))
    password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "userPwd")))

    username_input.send_keys(config['credentials']['username'])
    password_input.send_keys(config['credentials']['password'])
    # 로그인 버튼이 클릭 가능할 때까지 대기
    try:
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btn_login"))
        )
        # 로그인 버튼 클릭
        login_button.click()
    except TimeoutException:
        print("로그인 버튼이 클릭 가능한 상태가 되지 않았습니다.")

# Step-2.2: SNS 로그인 (카카오)
elif login_type == "kakao":
    kakaoLogin_link = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "kakao")))
    kakaoLogin_link.click()
    
    username_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "loginId--1")))
    username_field.send_keys(config['social']['kakao']['id'])
    
    password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password--2")))
    password_field.send_keys(config['social']['kakao']['password'])
    
    kakaoLogin_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn_g.highlight.submit")))
    kakaoLogin_button.click()

    continue_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn_agree")))
    continue_button.click()

# Step-2.3: SNS 로그인 (네이버)
# elif login_type == "naver":
#     naverLogin_link = driver.find_element(By.CLASS_NAME, "naver")
#     naverLogin_link.click()

# Step-2.3: SNS 로그인 (애플)
# elif login_type == "apple":
#     appleLogin_link = driver.find_element(By.CLASS_NAME, "apple")
#     appleLogin_link.click()

# Step-3: 공연 검색
# 검색어가 포함된 URL로 직접 이동 
search_query = "2024 LCK 스프링 결승 진출전 HLE vs T1"
encoded_query = urllib.parse.quote(search_query)  # 검색어를 URL 인코딩합니다.
url = f"https://isearch.interpark.com/result?q={encoded_query}"
driver.get(url)
# 위 방법은 완벽하지 않아 추후에 추가 작업이 발생할 수 있다.


# 추가 작업 수행...
os.system('pause')

driver.quit()