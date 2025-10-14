import unittest
import json
from test_config import BaseTestCase

class TestRecipientsAPI(BaseTestCase):
    """Recipients API 테스트"""
    
    def setUp(self):
        """테스트 전 실행되는 메서드"""
        super().setUp()
        
        # 테스트용 사용자 생성
        user_data = {
            'LastName': '테스트',
            'FirstName': '사용자',
            'Email': 'test@example.com',
            'Grade': 'A',
            'DOB': '1990-01-01'
        }
        
        user_response = self.client.post('/api/users',
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
        
        response = self.client.post('/api/wills',
                                  data=json.dumps(will_data),
                                  content_type='application/json')
        self.test_will = json.loads(response.data)['data']
        self.test_will_id = self.test_will['id']
    
    def test_get_all_recipients_empty(self):
        """빈 수신자 목록 조회 테스트"""
        response = self.client.get('/api/recipients')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 0)
        self.assertEqual(len(data['data']), 0)
    
    def test_create_recipient_success(self):
        """수신자 생성 성공 테스트"""
        recipient_data = {
            'will_id': self.test_will_id,
            'recipient_email': 'recipient@example.com',
            'recipient_name': '홍길동',
            'relatedCode': 'A'
        }
        
        response = self.client.post('/api/recipients',
                                  data=json.dumps(recipient_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertEqual(data['data']['will_id'], self.test_will_id)
        self.assertEqual(data['data']['recipient_email'], 'recipient@example.com')
        self.assertEqual(data['data']['recipient_name'], '홍길동')
        self.assertEqual(data['data']['relatedCode'], 'A')
    
    def test_create_recipient_missing_required_fields(self):
        """필수 필드 누락으로 수신자 생성 실패 테스트"""
        # will_id 누락
        recipient_data = {
            'recipient_email': 'test@example.com',
            'recipient_name': '테스트'
        }
        
        response = self.client.post('/api/recipients',
                                  data=json.dumps(recipient_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Missing required fields', data['error'])
    
    def test_create_recipient_no_data(self):
        """데이터 없이 수신자 생성 실패 테스트"""
        response = self.client.post('/api/recipients',
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('No data provided', data['error'])
    
    def test_get_recipient_by_id_success(self):
        """수신자 ID로 조회 성공 테스트"""
        # 먼저 수신자 생성
        recipient_data = {
            'will_id': self.test_will_id,
            'recipient_email': 'test@example.com',
            'recipient_name': '테스트 사용자',
            'relatedCode': 'B'
        }
        
        create_response = self.client.post('/api/recipients',
                                         data=json.dumps(recipient_data),
                                         content_type='application/json')
        created_recipient = json.loads(create_response.data)['data']
        recipient_id = created_recipient['id']
        
        # 생성된 수신자 조회
        response = self.client.get(f'/api/recipients/{recipient_id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['id'], recipient_id)
        self.assertEqual(data['data']['recipient_name'], '테스트 사용자')
    
    def test_get_recipient_by_id_not_found(self):
        """존재하지 않는 수신자 조회 실패 테스트"""
        response = self.client.get('/api/recipients/999')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Recipient not found')
    
    def test_get_recipients_by_will_id(self):
        """특정 유언장의 수신자들 조회 테스트"""
        # 해당 유언장에 여러 수신자 생성
        recipients_data = [
            {
                'will_id': self.test_will_id,
                'recipient_email': 'user1@example.com',
                'recipient_name': '사용자1',
                'relatedCode': 'A'
            },
            {
                'will_id': self.test_will_id,
                'recipient_email': 'user2@example.com',
                'recipient_name': '사용자2',
                'relatedCode': 'B'
            }
        ]
        
        for recipient_data in recipients_data:
            self.client.post('/api/recipients',
                           data=json.dumps(recipient_data),
                           content_type='application/json')
        
        # 특정 유언장의 수신자들 조회
        response = self.client.get(f'/api/recipients/will/{self.test_will_id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 2)
        self.assertEqual(len(data['data']), 2)
    
    def test_update_recipient_success(self):
        """수신자 정보 수정 성공 테스트"""
        # 먼저 수신자 생성
        recipient_data = {
            'will_id': self.test_will_id,
            'recipient_email': 'original@example.com',
            'recipient_name': '원본 이름',
            'relatedCode': 'A'
        }
        
        create_response = self.client.post('/api/recipients',
                                         data=json.dumps(recipient_data),
                                         content_type='application/json')
        created_recipient = json.loads(create_response.data)['data']
        recipient_id = created_recipient['id']
        
        # 수신자 정보 수정
        update_data = {
            'recipient_email': 'updated@example.com',
            'recipient_name': '수정된 이름',
            'relatedCode': 'B'
        }
        
        response = self.client.put(f'/api/recipients/{recipient_id}',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['recipient_email'], 'updated@example.com')
        self.assertEqual(data['data']['recipient_name'], '수정된 이름')
        self.assertEqual(data['data']['relatedCode'], 'B')
    
    def test_update_recipient_not_found(self):
        """존재하지 않는 수신자 수정 실패 테스트"""
        update_data = {'recipient_name': '새 이름'}
        
        response = self.client.put('/api/recipients/999',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Recipient not found')
    
    def test_delete_recipient_success(self):
        """수신자 삭제 성공 테스트"""
        # 먼저 수신자 생성
        recipient_data = {
            'will_id': self.test_will_id,
            'recipient_email': 'delete@example.com',
            'recipient_name': '삭제될 사용자'
        }
        
        create_response = self.client.post('/api/recipients',
                                         data=json.dumps(recipient_data),
                                         content_type='application/json')
        created_recipient = json.loads(create_response.data)['data']
        recipient_id = created_recipient['id']
        
        # 수신자 삭제
        response = self.client.delete(f'/api/recipients/{recipient_id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # 삭제된 수신자 조회 시 404 확인
        get_response = self.client.get(f'/api/recipients/{recipient_id}')
        self.assertEqual(get_response.status_code, 404)
    
    def test_delete_recipient_not_found(self):
        """존재하지 않는 수신자 삭제 실패 테스트"""
        response = self.client.delete('/api/recipients/999')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Recipient not found')
    
    def test_get_all_recipients_with_data(self):
        """수신자 목록 조회 (데이터 있음) 테스트"""
        # 여러 수신자 생성
        recipients_data = [
            {
                'will_id': self.test_will_id,
                'recipient_email': 'recipient1@example.com',
                'recipient_name': '수신자1'
            },
            {
                'will_id': self.test_will_id,
                'recipient_email': 'recipient2@example.com',
                'recipient_name': '수신자2'
            },
            {
                'will_id': self.test_will_id,
                'recipient_email': 'recipient3@example.com',
                'recipient_name': '수신자3'
            }
        ]
        
        for recipient_data in recipients_data:
            self.client.post('/api/recipients',
                           data=json.dumps(recipient_data),
                           content_type='application/json')
        
        # 모든 수신자 조회
        response = self.client.get('/api/recipients')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 3)
        self.assertEqual(len(data['data']), 3)

if __name__ == '__main__':
    unittest.main()