from flask import Blueprint, jsonify
import os
import logging
import subprocess
from datetime import datetime

# 로거 설정
logger = logging.getLogger(__name__)

def init_system_routes(db):
    """시스템 관리 라우트를 초기화하는 함수"""
    
    system_bp = Blueprint('system', __name__)
    
    def test_db_connection():
        """데이터베이스 연결 테스트"""
        try:
            # 간단한 쿼리로 연결 테스트 (SQLAlchemy 2.x 호환)
            with db.engine.connect() as connection:
                result = connection.execute(db.text('SELECT 1'))
                result.fetchone()
            logger.info("✅ 데이터베이스 연결 성공!")
            return True
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 실패: {e}")
            return False
    
    @system_bp.route('/api/health', methods=['GET'])
    def health_check():
        """시스템 상태 확인"""
        # 데이터베이스 연결 상태 확인
        db_status = test_db_connection()
        
        response = {
            'status': 'ok',
            'database': 'connected' if db_status else 'disconnected',
            'message': 'Database connection successful' if db_status else 'Database connection failed'
        }
        
        logger.info(f"Health check - Database: {'✅ Connected' if db_status else '❌ Disconnected'}")
        
        return jsonify(response)
    
    @system_bp.route('/api/docs', methods=['GET'])
    def api_docs():
        """API 문서 페이지 서빙"""
        try:
            # 현재 파일에서 프로젝트 루트까지의 경로 계산
            current_dir = os.path.dirname(os.path.abspath(__file__))  # route 폴더
            backend_dir = os.path.dirname(current_dir)  # backend 폴더
            doc_path = os.path.join(backend_dir, 'doc', 'api-documentation.html')
            
            logger.info(f"API 문서 경로: {doc_path}")
            logger.info(f"파일 존재 여부: {os.path.exists(doc_path)}")
            
            with open(doc_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            return html_content
        except FileNotFoundError:
            return jsonify({
                'success': False,
                'error': 'API documentation not found'
            }), 404
        except Exception as e:
            logger.error(f"❌ API 문서 로드 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return system_bp