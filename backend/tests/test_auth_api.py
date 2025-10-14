import unittest
import json
import sys
import os

# 프로젝트 루트 경로를 Python path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from test_config import BaseTestCase

class TestAuthAPI(BaseTestCase):
    """Authentication API 테스트 클래스"""
    
    def test_register_success(self):
        """회원가입 성공 테스트"""
        user_data = {
            'user_id': 'testuser001',
            'password': 'TestPass123!',
            'email': 'test@example.com',
            'firstName': 'Test',
            'lastName': 'User'
        }
        
        response = self.client.post('/api/auth/register',
                                  data=json.dumps(user_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
        self.assertIn('message', data)
    
    def test_register_duplicate_user(self):
        """중복 사용자 가입 테스트"""
        user_data = {
            'user_id': 'testuser001',
            'password': 'TestPass123!',
            'email': 'test@example.com',
            'firstName': 'Test',
            'lastName': 'User'
        }
        
        # 첫 번째 가입
        self.client.post('/api/auth/register',
                        data=json.dumps(user_data),
                        content_type='application/json')
        
        # 두 번째 가입 시도 (중복)
        response = self.client.post('/api/auth/register',
                                  data=json.dumps(user_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data.get('success'))
    
    def test_login_success(self):
        """로그인 성공 테스트"""
        # 먼저 사용자 등록
        user_data = {
            'user_id': 'testuser002',
            'password': 'TestPass123!',
            'email': 'test2@example.com',
            'firstName': 'Test2',
            'lastName': 'User2'
        }
        
        self.client.post('/api/auth/register',
                        data=json.dumps(user_data),
                        content_type='application/json')
        
        # 로그인 시도
        login_data = {
            'user_id': 'testuser002',
            'password': 'TestPass123!'
        }
        
        response = self.client.post('/api/auth/login',
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
        self.assertIn('token', data)
        self.assertIn('user', data)
    
    def test_login_invalid_credentials(self):
        """잘못된 인증 정보로 로그인 테스트"""
        login_data = {
            'user_id': 'nonexistent',
            'password': 'wrongpassword'
        }
        
        response = self.client.post('/api/auth/login',
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertFalse(data.get('success'))
    
    def test_verify_token_valid(self):
        """유효한 토큰 검증 테스트"""
        # 사용자 등록 및 로그인
        user_data = {
            'user_id': 'testuser003',
            'password': 'TestPass123!',
            'email': 'test3@example.com',
            'firstName': 'Test3',
            'lastName': 'User3'
        }
        
        self.client.post('/api/auth/register',
                        data=json.dumps(user_data),
                        content_type='application/json')
        
        login_response = self.client.post('/api/auth/login',
                                        data=json.dumps({
                                            'user_id': 'testuser003',
                                            'password': 'TestPass123!'
                                        }),
                                        content_type='application/json')
        
        login_data = json.loads(login_response.data)
        token = login_data['token']
        
        # 토큰 검증
        response = self.client.get('/api/auth/verify',
                                 headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
        self.assertIn('user', data)
    
    def test_verify_token_invalid(self):
        """유효하지 않은 토큰 검증 테스트"""
        response = self.client.get('/api/auth/verify',
                                 headers={'Authorization': 'Bearer invalidtoken'})
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertFalse(data.get('success'))

if __name__ == '__main__':
    unittest.main()