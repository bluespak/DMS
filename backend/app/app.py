from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import sys
import os
from dotenv import load_dotenv
import logging

# .env 파일 로드
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# 모델과 라우트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

app = Flask(__name__)
CORS(app)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)

# 모델 임포트 및 초기화
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models'))
from userinfo import create_userinfo_model
from will import create_will_model
from recipients import create_recipient_model
from trigger import create_trigger_model
from dispatchlog import create_dispatchlog_model

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

# 모델 생성
UserInfo = create_userinfo_model(db)
Will = create_will_model(db)
Recipient = create_recipient_model(db)
Trigger = create_trigger_model(db)
DispatchLog = create_dispatchlog_model(db)

# 라우트 초기화 및 등록
app.register_blueprint(init_userinfo_routes(db, UserInfo))
app.register_blueprint(init_will_routes(db, Will))
app.register_blueprint(init_recipients_routes(db, Recipient))
app.register_blueprint(init_triggers_routes(db, Trigger))
app.register_blueprint(init_dispatchlog_routes(db, DispatchLog))
app.register_blueprint(init_system_routes(db))
app.register_blueprint(init_test_routes())
app.register_blueprint(init_home_routes())

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



if __name__ == '__main__':
    logger.info("🚀 Flask 애플리케이션 시작 중...")
    logger.info(f"데이터베이스 URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
    app.run(debug=True)