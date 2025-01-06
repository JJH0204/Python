from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import logging

class TicketingBot:
    def __init__(self):
        self.driver = None
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def initialize_driver(self):
        """Initialize Chrome WebDriver with optimized settings"""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.maximize_window()

    def login(self, url, username, password):
        """Login to the ticketing website"""
        try:
            if not self.driver:
                self.initialize_driver()
                
            self.driver.get(url)
            self.logger.info("로그인 페이지로 이동 중...")
            
            # 일반적인 로그인 폼 필드 ID/이름 목록
            username_selectors = [
                (By.ID, "username"),
                (By.ID, "userid"),
                (By.ID, "id"),
                (By.NAME, "username"),
                (By.NAME, "userid"),
                (By.NAME, "id"),
                (By.CSS_SELECTOR, "input[type='text']")
            ]
            
            password_selectors = [
                (By.ID, "password"),
                (By.ID, "pwd"),
                (By.NAME, "password"),
                (By.NAME, "pwd"),
                (By.CSS_SELECTOR, "input[type='password']")
            ]
            
            # 아이디 필드 찾기
            username_field = None
            for selector in username_selectors:
                try:
                    username_field = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located(selector)
                    )
                    self.logger.debug(f"아이디 필드 발견: {selector}")
                    break
                except:
                    continue
                    
            if not username_field:
                raise Exception("아이디 입력 필드를 찾을 수 없습니다")
            
            # 비밀번호 필드 찾기
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located(selector)
                    )
                    self.logger.debug(f"비밀번호 필드 발견: {selector}")
                    break
                except:
                    continue
                    
            if not password_field:
                raise Exception("비밀번호 입력 필드를 찾을 수 없습니다")
            
            # 로그인 정보 입력
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            # 로그인 버튼 찾기
            login_button = None
            button_selectors = [
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, "input[type='submit']"),
                (By.ID, "login"),
                (By.NAME, "login"),
                (By.XPATH, "//button[contains(text(), '로그인')]"),
                (By.XPATH, "//input[contains(@value, '로그인')]")
            ]
            
            for selector in button_selectors:
                try:
                    login_button = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable(selector)
                    )
                    self.logger.debug(f"로그인 버튼 발견: {selector}")
                    break
                except:
                    continue
                    
            if not login_button:
                raise Exception("로그인 버튼을 찾을 수 없습니다")
            
            # 로그인 버튼 클릭
            login_button.click()
            self.logger.info("로그인 시도 중...")
            
            # 로그인 성공 여부 확인 (예: URL 변경 또는 특정 요소 존재)
            time.sleep(2)  # 페이지 전환 대기
            
            # 에러 메시지 확인
            error_selectors = [
                "//div[contains(text(), '실패')]",
                "//div[contains(text(), '오류')]",
                "//span[contains(text(), '실패')]",
                "//span[contains(text(), '오류')]"
            ]
            
            for selector in error_selectors:
                try:
                    error_elem = self.driver.find_element(By.XPATH, selector)
                    if error_elem.is_displayed():
                        raise Exception("로그인 실패: 아이디 또는 비밀번호가 올바르지 않습니다")
                except NoSuchElementException:
                    continue
            
            self.logger.info("로그인 성공")
            
        except Exception as e:
            self.logger.error(f"로그인 실패: {str(e)}")
            raise

    def select_seats(self, seat_preferences):
        """Select seats based on user preferences"""
        try:
            # Wait for seat selection page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "seat-map"))
            )
            
            # Implement seat selection logic based on preferences
            # This is a placeholder - actual implementation will depend on the website's structure
            for seat in seat_preferences:
                seat_element = self.driver.find_element(By.ID, f"seat-{seat}")
                if seat_element.is_enabled():
                    seat_element.click()
                    self.logger.info(f"Selected seat: {seat}")
                    break
            
            return True
        except Exception as e:
            self.logger.error(f"Seat selection failed: {str(e)}")
            return False

    def complete_purchase(self, payment_info):
        """Complete the purchase process"""
        try:
            # Wait for payment form
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "payment-form"))
            )
            
            # Fill payment information
            # Implementation depends on the specific website's payment process
            
            # Submit payment
            submit_button = self.driver.find_element(By.ID, "submit-payment")
            submit_button.click()
            
            self.logger.info("Purchase completed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Purchase failed: {str(e)}")
            return False

    def close(self):
        """Close the browser and clean up"""
        if self.driver:
            self.driver.quit()
            self.logger.info("Browser closed")
