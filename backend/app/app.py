from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import sys
import os
import time
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# 모델과 라우트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from utils.logging_config import setup_flask_logging, get_dms_logger

app = Flask(__name__)
CORS(app, supports_credentials=True)

# DMS 로깅 시스템 설정 - 서버 로그 사용
dms_logger = setup_flask_logging(app)
logger = dms_logger.get_logger()
api_logger = dms_logger.get_api_logger()

app.config.from_object(Config)

db = SQLAlchemy(app)

# 모델 임포트 및 초기화
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models'))
from userinfo import create_userinfo_model
from will import create_will_model
from recipients import create_recipient_model
from trigger import create_trigger_model
from dispatchlog import create_dispatchlog_model
from will_blockchain import (
    create_blockchain_event_model,
    create_blockchain_outbox_model,
    create_will_version_model,
)

# 라우트 임포트 및 등록
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'routes'))
from userinfo_routes import init_userinfo_routes
from will_routes import init_will_routes
from recipients_routes import init_recipients_routes
from triggers_routes import init_triggers_routes
from dispatchlog_routes import init_dispatchlog_routes
from system_routes import init_system_routes
from test_routes import init_test_routes
from home_routes import init_home_routes
from frontend_log_routes import init_frontend_log_routes
from auth_routes import init_auth_routes
from liveconfirmation_routes import init_liveconfirmation_routes

# 모델 생성
UserInfo = create_userinfo_model(db)
Will = create_will_model(db)
Recipient = create_recipient_model(db)
Trigger = create_trigger_model(db)
DispatchLog = create_dispatchlog_model(db)
WillVersion = create_will_version_model(db)
BlockchainEvent = create_blockchain_event_model(db)
BlockchainOutbox = create_blockchain_outbox_model(db)

# API 요청 로깅 미들웨어
@app.before_request
def log_request_info():
    """요청 시작 시 로깅"""
    g.start_time = time.time()
    
    # 정적 파일 요청은 로깅하지 않음
    if request.endpoint == 'static':
        return
    
    logger.debug(f"API Request: {request.method} {request.path} | IP: {request.remote_addr}")

@app.after_request
def log_response_info(response):
    """응답 완료 시 로깅"""
    # 정적 파일 요청은 로깅하지 않음
    if request.endpoint == 'static':
        return response
    
    if hasattr(g, 'start_time'):
        response_time = time.time() - g.start_time
        
        # API 요청 로그 기록
        dms_logger.log_api_request(
            method=request.method,
            endpoint=request.path,
            ip=request.remote_addr,
            status_code=response.status_code,
            response_time=response_time
        )
        
        # 에러 상태 코드인 경우 추가 로깅
        if response.status_code >= 400:
            logger.warning(f"API Error: {request.method} {request.path} | Status: {response.status_code} | IP: {request.remote_addr}")
    
    return response

# 전역 에러 핸들러
@app.errorhandler(Exception)
def handle_exception(e):
    """전역 예외 처리 및 로깅"""
    logger.error(f"Unhandled Exception: {str(e)} | Path: {request.path} | Method: {request.method} | IP: {request.remote_addr}", exc_info=True)
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

@app.errorhandler(404)
def not_found(error):
    """404 에러 처리"""
    logger.warning(f"404 Not Found: {request.method} {request.path} | IP: {request.remote_addr}")
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404

# 라우트 초기화 및 등록
app.register_blueprint(init_userinfo_routes(db, UserInfo))
app.register_blueprint(init_will_routes(db, Will, Recipient))
app.register_blueprint(init_recipients_routes(db, Recipient))
app.register_blueprint(init_triggers_routes(db, Trigger))
app.register_blueprint(init_dispatchlog_routes(db, DispatchLog, Recipient))
app.register_blueprint(init_system_routes(db))
app.register_blueprint(init_test_routes())
app.register_blueprint(init_home_routes())
app.register_blueprint(init_auth_routes(db, UserInfo))
app.register_blueprint(init_liveconfirmation_routes(db, DispatchLog))

# Frontend 로그 라우트 초기화
init_frontend_log_routes(app)

# 앱 시작 시 데이터베이스 연결 확인
with app.app_context():
    logger.info("데이터베이스 연결 테스트 중...")
    try:
        # 간단한 쿼리로 연결 테스트 (SQLAlchemy 2.x 호환)
        with db.engine.connect() as connection:
            result = connection.execute(db.text('SELECT 1'))
            result.fetchone()
        logger.info("✅ 데이터베이스 연결 성공!")
    except Exception as e:
        logger.error(f"❌ 데이터베이스 연결 실패: {e}")



def mask_db_uri(uri):
    """데이터베이스 URI에서 비밀번호를 마스킹합니다."""
    if not uri or 'Not configured' in uri:
        return uri
    
    import re
    # mysql+pymysql://user:password@host/db 패턴에서 password 부분을 ****로 마스킹
    masked_uri = re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', uri)
    return masked_uri

if __name__ == '__main__':
    logger.info("🚀 Flask 애플리케이션 시작 중...")
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')
    masked_uri = mask_db_uri(db_uri)
    logger.info(f"데이터베이스 URI: {masked_uri}")
    
    # Docker 환경에서는 0.0.0.0에 바인딩
    import os
    host = os.environ.get('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_RUN_PORT', '5000'))
    logger.info(f"Flask 서버 시작: {host}:{port}")
    
    app.run(debug=True, host=host, port=port)