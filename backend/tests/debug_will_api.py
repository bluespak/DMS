import unittest
import json
from test_config import BaseTestCase

class DebugWillAPI(BaseTestCase):
    
    def test_debug_create_will(self):
        """Will 생성 시 발생하는 500 에러를 디버깅"""
        will_data = {
            'user_id': 1,
            'subject': '나의 마지막 편지',
            'body': '소중한 사람들에게 전하는 마지막 말씀입니다.'
        }
        
        response = self.client.post('/api/wills',
                                  data=json.dumps(will_data),
                                  content_type='application/json')
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Data: {response.data.decode()}")
        
        if response.status_code != 201:
            try:
                data = json.loads(response.data)
                print(f"Error Details: {data}")
            except:
                print("Cannot parse response as JSON")

if __name__ == '__main__':
    unittest.main()