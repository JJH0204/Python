import json
import os
import logging
from pathlib import Path
from selenium_ticketing import TicketingBot
from server_time import ServerTimeTracker

class LoginManager:
    def __init__(self):
        self.config_file = 'login_config.json'
        self.setup_logging()
        self.config = self.load_config()
        self.ticketing_bot = TicketingBot()
        self.time_tracker = ServerTimeTracker()

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"설정 파일 로드 실패: {str(e)}")
        return {'url': '', 'username': '', 'password': ''}

    def save_config(self, url, username, password):
        """Save login credentials to config file"""
        try:
            config = {
                'url': url,
                'username': username,
                'password': password
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            self.logger.info("로그인 정보가 저장되었습니다")
            return True
        except Exception as e:
            self.logger.error(f"설정 저장 실패: {str(e)}")
            return False

    def get_credentials(self):
        """Get saved credentials"""
        return self.config.get('url', ''), self.config.get('username', ''), self.config.get('password', '')

    def validate_credentials(self, url, username, password):
        """Validate if all credentials are provided"""
        if not url or not username or not password:
            raise ValueError("모든 필드를 입력해주세요.")
        return True

    def attempt_login(self, url, username, password):
        """Attempt to login with provided credentials"""
        try:
            self.validate_credentials(url, username, password)
            
            # Initialize Chrome driver if not exists
            if not hasattr(self.ticketing_bot, 'driver') or not self.ticketing_bot.driver:
                self.ticketing_bot.initialize_driver()
            
            # Attempt login
            self.ticketing_bot.login(url, username, password)
            
            # Start server time tracking
            self.time_tracker.start_tracking(url)
            
            self.logger.info("로그인 성공")
            return True, None
            
        except Exception as e:
            self.logger.error(f"로그인 실패: {str(e)}")
            
            # Clean up on failure
            if hasattr(self.ticketing_bot, 'driver') and self.ticketing_bot.driver:
                self.ticketing_bot.driver.quit()
                self.ticketing_bot.driver = None
                
            return False, str(e)

    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'ticketing_bot') and self.ticketing_bot.driver:
            self.ticketing_bot.driver.quit()
        if hasattr(self, 'time_tracker'):
            self.time_tracker.stop_tracking()
