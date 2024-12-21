import customtkinter as ctk
from tkcalendar import DateEntry
from datetime import datetime
import json
import logging
from selenium_ticketing import TicketingBot
from server_time import ServerTimeTracker

class TicketingGUI:
    def __init__(self):
        self.setup_logging()
        self.setup_window()
        self.load_config()
        self.ticketing_bot = TicketingBot()
        self.time_tracker = ServerTimeTracker()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def setup_window(self):
        """Initialize the main window and UI components"""
        self.window = ctk.CTk()
        self.window.title("자동 티켓팅 시스템")
        self.window.geometry("800x600")
        
        # Create tabs
        self.tabview = ctk.CTkTabview(self.window)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Add tabs
        self.tab_login = self.tabview.add("로그인 설정")
        self.tab_ticket = self.tabview.add("티켓 설정")
        self.tab_monitor = self.tabview.add("티켓팅")
        
        self.setup_login_tab()
        self.setup_ticket_tab()
        self.setup_monitor_tab()

    def setup_login_tab(self):
        """Setup login credentials tab"""
        # Website URL
        ctk.CTkLabel(self.tab_login, text="웹사이트 URL:").pack(pady=5)
        self.url_entry = ctk.CTkEntry(self.tab_login, width=300)
        self.url_entry.pack(pady=5)
        
        # Username
        ctk.CTkLabel(self.tab_login, text="아이디:").pack(pady=5)
        self.username_entry = ctk.CTkEntry(self.tab_login, width=300)
        self.username_entry.pack(pady=5)
        
        # Password
        ctk.CTkLabel(self.tab_login, text="비밀번호:").pack(pady=5)
        self.password_entry = ctk.CTkEntry(self.tab_login, show="*", width=300)
        self.password_entry.pack(pady=5)
        
        # Save button
        ctk.CTkButton(self.tab_login, text="로그인 정보 저장", 
                     command=self.save_credentials).pack(pady=20)

    def setup_ticket_tab(self):
        """Setup ticket preferences tab"""
        # Date selection
        ctk.CTkLabel(self.tab_ticket, text="예매 날짜:").pack(pady=5)
        self.date_entry = DateEntry(self.tab_ticket, width=12, background='darkblue',
                                  foreground='white', borderwidth=2)
        self.date_entry.pack(pady=5)
        
        # Time selection
        ctk.CTkLabel(self.tab_ticket, text="예매 시간 (HH:MM):").pack(pady=5)
        self.time_entry = ctk.CTkEntry(self.tab_ticket, width=100)
        self.time_entry.pack(pady=5)
        
        # Save button
        ctk.CTkButton(self.tab_ticket, text="설정 저장", 
                     command=self.save_preferences).pack(pady=20)

    def setup_monitor_tab(self):
        """Setup ticketing tab"""
        # Website path input
        ctk.CTkLabel(self.tab_monitor, text="티켓팅 웹사이트 경로:").pack(pady=5)
        self.website_path_entry = ctk.CTkEntry(self.tab_monitor, width=300)
        self.website_path_entry.pack(pady=5)
        
        # Status display
        self.status_label = ctk.CTkLabel(self.tab_monitor, text="상태: 대기중")
        self.status_label.pack(pady=10)
        
        # Server time display frame
        time_frame = ctk.CTkFrame(self.tab_monitor)
        time_frame.pack(pady=10, padx=20, fill="x")
        
        # Server time with large font
        self.server_time_label = ctk.CTkLabel(
            time_frame, 
            text="서버 시간: 연결 대기중",
            font=("Arial", 20, "bold")
        )
        self.server_time_label.pack(pady=5)
        
        # Time difference with smaller font
        self.time_diff_label = ctk.CTkLabel(
            time_frame,
            text="시간 차이: -",
            font=("Arial", 12)
        )
        self.time_diff_label.pack(pady=2)
        
        # Control buttons
        self.start_button = ctk.CTkButton(self.tab_monitor, text="티켓팅 시작", 
                                        command=self.start_monitoring)
        self.start_button.pack(pady=10)
        
        self.stop_button = ctk.CTkButton(self.tab_monitor, text="티켓팅 중지", 
                                       command=self.stop_monitoring)
        self.stop_button.pack(pady=10)
        self.stop_button.configure(state="disabled")

    def save_credentials(self):
        """Save login credentials and start time synchronization"""
        self.config['url'] = self.url_entry.get()
        self.config['username'] = self.username_entry.get()
        self.config['password'] = self.password_entry.get()
        self.save_config()
        
        # Start time synchronization with the saved URL
        if self.config['url']:
            self.time_tracker.start_tracking(self.config['url'])
            self.update_server_time()
            self.logger.info("서버 시간 동기화가 시작되었습니다")
        
        self.logger.info("로그인 정보가 저장되었습니다")

    def save_preferences(self):
        """Save ticket preferences"""
        self.config['target_date'] = self.date_entry.get_date().strftime('%Y-%m-%d')
        self.config['target_time'] = self.time_entry.get()
        self.save_config()
        self.logger.info("설정이 저장되었습니다")

    def load_config(self):
        """Load configuration from file"""
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {}
            self.logger.info("No config file found, creating new one")

    def save_config(self):
        """Save configuration to file"""
        with open('config.json', 'w') as f:
            json.dump(self.config, f)

    def start_monitoring(self):
        """Start ticketing process"""
        website_path = self.website_path_entry.get()
        if not website_path:
            self.logger.warning("티켓팅 웹사이트 경로를 입력해주세요.")
            return
            
        self.status_label.configure(text="상태: 실행중")
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        
        # Start time tracking
        self.time_tracker.start_tracking(website_path)
        self.update_server_time()
        
        self.logger.info("티켓팅이 시작되었습니다.")

    def stop_monitoring(self):
        """Stop monitoring and cleanup"""
        self.status_label.configure(text="상태: 중지됨")
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        
        # Stop time tracking
        self.time_tracker.stop_tracking()
        self.logger.info("Monitoring stopped")

    def update_server_time(self):
        """Update server time display"""
        if hasattr(self, 'time_tracker'):
            try:
                current_time = datetime.fromtimestamp(self.time_tracker.get_current_server_time())
                time_diff = self.time_tracker.time_difference
                
                # 서버 시간 업데이트
                time_str = current_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]
                self.server_time_label.configure(text=f"서버 시간: {time_str}")
                
                # 시간 차이 업데이트 (색상으로 상태 표시)
                if abs(time_diff) < 0.5:  # 0.5초 미만
                    color = "green"
                    status = "정상"
                elif abs(time_diff) < 1.0:  # 1초 미만
                    color = "orange"
                    status = "주의"
                else:
                    color = "red"
                    status = "경고"
                
                self.time_diff_label.configure(
                    text=f"시간 차이: {time_diff:+.2f}초 ({status})",
                    text_color=color
                )
            except Exception as e:
                self.logger.error(f"시간 업데이트 실패: {str(e)}")
                
        self.window.after(50, self.update_server_time)  # 50ms 간격으로 업데이트

    def run(self):
        """Start the GUI application"""
        self.window.mainloop()

if __name__ == "__main__":
    app = TicketingGUI()
    app.run()
