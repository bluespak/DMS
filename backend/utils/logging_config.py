#!/usr/bin/env python3
"""
DMS 로깅 설정 모듈
- 로그 레벨 관리 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- 파일 로테이션 (크기 제한)
- 콘솔과 파일 동시 출력
- 개발/운영 환경별 설정
"""

import logging
import logging.handlers
import os
import uuid
from datetime import datetime
from pathlib import Path

class DMSLogger:
    """DMS 전용 로거 클래스"""
    
    def __init__(self, name='DMS', log_dir=None):
        self.name = name
        self.log_dir = Path(log_dir or os.getenv('LOG_DIR', 'logs'))
        self.log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.max_size_mb = int(os.getenv('LOG_MAX_SIZE_MB', '20'))
        self.backup_count = int(os.getenv('LOG_BACKUP_COUNT', '5'))
        self.logger = None
        self.current_date = datetime.now().strftime('%Y%m%d')
        self.session_id = str(uuid.uuid4())[:8]  # 서버 재시작 감지용 세션 ID
        self._setup_logging()
    
    def _setup_logging(self):
        """로깅 시스템 초기화"""
        # 로그 디렉토리 생성
        self.log_dir.mkdir(exist_ok=True)
        
        # 로거 생성
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        
        # 기존 핸들러 제거 (중복 방지)
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 날짜 + 세션 ID 기반 파일명 prefix 생성
        # 형식: dms_backend_api_YYYYMMDD_HHMMSS_SESSION
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_prefix = f'dms_backend_api_{timestamp}_{self.session_id}'
        
        # 포맷터 설정 - 밀리초, 프로세스 ID, 세션 ID 포함
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d | PID:%(process)d | SID:' + self.session_id + ' | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 콘솔 핸들러 (INFO 레벨 이상)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 파일 핸들러 - 전체 로그 (DEBUG 레벨 이상)
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f'{log_prefix}.log',
            maxBytes=self.max_size_mb*1024*1024,  # 환경변수 기반 크기
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # 에러 파일 핸들러 (ERROR 레벨 이상)
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f'{log_prefix}_error.log',
            maxBytes=5*1024*1024,   # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
        
        # 애플리케이션별 핸들러 - API 요청 로그
        api_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f'{log_prefix}_api.log',
            maxBytes=20*1024*1024,  # 20MB
            backupCount=10,
            encoding='utf-8'
        )
        api_handler.setLevel(logging.INFO)
        api_formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d | PID:%(process)d | SID:' + self.session_id + ' | %(levelname)-8s | API | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        api_handler.setFormatter(api_formatter)
        
        # API 로거 별도 생성
        self.api_logger = logging.getLogger(f'{self.name}.API')
        self.api_logger.setLevel(logging.INFO)
        self.api_logger.addHandler(api_handler)
        self.api_logger.propagate = False  # 부모 로거로 전파 방지
    
    def _check_date_change(self):
        """날짜 변화 체크 및 로그 파일 재생성"""
        current_date = datetime.now().strftime('%Y%m%d')
        if current_date != self.current_date:
            self.current_date = current_date
            self.session_id = str(uuid.uuid4())[:8]  # 새로운 세션 ID 생성
            self._setup_logging()  # 로깅 시스템 재초기화
            self.logger.info(f"📅 날짜 변경 감지 - 새로운 로그 파일 생성: {current_date}")
    
    def get_logger(self):
        """메인 로거 반환 (날짜 체크 포함)"""
        self._check_date_change()
        return self.logger
    
    def get_api_logger(self):
        """API 전용 로거 반환 (날짜 체크 포함)"""
        self._check_date_change()
        return self.api_logger
    
    def log_api_request(self, method, endpoint, user_id=None, ip=None, status_code=None, response_time=None):
        """API 요청 로그 기록"""
        self._check_date_change()
        log_msg = f"{method} {endpoint}"
        if user_id:
            log_msg += f" | User: {user_id}"
        if ip:
            log_msg += f" | IP: {ip}"
        if status_code:
            log_msg += f" | Status: {status_code}"
        if response_time:
            log_msg += f" | Time: {response_time:.3f}s"
        
        self.api_logger.info(log_msg)
    
    def log_database_operation(self, operation, table, record_count=None, user_id=None):
        """데이터베이스 작업 로그"""
        self._check_date_change()
        log_msg = f"DB {operation.upper()}: {table}"
        if record_count is not None:
            log_msg += f" | Records: {record_count}"
        if user_id:
            log_msg += f" | User: {user_id}"
        
        self.logger.info(log_msg)
    
    def log_trigger_check(self, trigger_id, trigger_type, user_id, is_triggered=False):
        """트리거 체크 로그"""
        self._check_date_change()
        status = "TRIGGERED" if is_triggered else "CHECKED"
        self.logger.info(f"TRIGGER {status}: ID={trigger_id} | Type={trigger_type} | User={user_id}")
    
    def log_email_dispatch(self, will_id, recipient_id, recipient_email, status):
        """이메일 발송 로그"""
        self._check_date_change()
        self.logger.info(f"EMAIL {status.upper()}: Will={will_id} | Recipient={recipient_id} | Email={recipient_email}")
    
    def log_security_event(self, event_type, user_id=None, ip=None, details=None):
        """보안 이벤트 로그"""
        self._check_date_change()
        log_msg = f"SECURITY {event_type.upper()}"
        if user_id:
            log_msg += f" | User: {user_id}"
        if ip:
            log_msg += f" | IP: {ip}"
        if details:
            log_msg += f" | Details: {details}"
        
        self.logger.warning(log_msg)

