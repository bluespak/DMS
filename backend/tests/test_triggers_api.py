import unittest
import json
from datetime import datetime
from test_config import BaseTestCase

class TestTriggersAPI(BaseTestCase):
    """Triggers API 테스트"""
    
    def setUp(self):
        """테스트 설정 - 테스트용 사용자 생성"""
        super().setUp()
        
        # 테스트용 사용자 생성
        user_data = {
            'LastName': '테스트',
            'FirstName': '사용자',
            'Email': 'testuser@example.com',
            'Grade': 'A'
        }
        
        response = self.client.post('/api/userinfo',
                                  data=json.dumps(user_data),
                                  content_type='application/json')
        self.test_user = json.loads(response.data)
        self.test_user_id = self.test_user['id']
    
    def test_get_all_triggers_empty(self):
        """빈 트리거 목록 조회 테스트"""
        response = self.client.get('/api/triggers')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 0)
    
    def test_create_trigger_success(self):
        """트리거 생성 성공 테스트"""
        trigger_data = {
            'user_id': self.test_user_id,
            'trigger_type': 'inactivity',
            'trigger_value': '30',
            'is_triggered': False
        }
        
        response = self.client.post('/api/triggers',
                                  data=json.dumps(trigger_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['user_id'], self.test_user_id)
        self.assertEqual(data['data']['trigger_type'], 'inactivity')
        self.assertEqual(data['data']['trigger_value'], '30')
        self.assertFalse(data['data']['is_triggered'])
    
    def test_create_trigger_invalid_type(self):
        """잘못된 트리거 타입으로 생성 실패 테스트"""
        trigger_data = {
            'user_id': self.test_user_id,
            'trigger_type': 'invalid_type',
            'trigger_value': '30'
        }
        
        response = self.client.post('/api/triggers',
                                  data=json.dumps(trigger_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Invalid trigger type', data['error'])
    
    def test_create_trigger_missing_required_fields(self):
        """필수 필드 누락으로 트리거 생성 실패 테스트"""
        trigger_data = {
            'trigger_type': 'inactivity',
            'trigger_value': '30'
        }
        
        response = self.client.post('/api/triggers',
                                  data=json.dumps(trigger_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Missing required fields', data['error'])
    
    def test_get_triggers_by_user_id(self):
        """특정 사용자의 트리거들 조회 테스트"""
        # 해당 사용자에 여러 트리거 생성
        triggers_data = [
            {
                'user_id': self.test_user_id,
                'trigger_type': 'inactivity',
                'trigger_value': '30'
            },
            {
                'user_id': self.test_user_id,
                'trigger_type': 'date',
                'trigger_value': '2024-12-31'
            }
        ]
        
        for trigger_data in triggers_data:
            self.client.post('/api/triggers',
                           data=json.dumps(trigger_data),
                           content_type='application/json')
        
        # 특정 사용자의 트리거들 조회
        response = self.client.get(f'/api/triggers/user/{self.test_user_id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 2)
    
    def test_update_trigger_success(self):
        """트리거 수정 성공 테스트"""
        # 먼저 트리거 생성
        trigger_data = {
            'user_id': self.test_user_id,
            'trigger_type': 'inactivity',
            'trigger_value': '30',
            'is_triggered': False
        }
        
        create_response = self.client.post('/api/triggers',
                                         data=json.dumps(trigger_data),
                                         content_type='application/json')
        created_trigger = json.loads(create_response.data)['data']
        trigger_id = created_trigger['id']
        
        # 트리거 수정
        update_data = {
            'trigger_value': '60',
            'is_triggered': True
        }
        
        response = self.client.put(f'/api/triggers/{trigger_id}',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['trigger_value'], '60')
        self.assertTrue(data['data']['is_triggered'])
    
    def test_delete_trigger_success(self):
        """트리거 삭제 성공 테스트"""
        # 먼저 트리거 생성
        trigger_data = {
            'user_id': self.test_user_id,
            'trigger_type': 'manual',
            'trigger_value': 'test'
        }
        
        create_response = self.client.post('/api/triggers',
                                         data=json.dumps(trigger_data),
                                         content_type='application/json')
        created_trigger = json.loads(create_response.data)['data']
        trigger_id = created_trigger['id']
        
        # 트리거 삭제
        response = self.client.delete(f'/api/triggers/{trigger_id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # 삭제된 트리거 조회 시 404 확인
        get_response = self.client.get(f'/api/triggers/{trigger_id}')
        self.assertEqual(get_response.status_code, 404)

if __name__ == '__main__':
    unittest.main()