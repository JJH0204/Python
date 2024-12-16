import customtkinter as ctk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from datetime import datetime, timedelta
import threading
import ntplib
import requests
from urllib.parse import urlparse

class TimeSync:
    @staticmethod
    def get_server_time(domain):
        """서버 시간 가져오기"""
        try:
            response = requests.head(f"https://{domain}")
            server_time = response.headers.get('date')
            if server_time:
                server_datetime = datetime.strptime(server_time, '%a, %d %b %Y %H:%M:%S %Z')
                return server_datetime
        except Exception as e:
            print(f"서버 시간 동기화 실패: {str(e)}")
        return None

class TicketingGUI:
    def __init__(self):
        self.setup_gui()
        self.bot = None
        self.server_time_thread = None
        self.server_time_running = False

    def setup_gui(self):
        """GUI 설정"""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.window = ctk.CTk()
        self.window.title("티켓팅 자동화 프로그램")
        self.window.geometry("800x700")

        # 입력 프레임
        input_frame = ctk.CTkFrame(self.window)
        input_frame.pack(padx=20, pady=20, fill="x")

        # URL 입력
        ctk.CTkLabel(input_frame, text="티켓팅 사이트 URL:").pack(anchor="w")
        self.url_entry = ctk.CTkEntry(input_frame, width=400)
        self.url_entry.pack(pady=5, anchor="w")

        # 서버 도메인 입력
        ctk.CTkLabel(input_frame, text="서버 도메인 (예: ticket.example.com):").pack(anchor="w")
        self.domain_entry = ctk.CTkEntry(input_frame, width=400)
        self.domain_entry.pack(pady=5, anchor="w")

        # 시간 설정 프레임
        time_frame = ctk.CTkFrame(input_frame)
        time_frame.pack(pady=10, fill="x")

        # 예약 시간 입력
        ctk.CTkLabel(time_frame, text="예약 시간 설정:").pack(anchor="w")
        time_input_frame = ctk.CTkFrame(time_frame)
        time_input_frame.pack(fill="x", pady=5)

        # 날짜 입력
        self.date_entry = ctk.CTkEntry(time_input_frame, width=100, placeholder_text="YYYY-MM-DD")
        self.date_entry.pack(side="left", padx=5)

        # 시간 입력
        self.hour_entry = ctk.CTkEntry(time_input_frame, width=50, placeholder_text="HH")
        self.hour_entry.pack(side="left", padx=5)
        ctk.CTkLabel(time_input_frame, text=":").pack(side="left")
        self.minute_entry = ctk.CTkEntry(time_input_frame, width=50, placeholder_text="MM")
        self.minute_entry.pack(side="left", padx=5)
        ctk.CTkLabel(time_input_frame, text=":").pack(side="left")
        self.second_entry = ctk.CTkEntry(time_input_frame, width=50, placeholder_text="SS")
        self.second_entry.pack(side="left", padx=5)

        # 서버 시간 표시
        self.server_time_label = ctk.CTkLabel(time_frame, text="서버 시간: 동기화 전")
        self.server_time_label.pack(anchor="w", pady=5)
        
        # 시간 동기화 버튼
        self.sync_button = ctk.CTkButton(time_frame, text="서버 시간 동기화", command=self.start_time_sync)
        self.sync_button.pack(anchor="w", pady=5)

        # 로그인 정보 입력
        ctk.CTkLabel(input_frame, text="아이디:").pack(anchor="w")
        self.id_entry = ctk.CTkEntry(input_frame, width=200)
        self.id_entry.pack(pady=5, anchor="w")

        ctk.CTkLabel(input_frame, text="비밀번호:").pack(anchor="w")
        self.pw_entry = ctk.CTkEntry(input_frame, width=200, show="*")
        self.pw_entry.pack(pady=5, anchor="w")

        ctk.CTkLabel(input_frame, text="2차 비밀번호:").pack(anchor="w")
        self.pw2_entry = ctk.CTkEntry(input_frame, width=200, show="*")
        self.pw2_entry.pack(pady=5, anchor="w")

        # 버튼 프레임
        button_frame = ctk.CTkFrame(self.window)
        button_frame.pack(pady=10, fill="x")

        self.start_button = ctk.CTkButton(button_frame, text="시작", command=self.start_ticketing)
        self.start_button.pack(side="left", padx=10)

        self.stop_button = ctk.CTkButton(button_frame, text="중지", command=self.stop_ticketing, state="disabled")
        self.stop_button.pack(side="left", padx=10)

        # 로그 출력 영역
        log_frame = ctk.CTkFrame(self.window)
        log_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.log_text = ctk.CTkTextbox(log_frame, width=700, height=300)
        self.log_text.pack(padx=10, pady=10, fill="both", expand=True)

    def update_server_time(self):
        """서버 시간 주기적 업데이트"""
        while self.server_time_running:
            try:
                domain = self.domain_entry.get()
                if domain:
                    server_time = TimeSync.get_server_time(domain)
                    if server_time:
                        self.server_time_label.configure(text=f"서버 시간: {server_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    else:
                        self.server_time_label.configure(text="서버 시간: 동기화 실패")
            except Exception as e:
                self.log(f"서버 시간 업데이트 실패: {str(e)}")
            time.sleep(1)

    def start_time_sync(self):
        """서버 시간 동기화 시작"""
        if not self.domain_entry.get():
            self.log("서버 도메인을 입력해주세요.")
            return

        self.server_time_running = True
        self.server_time_thread = threading.Thread(target=self.update_server_time, daemon=True)
        self.server_time_thread.start()
        self.sync_button.configure(state="disabled")
        self.log("서버 시간 동기화를 시작합니다.")

    def validate_time_input(self):
        """시간 입력값 검증"""
        try:
            date_str = self.date_entry.get()
            hour_str = self.hour_entry.get()
            minute_str = self.minute_entry.get()
            second_str = self.second_entry.get()

            if not all([date_str, hour_str, minute_str, second_str]):
                self.log("예약 시간을 모두 입력해주세요.")
                return None

            target_time = datetime.strptime(
                f"{date_str} {hour_str}:{minute_str}:{second_str}",
                "%Y-%m-%d %H:%M:%S"
            )
            return target_time
        except ValueError as e:
            self.log("올바른 시간 형식을 입력해주세요. (YYYY-MM-DD HH:MM:SS)")
            return None

    def log(self, message):
        """로그 메시지 출력"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")

    def start_ticketing(self):
        """티켓팅 시작"""
        # 입력값 검증
        if not all([self.url_entry.get(), self.id_entry.get(), self.pw_entry.get()]):
            self.log("필수 정보를 모두 입력해주세요.")
            return

        target_time = self.validate_time_input()
        if not target_time:
            return

        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

        # 티켓팅 봇 실행
        self.bot = TicketingBot(self, target_time)
        threading.Thread(target=self.bot.run, daemon=True).start()

    def stop_ticketing(self):
        """티켓팅 중지"""
        if self.bot:
            self.bot.stop()
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.log("티켓팅이 중지되었습니다.")

    def run(self):
        """GUI 실행"""
        self.window.mainloop()

class TicketingBot:
    def __init__(self, gui, target_time):
        self.gui = gui
        self.target_time = target_time
        self.running = False
        self.driver = None

    def setup_driver(self):
        """Chrome 드라이버 설정"""
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def wait_for_target_time(self):
        """목표 시간까지 대기"""
        while self.running:
            current_time = datetime.now()
            if current_time >= self.target_time:
                self.gui.log("목표 시간이 되어 티켓팅을 시작합니다.")
                return True
            time.sleep(0.1)
        return False

    def login(self):
        """로그인 수행"""
        try:
            self.driver.get(self.gui.url_entry.get())
            
            # ID 입력
            username_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_input.send_keys(self.gui.id_entry.get())
            
            # 비밀번호 입력
            password_input = self.driver.find_element(By.ID, "password")
            password_input.send_keys(self.gui.pw_entry.get())
            
            # 로그인 버튼 클릭
            login_button = self.driver.find_element(By.ID, "login-button")
            login_button.click()
            
            self.gui.log("로그인 성공!")
            return True
        except Exception as e:
            self.gui.log(f"로그인 실패: {str(e)}")
            return False

    def select_ticket(self):
        """티켓 선택 및 예매 시도"""
        try:
            self.gui.log("티켓 선택 프로세스 시작...")
            # 여기에 실제 티켓 선택 로직 구현
            pass
        except Exception as e:
            self.gui.log(f"티켓 선택 실패: {str(e)}")

    def purchase_ticket(self):
        """티켓 구매 실행"""
        try:
            if self.gui.pw2_entry.get():  # 2차 비밀번호가 있는 경우
                self.gui.log("2차 비밀번호 입력 중...")
                # 2차 비밀번호 입력 로직 구현
            self.gui.log("결제 프로세스 시작...")
            # 여기에 실제 구매 로직 구현
            pass
        except Exception as e:
            self.gui.log(f"티켓 구매 실패: {str(e)}")

    def stop(self):
        """티켓팅 중지"""
        self.running = False
        if self.driver:
            self.driver.quit()

    def run(self):
        """전체 티켓팅 프로세스 실행"""
        self.running = True
        self.gui.log(f"티켓팅 예약 시간: {self.target_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            self.setup_driver()
            if self.login() and self.running:
                self.gui.log("목표 시간까지 대기합니다...")
                if self.wait_for_target_time() and self.running:
                    self.select_ticket()
                    if self.running:
                        self.purchase_ticket()
        except Exception as e:
            self.gui.log(f"오류 발생: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
            if self.running:
                self.gui.start_button.configure(state="normal")
                self.gui.stop_button.configure(state="disabled")

if __name__ == "__main__":
    app = TicketingGUI()
    app.run()
