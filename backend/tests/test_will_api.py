import unittest
import json
from test_config import BaseTestCase

class TestWillAPI(BaseTestCase):
    """Will API 테스트"""
    
    def setUp(self):
        """테스트 전 실행되는 메서드"""
        super().setUp()
        
        # 테스트용 사용자 생성 (UserInfo 모델의 실제 필드명 사용)
        user_data = {
            'user_id': 'hong.gildong.001',  # user_id 필드 추가
            'LastName': '홍',
            'FirstName': '길동',
            'Email': 'hong@example.com',
            'Grade': 'A',
            'DOB': '1990-01-01'
        }
        
        response = self.client.post('/api/users',
                                  data=json.dumps(user_data),
                                  content_type='application/json')
        
        if response.status_code == 201:
            self.test_user = json.loads(response.data)
        else:
            raise Exception(f"테스트 사용자 생성 실패: Status {response.status_code}, Data: {response.data.decode()}")
    
    def test_get_all_wills_empty(self):
        """빈 유언장 목록 조회 테스트"""
        response = self.client.get('/api/wills')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 0)
        self.assertEqual(len(data['data']), 0)
    
    def test_create_will_success(self):
        """유언장 생성 성공 테스트"""
        will_data = {
            'user_id': self.test_user['user_id'],  # user_id 필드 사용
            'subject': '나의 마지막 편지',
            'body': '소중한 사람들에게 전하는 마지막 말씀입니다.'
        }
        
        response = self.client.post('/api/wills',
                                  data=json.dumps(will_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertEqual(data['data']['user_id'], self.test_user['id'])
        self.assertEqual(data['data']['subject'], '나의 마지막 편지')
        self.assertEqual(data['data']['body'], '소중한 사람들에게 전하는 마지막 말씀입니다.')
        self.assertIn('created_at', data['data'])
        self.assertIn('lastmodified_at', data['data'])
    
    def test_create_will_missing_required_fields(self):
        """필수 필드 누락으로 유언장 생성 실패 테스트"""
        # user_id 누락
        will_data = {
            'subject': '제목만 있는 유언장',
            'body': '내용만 있는 유언장'
        }
        
        response = self.client.post('/api/wills',
                                  data=json.dumps(will_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Missing required fields', data['error'])
    
    def test_create_will_no_data(self):
        """데이터 없이 유언장 생성 실패 테스트"""
        response = self.client.post('/api/wills',
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('No data provided', data['error'])
    
    def test_get_will_by_id_success(self):
        """유언장 ID로 조회 성공 테스트"""
        # 먼저 유언장 생성
        will_data = {
            'user_id': self.test_user['id'],
            'subject': '테스트 유언장',
            'body': '테스트 내용입니다.'
        }
        
        create_response = self.client.post('/api/wills',
                                         data=json.dumps(will_data),
                                         content_type='application/json')
        created_will = json.loads(create_response.data)['data']
        will_id = created_will['id']
        
        # 생성된 유언장 조회
        response = self.client.get(f'/api/wills/{will_id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['id'], will_id)
        self.assertEqual(data['data']['subject'], '테스트 유언장')
    
    def test_get_will_by_id_not_found(self):
        """존재하지 않는 유언장 조회 실패 테스트"""
        response = self.client.get('/api/wills/999')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Will not found')
    
    def test_update_will_success(self):
        """유언장 수정 성공 테스트"""
        # 먼저 유언장 생성
        will_data = {
            'user_id': self.test_user['id'],
            'subject': '원본 제목',
            'body': '원본 내용'
        }
        
        create_response = self.client.post('/api/wills',
                                         data=json.dumps(will_data),
                                         content_type='application/json')
        created_will = json.loads(create_response.data)['data']
        will_id = created_will['id']
        
        # 유언장 수정
        update_data = {
            'subject': '수정된 제목',
            'body': '수정된 내용입니다.'
        }
        
        response = self.client.put(f'/api/wills/{will_id}',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['subject'], '수정된 제목')
        self.assertEqual(data['data']['body'], '수정된 내용입니다.')
    
    def test_update_will_partial(self):
        """유언장 일부 필드만 수정 테스트"""
        # 먼저 유언장 생성
        will_data = {
            'user_id': self.test_user['id'],
            'subject': '원본 제목',
            'body': '원본 내용'
        }
        
        create_response = self.client.post('/api/wills',
                                         data=json.dumps(will_data),
                                         content_type='application/json')
        created_will = json.loads(create_response.data)['data']
        will_id = created_will['id']
        
        # subject만 수정
        update_data = {
            'subject': '새로운 제목'
        }
        
        response = self.client.put(f'/api/wills/{will_id}',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['subject'], '새로운 제목')
        self.assertEqual(data['data']['body'], '원본 내용')  # 변경되지 않음
    
    def test_update_will_not_found(self):
        """존재하지 않는 유언장 수정 실패 테스트"""
        update_data = {'subject': '새 제목'}
        
        response = self.client.put('/api/wills/999',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Will not found')
    
    def test_delete_will_success(self):
        """유언장 삭제 성공 테스트"""
        # 먼저 유언장 생성
        will_data = {
            'user_id': self.test_user['id'],
            'subject': '삭제할 유언장',
            'body': '삭제될 예정입니다.'
        }
        
        create_response = self.client.post('/api/wills',
                                         data=json.dumps(will_data),
                                         content_type='application/json')
        created_will = json.loads(create_response.data)['data']
        will_id = created_will['id']
        
        # 유언장 삭제
        response = self.client.delete(f'/api/wills/{will_id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # 삭제된 유언장 조회 시 404 확인
        get_response = self.client.get(f'/api/wills/{will_id}')
        self.assertEqual(get_response.status_code, 404)
    
    def test_delete_will_not_found(self):
        """존재하지 않는 유언장 삭제 실패 테스트"""
        response = self.client.delete('/api/wills/999')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Will not found')
    
    def test_get_all_wills_with_data(self):
        """유언장 목록 조회 (데이터 있음) 테스트"""
        # 여러 유언장 생성
        wills_data = [
            {'user_id': self.test_user['id'], 'subject': '첫 번째 유언장', 'body': '첫 번째 내용'},
            {'user_id': self.test_user['id'], 'subject': '두 번째 유언장', 'body': '두 번째 내용'},
            {'user_id': self.test_user['id'], 'subject': '세 번째 유언장', 'body': '세 번째 내용'}
        ]
        
        for will_data in wills_data:
            self.client.post('/api/wills',
                           data=json.dumps(will_data),
                           content_type='application/json')
        
        # 모든 유언장 조회
        response = self.client.get('/api/wills')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 3)
        self.assertEqual(len(data['data']), 3)

if __name__ == '__main__':
    unittest.main()