"""
Simple API connectivity test to verify the endpoints are working
"""
import unittest
import json
import sys
import os

# 프로젝트 루트 경로를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.app import app

class TestAPIConnectivity(unittest.TestCase):
    """API 연결성 테스트"""
    
    def setUp(self):
        """테스트 전 설정"""
        self.app = app
        self.app.config['TESTING'] = True
        # MySQL 테스트 데이터베이스 사용
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://dmsTestUser:dmstest2025!@localhost/dmsdb_test'
        self.client = self.app.test_client()
        
        # 테스트용 데이터베이스 테이블 생성
        with self.app.app_context():
            from app.app import db
            db.create_all()
            # 기존 테스트 데이터 정리
            db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 0'))
            for table in reversed(db.metadata.sorted_tables):
                db.session.execute(table.delete())
            db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 1'))
            db.session.commit()
    
    def tearDown(self):
        """테스트 후 정리"""
        with self.app.app_context():
            from app.app import db
            # 테스트 데이터 정리 (테이블은 유지)
            db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 0'))
            for table in reversed(db.metadata.sorted_tables):
                db.session.execute(table.delete())
            db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 1'))
            db.session.commit()
    
    def test_api_users_get_empty(self):
        """빈 사용자 목록 조회 테스트"""
        response = self.client.get('/api/users')
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data.decode()}")
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('data', data)
        self.assertEqual(len(data['data']), 0)
    
    def test_api_users_post_create(self):
        """사용자 생성 테스트"""
        user_data = {
            'user_id': 'test.user.001',
            'lastname': 'Test',
            'firstname': 'User',
            'email': 'test@example.com',
            'grade': 'A',
            'DOB': '1990-01-01'
        }
        
        response = self.client.post('/api/users', json=user_data)
        print(f"Create response status: {response.status_code}")
        print(f"Create response data: {response.data.decode()}")
        
        if response.status_code != 201:
            # 에러 상세 정보 출력
            print(f"Error creating user: {response.data.decode()}")
        
        self.assertEqual(response.status_code, 201)
        
        # 생성된 사용자 확인
        data = json.loads(response.data)
        self.assertIn('data', data)
        user_data = data['data']
        self.assertEqual(user_data['user_id'], 'test.user.001')
        self.assertEqual(user_data['email'], 'test@example.com')

if __name__ == '__main__':
    unittest.main(verbosity=2)