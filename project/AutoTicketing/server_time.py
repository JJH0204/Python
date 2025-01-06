import requests
import ntplib
from datetime import datetime
import time
import logging
from threading import Thread, Event

class ServerTimeTracker:
    def __init__(self):
        self.setup_logging()
        self.stop_event = Event()
        self.current_time = None
        self.time_difference = 0
        self.prev_time_diff = None
        self.ntp_client = ntplib.NTPClient()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def get_server_time(self, url):
        """Get time from NTP server"""
        try:
            # NTP 서버에서 시간 가져오기
            ntp_response = self.ntp_client.request('pool.ntp.org', version=3, timeout=2)
            
            # NTP 응답에서 이미 로컬 시간대가 적용된 시간을 얻음
            server_time = datetime.fromtimestamp(ntp_response.tx_time)
            
            self.logger.debug(f"NTP 서버 시간: {server_time}")
            return server_time
            
        except Exception as e:
            self.logger.error(f"NTP 서버 시간 가져오기 실패: {str(e)}")
            
            # HTTP 헤더로 폴백
            try:
                response = requests.head(url, timeout=2)
                if 'date' not in response.headers:
                    self.logger.error("HTTP 응답에 date 헤더가 없습니다")
                    return datetime.now()  # 로컬 시간 사용
                    
                server_time_str = response.headers['date']
                try:
                    server_time = datetime.strptime(server_time_str, '%a, %d %b %Y %H:%M:%S %Z')
                    return server_time
                except ValueError:
                    self.logger.error(f"잘못된 시간 형식: {server_time_str}")
                    return datetime.now()  # 로컬 시간 사용
                    
            except Exception as e2:
                self.logger.error(f"HTTP 시간 가져오기도 실패: {str(e2)}")
                return datetime.now()  # 로컬 시간 사용

    def calculate_time_difference(self, server_url):
        """Calculate time difference between local and server time"""
        try:
            server_time = self.get_server_time(server_url)
            if not server_time:
                return 0
                
            local_time = datetime.now()
            new_time_diff = (server_time - local_time).total_seconds()
            
            # 이전 시간차가 없으면 현재 값 사용
            if not hasattr(self, 'prev_time_diff') or self.prev_time_diff is None:
                self.time_difference = new_time_diff
            else:
                # 시간차가 9시간(32400초) 이상 나면 무시
                if abs(new_time_diff) > 32400:
                    self.logger.warning(f"비정상적인 시간 차이 감지: {new_time_diff:.2f}초")
                    return self.prev_time_diff
                
                # 급격한 변화 방지
                max_change = 0.1  # 최대 0.1초 변화 허용
                if abs(new_time_diff - self.prev_time_diff) > max_change:
                    if new_time_diff > self.prev_time_diff:
                        new_time_diff = self.prev_time_diff + max_change
                    else:
                        new_time_diff = self.prev_time_diff - max_change
                
                # 이동 평균 적용
                alpha = 0.2  # 새로운 값의 영향력 20%로 감소
                self.time_difference = (alpha * new_time_diff) + ((1 - alpha) * self.prev_time_diff)
            
            self.prev_time_diff = self.time_difference
            self.logger.info(f"서버와의 시간 차이: {self.time_difference:.2f}초")
            return self.time_difference
            
        except Exception as e:
            self.logger.error(f"시간 차이 계산 중 오류 발생: {str(e)}")
            return self.prev_time_diff if hasattr(self, 'prev_time_diff') else 0

    def get_current_server_time(self):
        """Get current server time based on calculated difference"""
        if not hasattr(self, 'time_difference'):
            return time.time()
        return time.time() + self.time_difference

    def start_tracking(self, server_url, update_interval=1):
        """Start continuous time tracking"""
        def track():
            while not self.stop_event.is_set():
                try:
                    self.calculate_time_difference(server_url)
                    time.sleep(update_interval)
                except Exception as e:
                    self.logger.error(f"시간 추적 중 오류 발생: {str(e)}")
                    time.sleep(1)

        self.stop_event.clear()
        self.prev_time_diff = None
        self.tracking_thread = Thread(target=track, daemon=True)
        self.tracking_thread.start()
        self.logger.info("시간 추적이 시작되었습니다")

    def stop_tracking(self):
        """Stop time tracking"""
        self.stop_event.set()
        if hasattr(self, 'tracking_thread'):
            self.tracking_thread.join()
        self.logger.info("Time tracking stopped")

    def wait_until(self, target_time):
        """Wait until specific server time"""
        while self.get_current_server_time() < target_time:
            time.sleep(0.001)  # Small sleep to prevent CPU overload
