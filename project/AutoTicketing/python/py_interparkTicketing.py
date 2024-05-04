# 정상 작동 버전 확인
# 파이썬 3.9.9 버전으로 작성된 인터파크 티켓팅 메크로 프로그램 테스트 버전

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

import json
import urllib.parse

import os
import time
# import easyocr

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

    # 원하는 검색어가 포함된 링크를 찾는다.
    links = pageLodeWait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[data-prd-name^='"+search_query+"']")))

    # 웹페이지가 로드될 때까지 2초를 대기
    driver.implicitly_wait(time_to_wait=2)

    # 첫 번째 링크를 선택하여 클릭하거나 새 탭에서 열기
    if links:
        link = links[0].get_attribute('href')
        print(f"Found link: {link}")
        # 새 탭에서 링크 열기
        driver.execute_script("window.open(arguments[0]);", link)
    else:
        print("Link not found.")
    
    # 웹페이지가 로드될 때까지 2초를 대기
    driver.implicitly_wait(time_to_wait=2)

    print(driver.window_handles)
    driver.switch_to.window(driver.window_handles[-1])

    # 웹페이지가 로드될 때까지 2초를 대기
    driver.implicitly_wait(time_to_wait=5)

    return

# 좌석 탐색
def select(driver):
    print(driver.window_handles)
    driver.switch_to.window(driver.window_handles[-1])
    driver.switch_to.frame(driver.find_element(By.XPATH,'//*[@id="ifrmSeat"]'))
    
    # 좌석등급 선택
    #driver.find_element(By.XPATH,'//*[@id="GradeRow"]/td[1]/div/span[2]').click()
    
    while True:
        # 세부 구역 선택
        driver.find_element(By.XPATH,'//*[@id="GradeDetail"]/div/ul/li[1]/a').click()
        
        # 좌석선택 아이프레임으로 이동
        driver.switch_to.frame(driver.find_element(By.XPATH,'//*[@id="ifrmSeatDetail"]'))
        
        # 좌석이 있으면 좌석 선택
        try:
            driver.find_element(By.XPATH,'//*[@id="Seats"]').click()
            # 결제 함수 실행
            # 좌석선택 완료 버튼 클릭
            driver.switch_to.default_content()
            driver.switch_to.frame(driver.find_element(By.XPATH,'//*[@id="ifrmSeat"]'))
            driver.find_element(By.XPATH,'//*[@id="NextStepImage"]').click()
            break
            
        # 좌석이 없으면 다시 조회
        except:
            print('******************************다시선택')
            driver.switch_to.default_content()
            driver.switch_to.frame(driver.find_element(By.XPATH,'//*[@id="ifrmSeat"]'))
            driver.find_element(By.XPATH,'/html/body/form[1]/div/div[1]/div[3]/div/p/a/img').click()
            time.sleep(1)
    return

def ticketingInterpark(driver, pageLodeWait):
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
    time.sleep(300/5)

    select(driver)
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
    ticketingInterpark(driver, pageLodeWait)

    driver.quit()

    return

# 이 파이썬 파일을 직접 실행할 때 실행될 main()
if __name__ == "__main__":
    ticketingProcessInterpark()