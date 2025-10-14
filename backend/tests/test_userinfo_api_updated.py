import unittest
import json
from test_config import BaseTestCase

class TestUserInfoAPIUpdated(BaseTestCase):
    """UserInfo API 테스트 - 업데이트된 스키마 및 엔드포인트 사용 (MySQL 테스트 DB)"""
    
    def test_get_all_users_empty(self):
        """빈 사용자 목록 조회 테스트"""
        response = self.client.get('/api/users')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)
    
    def test_create_user_success(self):
        """사용자 생성 성공 테스트"""
        user_data = {
            'user_id': 'john.doe.001',
            'lastname': 'Doe',
            'firstname': 'John',
            'email': 'john@example.com',
            'grade': 'A',
            'DOB': '1990-01-01'
        }
        
        response = self.client.post('/api/users', json=user_data)
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertEqual(data['lastname'], 'Doe')
        self.assertEqual(data['firstname'], 'John')
        self.assertEqual(data['email'], 'john@example.com')
    
    def test_create_user_no_data(self):
        """데이터 없이 사용자 생성 실패 테스트"""
        response = self.client.post('/api/users', json={})
        self.assertEqual(response.status_code, 400)
    
    def test_create_user_duplicate_user_id(self):
        """중복 user_id로 사용자 생성 실패 테스트"""
        user_data = {
            'user_id': 'john.doe.001',
            'lastname': 'Doe',
            'firstname': 'John',
            'email': 'john@example.com',
            'grade': 'A',
            'DOB': '1990-01-01'
        }
        
        # 첫 번째 사용자 생성
        response1 = self.client.post('/api/users', json=user_data)
        self.assertEqual(response1.status_code, 201)
        
        # 동일한 user_id로 두 번째 사용자 생성 시도
        response2 = self.client.post('/api/users', json=user_data)
        self.assertEqual(response2.status_code, 400)
    
    def test_get_user_by_id_success(self):
        """사용자 ID로 조회 성공 테스트"""
        # 테스트용 사용자 생성
        user_data = {
            'user_id': 'john.doe.001',
            'lastname': 'Doe',
            'firstname': 'John',
            'email': 'john@example.com',
            'grade': 'A',
            'DOB': '1990-01-01'
        }
        
        create_response = self.client.post('/api/users', json=user_data)
        self.assertEqual(create_response.status_code, 201)
        
        created_user = json.loads(create_response.data)
        user_id = created_user['id']
        
        # 생성된 사용자 조회
        response = self.client.get(f'/api/users/{user_id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['lastname'], 'Doe')
    
    def test_get_user_by_id_not_found(self):
        """존재하지 않는 사용자 조회 실패 테스트"""
        response = self.client.get('/api/users/999')
        self.assertEqual(response.status_code, 404)
    
    def test_update_user_success(self):
        """사용자 정보 수정 성공 테스트"""
        # 테스트용 사용자 생성
        user_data = {
            'user_id': 'john.doe.001',
            'lastname': 'Doe',
            'firstname': 'John',
            'email': 'john@example.com',
            'grade': 'A',
            'DOB': '1990-01-01'
        }
        
        create_response = self.client.post('/api/users', json=user_data)
        self.assertEqual(create_response.status_code, 201)
        
        created_user = json.loads(create_response.data)
        user_id = created_user['id']
        
        # 사용자 정보 수정
        update_data = {
            'lastname': 'Smith',
            'grade': 'B'
        }
        
        response = self.client.put(f'/api/users/{user_id}', json=update_data)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['lastname'], 'Smith')
        self.assertEqual(data['grade'], 'B')
        # 수정하지 않은 필드는 그대로 유지
        self.assertEqual(data['firstname'], 'John')
    
    def test_update_user_not_found(self):
        """존재하지 않는 사용자 수정 실패 테스트"""
        update_data = {
            'lastname': 'Smith'
        }
        
        response = self.client.put('/api/users/999', json=update_data)
        self.assertEqual(response.status_code, 404)
    
    def test_delete_user_success(self):
        """사용자 삭제 성공 테스트"""
        # 테스트용 사용자 생성
        user_data = {
            'user_id': 'john.doe.001',
            'lastname': 'Doe',
            'firstname': 'John',
            'email': 'john@example.com',
            'grade': 'A',
            'DOB': '1990-01-01'
        }
        
        create_response = self.client.post('/api/users', json=user_data)
        self.assertEqual(create_response.status_code, 201)
        
        created_user = json.loads(create_response.data)
        user_id = created_user['id']
        
        # 사용자 삭제
        response = self.client.delete(f'/api/users/{user_id}')
        self.assertEqual(response.status_code, 200)
        
        # 삭제된 사용자 조회 시 404 확인
        get_response = self.client.get(f'/api/users/{user_id}')
        self.assertEqual(get_response.status_code, 404)
    
    def test_delete_user_not_found(self):
        """존재하지 않는 사용자 삭제 실패 테스트"""
        response = self.client.delete('/api/users/999')
        self.assertEqual(response.status_code, 404)
    
    def test_get_all_users_with_data(self):
        """사용자 목록 조회 (데이터 있음) 테스트"""
        # 테스트용 사용자들 생성
        users_data = [
            {
                'user_id': 'john.doe.001',
                'lastname': 'Doe',
                'firstname': 'John',
                'email': 'john@example.com',
                'grade': 'A',
                'DOB': '1990-01-01'
            },
            {
                'user_id': 'jane.smith.002',
                'lastname': 'Smith', 
                'firstname': 'Jane',
                'email': 'jane@example.com',
                'grade': 'B',
                'DOB': '1992-02-02'
            }
        ]
        
        for user_data in users_data:
            response = self.client.post('/api/users', json=user_data)
            self.assertEqual(response.status_code, 201)
        
        # 모든 사용자 조회
        response = self.client.get('/api/users')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)

if __name__ == '__main__':
    unittest.main()