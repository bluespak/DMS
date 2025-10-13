import unittest
import json
from datetime import datetime
from test_config import BaseTestCase

class TestDispatchLogAPI(BaseTestCase):
    """DispatchLog API 테스트"""
    
    def setUp(self):
        """테스트 설정 - 테스트용 유언장과 수신자 생성"""
        super().setUp()
        
        # 테스트용 사용자 생성
        user_data = {
            'LastName': '테스트',
            'FirstName': '사용자',
            'Email': 'test@example.com',
            'Grade': 'A',
            'DOB': '1990-01-01'
        }
        
        user_response = self.client.post('/api/userinfo',
                                       data=json.dumps(user_data),
                                       content_type='application/json')
        
        if user_response.status_code == 201:
            self.test_user = json.loads(user_response.data)
        else:
            raise Exception(f"테스트 사용자 생성 실패: {user_response.status_code}")
        
        # 테스트용 유언장 생성
        will_data = {
            'user_id': self.test_user['id'],
            'subject': '테스트 유언장',
            'body': '테스트 내용'
        }
        
        will_response = self.client.post('/api/wills',
                                       data=json.dumps(will_data),
                                       content_type='application/json')
        self.test_will = json.loads(will_response.data)['data']
        self.test_will_id = self.test_will['id']
        
        # 테스트용 수신자 생성
        recipient_data = {
            'will_id': self.test_will_id,
            'recipient_email': 'recipient@example.com',
            'recipient_name': '테스트 수신자'
        }
        
        recipient_response = self.client.post('/api/recipients',
                                            data=json.dumps(recipient_data),
                                            content_type='application/json')
        self.test_recipient = json.loads(recipient_response.data)['data']
        self.test_recipient_id = self.test_recipient['id']
    
    def test_get_all_dispatch_logs_empty(self):
        """빈 발송 로그 목록 조회 테스트"""
        response = self.client.get('/api/dispatch-logs')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 0)
    
    def test_create_dispatch_log_success(self):
        """발송 로그 생성 성공 테스트"""
        log_data = {
            'will_id': self.test_will_id,
            'recipient_id': self.test_recipient_id,
            'status': 'pending'
        }
        
        response = self.client.post('/api/dispatch-logs',
                                  data=json.dumps(log_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['will_id'], self.test_will_id)
        self.assertEqual(data['data']['recipient_id'], self.test_recipient_id)
        self.assertEqual(data['data']['status'], 'pending')
    
    def test_create_dispatch_log_with_sent_at(self):
        """sent_at 포함한 발송 로그 생성 테스트"""
        sent_at = datetime.now().isoformat()
        log_data = {
            'will_id': self.test_will_id,
            'recipient_id': self.test_recipient_id,
            'sent_at': sent_at,
            'status': 'sent'
        }
        
        response = self.client.post('/api/dispatch-logs',
                                  data=json.dumps(log_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['status'], 'sent')
        self.assertIsNotNone(data['data']['sent_at'])
    
    def test_create_dispatch_log_invalid_status(self):
        """잘못된 상태로 발송 로그 생성 실패 테스트"""
        log_data = {
            'will_id': self.test_will_id,
            'recipient_id': self.test_recipient_id,
            'status': 'invalid_status'
        }
        
        response = self.client.post('/api/dispatch-logs',
                                  data=json.dumps(log_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Invalid status', data['error'])
    
    def test_create_dispatch_log_missing_required_fields(self):
        """필수 필드 누락으로 발송 로그 생성 실패 테스트"""
        log_data = {
            'will_id': self.test_will_id,
            'status': 'pending'
            # recipient_id 누락
        }
        
        response = self.client.post('/api/dispatch-logs',
                                  data=json.dumps(log_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Missing required fields', data['error'])
    
    def test_get_logs_by_will_id(self):
        """특정 유언장의 발송 로그들 조회 테스트"""
        # 해당 유언장에 여러 발송 로그 생성
        logs_data = [
            {
                'will_id': self.test_will_id,
                'recipient_id': self.test_recipient_id,
                'status': 'pending'
            },
            {
                'will_id': self.test_will_id,
                'recipient_id': self.test_recipient_id,
                'status': 'sent'
            }
        ]
        
        for log_data in logs_data:
            self.client.post('/api/dispatch-logs',
                           data=json.dumps(log_data),
                           content_type='application/json')
        
        # 특정 유언장의 발송 로그들 조회
        response = self.client.get(f'/api/dispatch-logs/will/{self.test_will_id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 2)
    
    def test_get_logs_by_recipient_id(self):
        """특정 수신자의 발송 로그들 조회 테스트"""
        # 해당 수신자에 발송 로그 생성
        log_data = {
            'will_id': self.test_will_id,
            'recipient_id': self.test_recipient_id,
            'status': 'sent'
        }
        
        self.client.post('/api/dispatch-logs',
                       data=json.dumps(log_data),
                       content_type='application/json')
        
        # 특정 수신자의 발송 로그들 조회
        response = self.client.get(f'/api/dispatch-logs/recipient/{self.test_recipient_id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['data'][0]['recipient_id'], self.test_recipient_id)
    
    def test_update_dispatch_log_success(self):
        """발송 로그 수정 성공 테스트"""
        # 먼저 발송 로그 생성
        log_data = {
            'will_id': self.test_will_id,
            'recipient_id': self.test_recipient_id,
            'status': 'pending'
        }
        
        create_response = self.client.post('/api/dispatch-logs',
                                         data=json.dumps(log_data),
                                         content_type='application/json')
        created_log = json.loads(create_response.data)['data']
        log_id = created_log['id']
        
        # 발송 로그 수정
        update_data = {
            'status': 'sent',
            'sent_at': datetime.now().isoformat()
        }
        
        response = self.client.put(f'/api/dispatch-logs/{log_id}',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['status'], 'sent')
        self.assertIsNotNone(data['data']['sent_at'])
    
    def test_delete_dispatch_log_success(self):
        """발송 로그 삭제 성공 테스트"""
        # 먼저 발송 로그 생성
        log_data = {
            'will_id': self.test_will_id,
            'recipient_id': self.test_recipient_id,
            'status': 'failed'
        }
        
        create_response = self.client.post('/api/dispatch-logs',
                                         data=json.dumps(log_data),
                                         content_type='application/json')
        created_log = json.loads(create_response.data)['data']
        log_id = created_log['id']
        
        # 발송 로그 삭제
        response = self.client.delete(f'/api/dispatch-logs/{log_id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # 삭제된 발송 로그 조회 시 404 확인
        get_response = self.client.get(f'/api/dispatch-logs/{log_id}')
        self.assertEqual(get_response.status_code, 404)
    
    def test_get_all_dispatch_logs_with_data(self):
        """발송 로그 목록 조회 (데이터 있음) 테스트"""
        # 여러 발송 로그 생성
        logs_data = [
            {
                'will_id': self.test_will_id,
                'recipient_id': self.test_recipient_id,
                'status': 'pending'
            },
            {
                'will_id': self.test_will_id,
                'recipient_id': self.test_recipient_id,
                'status': 'sent'
            },
            {
                'will_id': self.test_will_id,
                'recipient_id': self.test_recipient_id,
                'status': 'failed'
            }
        ]
        
        for log_data in logs_data:
            self.client.post('/api/dispatch-logs',
                           data=json.dumps(log_data),
                           content_type='application/json')
        
        # 모든 발송 로그 조회
        response = self.client.get('/api/dispatch-logs')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 3)

if __name__ == '__main__':
    unittest.main()