# 전역 로거 인스턴스
_dms_logger = None

def get_dms_logger():
    """DMS 로거 싱글톤 인스턴스 반환"""
    global _dms_logger
    if _dms_logger is None:
        _dms_logger = DMSLogger()
    return _dms_logger

def setup_flask_logging(app):
    """Flask 애플리케이션에 로깅 설정 적용"""
    dms_logger = get_dms_logger()
    
    # Flask 기본 로거 설정
    app.logger.handlers.clear()
    app.logger.addHandler(dms_logger.get_logger().handlers[0])  # 콘솔 핸들러
    app.logger.addHandler(dms_logger.get_logger().handlers[1])  # 파일 핸들러
    app.logger.setLevel(logging.INFO)
    
    return dms_logger

def log_function_call(func_name, *args, **kwargs):
    """함수 호출 로그 데코레이터용"""
    logger = get_dms_logger().get_logger()
    args_str = ', '.join([str(arg) for arg in args])
    kwargs_str = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
    params = ', '.join(filter(None, [args_str, kwargs_str]))
    logger.debug(f"FUNCTION CALL: {func_name}({params})")

# 로그 레벨별 편의 함수들
def log_debug(message, **kwargs):
    """DEBUG 레벨 로그"""
    get_dms_logger().get_logger().debug(message, **kwargs)

def log_info(message, **kwargs):
    """INFO 레벨 로그"""
    get_dms_logger().get_logger().info(message, **kwargs)

def log_warning(message, **kwargs):
    """WARNING 레벨 로그"""
    get_dms_logger().get_logger().warning(message, **kwargs)

def log_error(message, **kwargs):
    """ERROR 레벨 로그"""
    get_dms_logger().get_logger().error(message, **kwargs)

def log_critical(message, **kwargs):
    """CRITICAL 레벨 로그"""
    get_dms_logger().get_logger().critical(message, **kwargs)

if __name__ == "__main__":
    # 테스트 코드
    logger = get_dms_logger()
    
    log_info("DMS 로깅 시스템 테스트 시작")
    log_debug("디버그 메시지 테스트")
    log_warning("경고 메시지 테스트")
    log_error("에러 메시지 테스트")
    
    # API 로그 테스트
    logger.log_api_request("GET", "/api/wills", user_id=1, ip="127.0.0.1", status_code=200, response_time=0.045)
    
    # 데이터베이스 로그 테스트
    logger.log_database_operation("select", "wills", record_count=52, user_id=1)
    
    # 트리거 로그 테스트  
    logger.log_trigger_check(1, "inactivity", 1, is_triggered=True)
    
    # 이메일 발송 로그 테스트
    logger.log_email_dispatch(1, 1, "test@sample.recipient.com", "sent")
    
    log_info("DMS 로깅 시스템 테스트 완료")