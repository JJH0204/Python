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

def driver_init(config):
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