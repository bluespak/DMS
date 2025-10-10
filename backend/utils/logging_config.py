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
    
    def __init__(self, name='DMS', log_type='server', log_dir=None):
        self.name = name
        self.log_type = log_type  # 'server', 'data', 'system' 등
        
        # 프로젝트 루트 디렉토리 찾기 (utils 디렉토리의 부모 디렉토리)
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent  # backend 디렉토리
        
        # 로그 디렉토리를 프로젝트 루트 기준으로 설정
        if log_dir:
            self.log_dir = Path(log_dir)
        else:
            default_log_dir = os.getenv('LOG_DIR', 'logs')
            self.log_dir = project_root / default_log_dir
            
        # 로그 타입별 서브 디렉토리 생성
        self.log_subdir = self.log_dir / self.log_type
            
        self.log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.max_size_mb = int(os.getenv('LOG_MAX_SIZE_MB', '20'))
        self.backup_count = int(os.getenv('LOG_BACKUP_COUNT', '5'))
        self.archive_hours = int(os.getenv('LOG_ARCHIVE_HOURS', '72'))  # 기본 72시간 (3일)
        self.logger = None
        self.current_date = datetime.now().strftime('%Y%m%d')
        self.session_id = str(uuid.uuid4())[:8]  # 서버 재시작 감지용 세션 ID
        self._setup_logging()
    
    def _setup_logging(self):
        """로깅 시스템 초기화"""
        # 로그 디렉토리 생성 (메인 디렉토리 및 서브 디렉토리)
        self.log_dir.mkdir(exist_ok=True)
        self.log_subdir.mkdir(exist_ok=True)
        
        # 자동 아카이브 실행 (3일 이상 된 로그 파일)
        self._auto_archive_old_logs()
        
        # 로거 생성
        self.logger = logging.getLogger(f'{self.name}.{self.log_type}')
        self.logger.setLevel(logging.DEBUG)
        
        # 기존 핸들러 제거 (중복 방지)
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 로그 타입별 파일명 prefix 생성
        # 서버 로그: dms_server_YYYYMMDD_HHMMSS_SESSION
        # 데이터 로그: dms_data_YYYYMMDD_HHMMSS_SESSION  
        # 시스템 로그: dms_system_YYYYMMDD_HHMMSS_SESSION
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_prefix = f'dms_{self.log_type}_{timestamp}_{self.session_id}'
        
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
            self.log_subdir / f'{log_prefix}.log',
            maxBytes=self.max_size_mb*1024*1024,  # 환경변수 기반 크기
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # 에러 파일 핸들러 (ERROR 레벨 이상)
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_subdir / f'{log_prefix}_error.log',
            maxBytes=5*1024*1024,   # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
        
        # 서버 로그에만 API 핸들러 추가
        if self.log_type == 'server':
            # 애플리케이션별 핸들러 - API 요청 로그
            api_handler = logging.handlers.RotatingFileHandler(
                self.log_subdir / f'{log_prefix}_api.log',
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
            self.api_logger = logging.getLogger(f'{self.name}.{self.log_type}.API')
            self.api_logger.setLevel(logging.INFO)
            self.api_logger.addHandler(api_handler)
            self.api_logger.propagate = False  # 부모 로거로 전파 방지
    
    def _auto_archive_old_logs(self):
        """설정된 시간 이상 된 로그 파일을 자동으로 archive 폴더로 이동"""
        try:
            import shutil
            from datetime import timedelta
            
            # 환경변수 기반 시간 기준점 (기본값: 72시간)
            cutoff_date = datetime.now() - timedelta(hours=self.archive_hours)
            archive_dir = self.log_dir / 'archive' / self.log_type
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            moved_count = 0
            
            # 현재 로그 타입 디렉토리의 로그 파일들 확인
            for log_file in self.log_subdir.glob('*.log'):
                try:
                    # 파일 수정 시간 확인
                    file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                    
                    if file_time < cutoff_date:
                        # 아카이브로 이동
                        archive_file = archive_dir / log_file.name
                        shutil.move(str(log_file), str(archive_file))
                        moved_count += 1
                        
                except Exception as e:
                    # 개별 파일 처리 실패 시 계속 진행
                    continue
            
            # 아카이브 결과 로그 (이미 생성된 로거가 있는 경우에만)
            if moved_count > 0 and hasattr(self, 'logger') and self.logger:
                hours_text = f"{self.archive_hours}시간"
                if self.archive_hours >= 24:
                    days = self.archive_hours // 24
                    remaining_hours = self.archive_hours % 24
                    if remaining_hours == 0:
                        hours_text = f"{days}일"
                    else:
                        hours_text = f"{days}일 {remaining_hours}시간"
                self.logger.info(f"자동 아카이브 완료: {moved_count}개 파일 이동 ({hours_text} 이상 된 로그)")
                
        except Exception as e:
            # 아카이브 실패 시에도 로깅 시스템 초기화는 계속 진행
            pass
    
    def _check_date_change(self):
        """날짜 변화 체크 및 로그 파일 재생성"""
        current_date = datetime.now().strftime('%Y%m%d')
        if current_date != self.current_date:
            self.current_date = current_date
            self.session_id = str(uuid.uuid4())[:8]  # 새로운 세션 ID 생성
            
            # 날짜가 변경될 때마다 자동 아카이브 실행
            self._auto_archive_old_logs()
            
            self._setup_logging()  # 로깅 시스템 재초기화
            self.logger.info(f"📅 날짜 변경 감지 - 새로운 로그 파일 생성: {current_date}")
            
            # 아카이브 시간 표시 계산
            hours_text = f"{self.archive_hours}시간"
            if self.archive_hours >= 24:
                days = self.archive_hours // 24
                remaining_hours = self.archive_hours % 24
                if remaining_hours == 0:
                    hours_text = f"{days}일"
                else:
                    hours_text = f"{days}일 {remaining_hours}시간"
            self.logger.info(f"🗂️  {hours_text} 이상 된 로그 파일 자동 아카이브 실행")
    
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

    @classmethod
    def create_server_logger(cls, name='DMS'):
        """서버 운영 로그용 로거 생성"""
        return cls(name=name, log_type='server')
    
    @classmethod
    def create_data_logger(cls, name='DMS'):
        """데이터 처리 로그용 로거 생성 (import, export 등)"""
        return cls(name=name, log_type='data')
    
    @classmethod
    def create_system_logger(cls, name='DMS'):
        """시스템 로그용 로거 생성"""
        return cls(name=name, log_type='system')

# 전역 로거 인스턴스들
_server_logger = None
_data_logger = None
_system_logger = None

def get_server_logger():
    """서버 로거 싱글톤 인스턴스 반환"""
    global _server_logger
    if _server_logger is None:
        _server_logger = DMSLogger.create_server_logger()
    return _server_logger

def get_data_logger():
    """데이터 로거 싱글톤 인스턴스 반환"""
    global _data_logger
    if _data_logger is None:
        _data_logger = DMSLogger.create_data_logger()
    return _data_logger

def get_system_logger():
    """시스템 로거 싱글톤 인스턴스 반환"""
    global _system_logger
    if _system_logger is None:
        _system_logger = DMSLogger.create_system_logger()
    return _system_logger

def get_dms_logger():
    """기본 DMS 로거 (서버 로거와 동일)"""
    return get_server_logger()

def setup_flask_logging(app):
    """Flask 애플리케이션에 서버 로깅 설정 적용"""
    server_logger = get_server_logger()
    
    # Flask 기본 로거 설정
    app.logger.handlers.clear()
    app.logger.addHandler(server_logger.get_logger().handlers[0])  # 콘솔 핸들러
    app.logger.addHandler(server_logger.get_logger().handlers[1])  # 파일 핸들러
    app.logger.setLevel(logging.INFO)
    
    # 서버 시작 로그
    server_logger.get_logger().info("=" * 50)
    server_logger.get_logger().info("DMS Flask Server Starting...")
    server_logger.get_logger().info(f"Session ID: {server_logger.session_id}")
    server_logger.get_logger().info(f"Process ID: {os.getpid()}")
    server_logger.get_logger().info("=" * 50)
    
    return server_logger

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