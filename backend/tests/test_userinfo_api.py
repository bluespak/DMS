import unittest
import json
import sys
import os

# 프로젝트 루트 경로를 Python path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from test_config import BaseTestCase

class TestUserInfoAPI(BaseTestCase):
    """UserInfo API 테스트 클래스"""
    
    def test_get_all_users_empty(self):
        """빈 사용자 목록 조회 테스트"""
        response = self.client.get('/api/userinfo')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)
    
    def test_create_user_success(self):
        """사용자 생성 성공 테스트"""
        user_data = {
            'LastName': 'Doe',
            'FirstName': 'John',
            'Email': 'john@example.com',
            'Grade': 'A',
            'DOB': '1990-01-01'
        }
        
        response = self.client.post('/api/userinfo', json=user_data)
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertEqual(data['LastName'], 'Doe')
        self.assertEqual(data['FirstName'], 'John')
        self.assertEqual(data['Email'], 'john@example.com')
    
    def test_create_user_no_data(self):
        """데이터 없이 사용자 생성 실패 테스트"""
        response = self.client.post('/api/userinfo', json={})
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'No data provided')
    
    def test_create_user_invalid_date(self):
        """잘못된 날짜 형식으로 사용자 생성 실패 테스트"""
        user_data = {
            'LastName': 'Doe',
            'FirstName': 'John',
            'Email': 'john@example.com',
            'Grade': 'A',
            'DOB': 'invalid-date'
        }
        
        response = self.client.post('/api/userinfo', json=user_data)
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_get_user_by_id_success(self):
        """사용자 ID로 조회 성공 테스트"""
        # 먼저 사용자 생성
        user_data = {
            'LastName': 'Doe',
            'FirstName': 'John',
            'Email': 'john@example.com',
            'Grade': 'A',
            'DOB': '1990-01-01'
        }
        
        create_response = self.client.post('/api/userinfo', json=user_data)
        self.assertEqual(create_response.status_code, 201)
        
        created_user = json.loads(create_response.data)
        user_id = created_user['id']
        
        # 사용자 조회
        response = self.client.get(f'/api/userinfo/{user_id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['id'], user_id)
        self.assertEqual(data['LastName'], 'Doe')
    
    def test_get_user_by_id_not_found(self):
        """존재하지 않는 사용자 조회 실패 테스트"""
        response = self.client.get('/api/userinfo/999')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_update_user_success(self):
        """사용자 정보 수정 성공 테스트"""
        # 먼저 사용자 생성
        user_data = {
            'LastName': 'Doe',
            'FirstName': 'John',
            'Email': 'john@example.com',
            'Grade': 'A',
            'DOB': '1990-01-01'
        }
        
        create_response = self.client.post('/api/userinfo', json=user_data)
        created_user = json.loads(create_response.data)
        user_id = created_user['id']
        
        # 사용자 정보 수정
        update_data = {
            'LastName': 'Smith',
            'Grade': 'B'
        }
        
        response = self.client.put(f'/api/userinfo/{user_id}', json=update_data)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['LastName'], 'Smith')
        self.assertEqual(data['Grade'], 'B')
        self.assertEqual(data['FirstName'], 'John')  # 변경되지 않은 값
    
    def test_update_user_not_found(self):
        """존재하지 않는 사용자 수정 실패 테스트"""
        update_data = {
            'LastName': 'Smith'
        }
        
        response = self.client.put('/api/userinfo/999', json=update_data)
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_delete_user_success(self):
        """사용자 삭제 성공 테스트"""
        # 먼저 사용자 생성
        user_data = {
            'LastName': 'Doe',
            'FirstName': 'John',
            'Email': 'john@example.com',
            'Grade': 'A',
            'DOB': '1990-01-01'
        }
        
        create_response = self.client.post('/api/userinfo', json=user_data)
        created_user = json.loads(create_response.data)
        user_id = created_user['id']
        
        # 사용자 삭제
        response = self.client.delete(f'/api/userinfo/{user_id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('message', data)
        
        # 삭제 확인
        get_response = self.client.get(f'/api/userinfo/{user_id}')
        self.assertEqual(get_response.status_code, 404)
    
    def test_delete_user_not_found(self):
        """존재하지 않는 사용자 삭제 실패 테스트"""
        response = self.client.delete('/api/userinfo/999')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_get_all_users_with_data(self):
        """사용자 목록 조회 (데이터 있음) 테스트"""
        # 여러 사용자 생성
        users_data = [
            {
                'LastName': 'Doe',
                'FirstName': 'John',
                'Email': 'john@example.com',
                'Grade': 'A',
                'DOB': '1990-01-01'
            },
            {
                'LastName': 'Smith',
                'FirstName': 'Jane',
                'Email': 'jane@example.com',
                'Grade': 'B',
                'DOB': '1992-05-15'
            }
        ]
        
        for user_data in users_data:
            self.client.post('/api/userinfo', json=user_data)
        
        # 사용자 목록 조회
        response = self.client.get('/api/userinfo')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)

if __name__ == '__main__':
    unittest.main()