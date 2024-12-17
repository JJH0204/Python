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
import tkcalendar
import statistics
from dateutil import tz
from datetime import timezone

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
        self.window = ctk.CTk()
        self.setup_gui()
        self.bot = None
        self.server_time_thread = None
        self.server_time_running = False
        self.sync_interval = 1000  # 시간 동기화 간격 (밀리초)
        self.sync_lock = threading.Lock()  # 스레드 동기화를 위한 락
        self.server_timestamp = None  # 서버의 현재 타임스탬프
        self.local_timestamp = None  # 동기화 시점의 로컬 타임스탬프
        self.time_diff = 0  # 서버와 로컬 시간의 차이 (초)
        self.update_display_running = False  # 디스플레이 업데이트 상태

    def setup_gui(self):
        self.window.title("티켓팅 자동화 프로그램")
        self.window.geometry("800x600")

        # 메인 프레임
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # 입력 필드 기본 설정
        entry_width = 400
        frame_padding = {"padx": 10, "pady": 5}
        
        # URL 입력 프레임
        url_frame = ctk.CTkFrame(main_frame)
        url_frame.pack(fill="x", **frame_padding)
        ctk.CTkLabel(url_frame, text="티켓팅 사이트 URL:", width=100).pack(side="left", padx=5)
        self.url_entry = ctk.CTkEntry(url_frame, width=entry_width)
        self.url_entry.pack(side="left", padx=5)

        # 서버 시간 표시
        time_frame = ctk.CTkFrame(main_frame)
        time_frame.pack(fill="x", **frame_padding)
        self.server_time_label = ctk.CTkLabel(
            time_frame,
            text="HH : MM : SS",
            font=("Arial", 24, "bold")
        )
        self.server_time_label.pack(pady=10)

        # 사용자 정보 프레임
        user_info_frame = ctk.CTkFrame(main_frame)
        user_info_frame.pack(fill="x", **frame_padding)
        ctk.CTkLabel(user_info_frame, text="사용자 정보").pack(anchor="w", padx=5, pady=5)
        
        # 아이디
        id_frame = ctk.CTkFrame(user_info_frame)
        id_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(id_frame, text="아이디:", width=100).pack(side="left", padx=5)
        self.id_entry = ctk.CTkEntry(id_frame, width=entry_width)
        self.id_entry.pack(side="left", padx=5)

        # 비밀번호
        pw_frame = ctk.CTkFrame(user_info_frame)
        pw_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(pw_frame, text="비밀번호:", width=100).pack(side="left", padx=5)
        self.pw_entry = ctk.CTkEntry(pw_frame, width=entry_width, show="*")
        self.pw_entry.pack(side="left", padx=5)

        # 2차 비밀번호
        pw2_frame = ctk.CTkFrame(user_info_frame)
        pw2_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(pw2_frame, text="2차 비밀번호:", width=100).pack(side="left", padx=5)
        self.pw2_entry = ctk.CTkEntry(pw2_frame, width=entry_width, show="*")
        self.pw2_entry.pack(side="left", padx=5)

        # 우측 프레임 (예약 설정)
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(fill="both", expand=True, **frame_padding)

        # 시간 예약 체크박스
        reservation_header = ctk.CTkFrame(right_frame)
        reservation_header.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(reservation_header, text="예약 시간 설정").pack(side="left", padx=5)
        self.time_reservation_var = ctk.BooleanVar(value=False)
        self.time_reservation_checkbox = ctk.CTkCheckBox(
            reservation_header,
            text="시간 예약 사용",
            variable=self.time_reservation_var,
            command=self.toggle_time_reservation
        )
        self.time_reservation_checkbox.pack(side="right", padx=5)

        # 도메인 입력
        domain_frame = ctk.CTkFrame(right_frame)
        domain_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(domain_frame, text="서버 도메인:", width=100).pack(side="left", padx=5)
        self.domain_entry = ctk.CTkEntry(domain_frame, width=entry_width, state="disabled")
        self.domain_entry.pack(side="left", padx=5)
        self.domain_entry.bind('<KeyRelease>', self.on_domain_change)

        # 시간 선택
        time_select_frame = ctk.CTkFrame(right_frame)
        time_select_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(time_select_frame, text="시간 선택:", width=100).pack(side="left", padx=5)

        time_input_frame = ctk.CTkFrame(time_select_frame)
        time_input_frame.pack(side="left", padx=5)

        self.hour_spinbox = ctk.CTkOptionMenu(
            time_input_frame,
            values=[f"{i:02d}" for i in range(24)],
            width=70,
            state="disabled"
        )
        self.hour_spinbox.pack(side="left", padx=2)
        
        ctk.CTkLabel(time_input_frame, text=":").pack(side="left")
        
        self.minute_spinbox = ctk.CTkOptionMenu(
            time_input_frame,
            values=[f"{i:02d}" for i in range(60)],
            width=70,
            state="disabled"
        )
        self.minute_spinbox.pack(side="left", padx=2)
        
        ctk.CTkLabel(time_input_frame, text=":").pack(side="left")
        
        self.second_spinbox = ctk.CTkOptionMenu(
            time_input_frame,
            values=[f"{i:02d}" for i in range(60)],
            width=70,
            state="disabled"
        )
        self.second_spinbox.pack(side="left", padx=2)

        # 로그 영역
        log_frame = ctk.CTkFrame(right_frame)
        log_frame.pack(fill="both", expand=True, padx=5, pady=5)
        ctk.CTkLabel(log_frame, text="로그").pack(anchor="w", padx=5, pady=2)
        self.log_text = ctk.CTkTextbox(log_frame, height=200)
        self.log_text.pack(padx=5, pady=2, fill="both", expand=True)

        # 하단 버튼
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", **frame_padding)
        
        self.start_button = ctk.CTkButton(button_frame, text="티켓팅 시작", command=self.start_ticketing, width=150)
        self.start_button.pack(side="left", padx=5)
        
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="티켓팅 중지",
            command=self.stop_ticketing,
            state="disabled",
            width=150
        )
        self.stop_button.pack(side="left", padx=5)

        # 초기 시간 설정
        now = datetime.now()
        self.hour_spinbox.set(f"{now.hour:02d}")
        self.minute_spinbox.set(f"{now.minute:02d}")
        self.second_spinbox.set(f"{now.second:02d}")

    def sync_time_with_server(self):
        """서버와의 시간 동기화 및 타임스탬프 저장"""
        try:
            domain = self.domain_entry.get().strip()
            if not domain:
                return False

            if not domain.startswith(('http://', 'https://')):
                domain = f'https://{domain}'

            # 시간 동기화 요청 전 로컬 시간 기록
            request_start = time.time()
            
            response = requests.head(domain, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }, timeout=5)
            
            request_end = time.time()
            
            if 'date' in response.headers:
                # 서버 시간 파싱
                server_time = datetime.strptime(
                    response.headers['date'],
                    '%a, %d %b %Y %H:%M:%S GMT'
                ).replace(tzinfo=timezone.utc)
                
                # 네트워크 지연시간의 절반을 보정값으로 사용
                network_delay = (request_end - request_start) / 2
                
                # 서버 타임스탬프 저장 (네트워크 지연 보정 적용)
                self.server_timestamp = server_time.timestamp() + network_delay
                self.local_timestamp = request_start
                self.time_diff = self.server_timestamp - self.local_timestamp
                
                # 한국 시간으로 변환하여 UI에 표시
                kr_time = server_time.astimezone(timezone(timedelta(hours=9)))
                self.server_time_label.configure(text=kr_time.strftime("%H:%M:%S"))
                
                return True
                
            return False

        except Exception as e:
            self.log(f"시간 동기화 중 오류 발생: {str(e)}")
            return False

    def get_current_server_time(self):
        """현재 서버 시간 계산"""
        if self.server_timestamp is not None and self.local_timestamp is not None:
            elapsed = time.time() - self.local_timestamp
            current_server_time = self.server_timestamp + elapsed
            return datetime.fromtimestamp(current_server_time, tz=timezone.utc)
        return None

    def update_time_display(self):
        """UI의 시간 표시를 업데이트"""
        if not self.server_time_running:
            self.update_display_running = False
            return

        try:
            current_time = self.get_current_server_time()
            if current_time:
                # 한국 시간으로 변환
                kr_time = current_time.astimezone(timezone(timedelta(hours=9)))
                self.server_time_label.configure(text=kr_time.strftime("%H:%M:%S"))
        except Exception as e:
            self.log(f"시간 표시 업데이트 중 오류: {str(e)}")

        # 다음 업데이트 예약 (10ms 간격으로 더 자주 업데이트)
        if self.server_time_running:
            self.window.after(10, self.update_time_display)

    def auto_sync_time(self):
        """자동 시간 동기화"""
        if not self.server_time_running:
            return

        try:
            domain = self.domain_entry.get().strip()
            if not domain:
                self.server_time_running = False
                self.update_display_running = False
                self.server_timestamp = None
                self.local_timestamp = None
                self.server_time_label.configure(text="HH : MM : SS")
                return

            # 서버 시간 동기화
            if self.sync_time_with_server():
                # 동기화 성공 시 UI 업데이트 상태 확인
                if not self.update_display_running:
                    self.update_display_running = True
                    self.update_time_display()
            
            # 다음 동기화 예약 (1초 간격)
            if self.server_time_running:
                self.window.after(self.sync_interval, self.auto_sync_time)
                
        except Exception as e:
            self.log(f"자동 시간 동기화 중 오류 발생: {str(e)}")

    def on_domain_change(self, event):
        """도메인 입력 시 자동 시간 동기화 시작"""
        try:
            with self.sync_lock:
                domain = self.domain_entry.get().strip()
                if self.time_reservation_var.get():
                    if domain:
                        self.server_time_running = True
                        # 최초 동기화 시작
                        if self.sync_time_with_server():
                            # UI 업데이트 시작
                            if not self.update_display_running:
                                self.update_display_running = True
                                self.update_time_display()
                            # 주기적 서버 시간 확인 시작
                            self.auto_sync_time()
                        else:
                            self.server_time_running = False
                            self.log("서버 시간 동기화에 실패했습니다.")
                    else:
                        # 도메인이 비어있을 때 시간 동기화 중지
                        self.server_time_running = False
                        self.update_display_running = False
                        self.server_timestamp = None
                        self.local_timestamp = None
                        self.server_time_label.configure(text="HH : MM : SS")
                        
        except Exception as e:
            self.log(f"시간 동기화 시작 실패: {str(e)}")

    def toggle_time_reservation(self):
        """시간 예약 체크박스 토글 시 관련 UI 활성/비활성화"""
        try:
            is_checked = self.time_reservation_var.get()
            
            # 도메인 입력 필드 상태 변경
            self.domain_entry.configure(state="normal" if is_checked else "disabled")
            
            # 시간 입력 위젯들 상태 변경
            widgets_to_toggle = [
                self.hour_spinbox,
                self.minute_spinbox,
                self.second_spinbox
            ]
            
            for widget in widgets_to_toggle:
                widget.configure(state="normal" if is_checked else "disabled")

            # 체크 해제 시 시간 동기화 중지
            if not is_checked:
                with self.sync_lock:
                    self.server_time_running = False
                    self.update_display_running = False
                    self.server_timestamp = None
                    self.local_timestamp = None
                    self.server_time_label.configure(text="HH : MM : SS")
                    self.domain_entry.delete(0, 'end')

        except Exception as e:
            self.log(f"시간 예약 설정 변경 중 오류 발생: {str(e)}")

    def check_reservation_time(self):
        """예약된 시간과 서버 시간 비교"""
        if not self.server_timestamp:
            return False
            
        try:
            # 예약된 시간 가져오기
            hour = int(self.hour_spinbox.get())
            minute = int(self.minute_spinbox.get())
            second = int(self.second_spinbox.get())
            
            # 현재 서버 시간 계산
            current_server_time = self.get_current_server_time()
            if not current_server_time:
                return False
                
            # 한국 시간대로 변환
            kr_time = current_server_time.astimezone(timezone(timedelta(hours=9)))
            
            # 예약된 시간 생성 (오늘 날짜 기준)
            reserved_time = kr_time.replace(
                hour=hour, 
                minute=minute, 
                second=second, 
                microsecond=0
            )
            
            # 시간 비교
            return kr_time >= reserved_time
            
        except Exception as e:
            self.log(f"시간 비교 중 오류 발생: {str(e)}")
            return False

    def start_ticketing(self):
        """티켓팅 시작"""
        if self.time_reservation_var.get():
            # 예약된 시간까지 대기
            if not self.check_reservation_time():
                # 100ms 후에 다시 확인
                self.window.after(100, self.start_ticketing)
                return
        
        # 여기에 실제 티켓팅 로직 구현
        self.log("티켓팅 시작!")

    def stop_ticketing(self):
        """티켓팅 중지"""
        if self.bot:
            self.bot.stop()
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.log("티켓팅이 중지되었습니다.")

    def log(self, message, show_time=True):
        """로그 메시지 출력"""
        if show_time:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.log_text.insert("end", f"[{timestamp}] {message}\n")
        else:
            self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")

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
        
        # 드라이버 경로를 명시적으로 설정
        driver_path = ChromeDriverManager().install()
        service = Service(executable_path=driver_path)
        
        try:
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
        except Exception as e:
            self.gui.log(f"드라이버 설정 중 오류 발생: {str(e)}")
            raise

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
        self.gui.log(f"티켓팅 예약 시간: {self.target_time.strftime('%H:%M:%S')}")
        
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
