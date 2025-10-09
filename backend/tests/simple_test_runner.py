"""
간단한 테스트 실행 스크립트
웹 인터페이스에서 안전하게 실행할 수 있도록 설계
"""
import os
import sys
import unittest
import io
from contextlib import redirect_stdout, redirect_stderr

def run_all_tests():
    """모든 API 테스트를 실행하고 모듈별 결과를 반환"""
    try:
        # 경로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))  # tests 폴더
        backend_dir = os.path.dirname(current_dir)  # backend 폴더
        
        # sys.path에 필요한 경로들 추가
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        
        # 모든 API 모듈 임포트
        from test_userinfo_api import TestUserInfoAPI
        from test_will_api import TestWillAPI
        from test_recipients_api import TestRecipientsAPI
        from test_triggers_api import TestTriggersAPI
        from test_dispatchlog_api import TestDispatchLogAPI
        
        # 테스트 모듈 정의
        test_modules = [
            ('UserInfo API', TestUserInfoAPI),
            ('Will API', TestWillAPI),
            ('Recipients API', TestRecipientsAPI),
            ('Triggers API', TestTriggersAPI),
            ('DispatchLog API', TestDispatchLogAPI),
        ]
        
        # 전체 결과 저장
        all_results = {
            'success': True,
            'total_tests': 0,
            'total_failures': 0,
            'total_errors': 0,
            'modules': {},
            'summary': ''
        }
        
        loader = unittest.TestLoader()
        
        # 각 모듈별로 테스트 실행
        for module_name, test_class in test_modules:
            try:
                # 개별 모듈 테스트 실행
                suite = loader.loadTestsFromTestCase(test_class)
                
                stdout_capture = io.StringIO()
                stderr_capture = io.StringIO()
                
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    runner = unittest.TextTestRunner(stream=stdout_capture, verbosity=2)
                    result = runner.run(suite)
                
                # 모듈별 결과 저장
                module_result = {
                    'success': result.wasSuccessful(),
                    'tests_run': result.testsRun,
                    'failures': len(result.failures),
                    'errors': len(result.errors),
                    'stdout': stdout_capture.getvalue(),
                    'stderr': stderr_capture.getvalue(),
                    'failure_details': [f"{test}: {error}" for test, error in result.failures],
                    'error_details': [f"{test}: {error}" for test, error in result.errors]
                }
                
                all_results['modules'][module_name] = module_result
                all_results['total_tests'] += module_result['tests_run']
                all_results['total_failures'] += module_result['failures']
                all_results['total_errors'] += module_result['errors']
                
                if not module_result['success']:
                    all_results['success'] = False
                    
            except Exception as e:
                # 개별 모듈 실행 실패 시
                all_results['modules'][module_name] = {
                    'success': False,
                    'tests_run': 0,
                    'failures': 0,
                    'errors': 1,
                    'stdout': '',
                    'stderr': f'모듈 실행 오류: {str(e)}',
                    'failure_details': [],
                    'error_details': [f'Module Error: {str(e)}']
                }
                all_results['total_errors'] += 1
                all_results['success'] = False
        
        # 요약 생성
        summary_lines = []
        summary_lines.append(f"전체 테스트 결과: {all_results['total_tests']}개 테스트 실행")
        summary_lines.append(f"성공: {all_results['total_tests'] - all_results['total_failures'] - all_results['total_errors']}개")
        if all_results['total_failures'] > 0:
            summary_lines.append(f"실패: {all_results['total_failures']}개")
        if all_results['total_errors'] > 0:
            summary_lines.append(f"오류: {all_results['total_errors']}개")
        
        all_results['summary'] = '\n'.join(summary_lines)
        
        return all_results
        
    except Exception as e:
        return {
            'success': False,
            'total_tests': 0,
            'total_failures': 0,
            'total_errors': 1,
            'modules': {},
            'summary': f'전체 테스트 실행 중 오류 발생: {str(e)}'
        }

def run_user_info_tests():
    """UserInfo API 테스트만 실행하고 상세 결과 반환"""
    try:
        # 경로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))  # tests 폴더
        backend_dir = os.path.dirname(current_dir)  # backend 폴더
        
        # sys.path에 필요한 경로들 추가
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        
        # 테스트 모듈 임포트
        from test_userinfo_api import TestUserInfoAPI
        
        # 테스트 슈트 생성
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(TestUserInfoAPI)
        
        # 출력 캡처
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            runner = unittest.TextTestRunner(stream=stdout_capture, verbosity=2)
            result = runner.run(suite)
        
        # 상세 결과 구성
        module_result = {
            'success': result.wasSuccessful(),
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'stdout': stdout_capture.getvalue(),
            'stderr': stderr_capture.getvalue(),
            'failure_details': [f"{test}: {error}" for test, error in result.failures],
            'error_details': [f"{test}: {error}" for test, error in result.errors]
        }
        
        # 전체 결과 형식에 맞춰 반환
        return {
            'success': module_result['success'],
            'total_tests': module_result['tests_run'],
            'total_failures': module_result['failures'],
            'total_errors': module_result['errors'],
            'modules': {
                'UserInfo API': module_result
            },
            'summary': f"UserInfo API 테스트: {module_result['tests_run']}개 실행, " +
                      f"성공: {module_result['tests_run'] - module_result['failures'] - module_result['errors']}개" +
                      (f", 실패: {module_result['failures']}개" if module_result['failures'] > 0 else "") +
                      (f", 오류: {module_result['errors']}개" if module_result['errors'] > 0 else "")
        }
        
    except Exception as e:
        return {
            'success': False,
            'total_tests': 0,
            'total_failures': 0,
            'total_errors': 1,
            'modules': {
                'UserInfo API': {
                    'success': False,
                    'tests_run': 0,
                    'failures': 0,
                    'errors': 1,
                    'stdout': '',
                    'stderr': f'테스트 실행 중 오류 발생: {str(e)}',
                    'failure_details': [],
                    'error_details': [f'테스트 실행 중 오류 발생: {str(e)}']
                }
            },
            'summary': f'UserInfo API 테스트 실행 중 오류 발생: {str(e)}'
        }

if __name__ == '__main__':
    # 직접 실행 시 모든 테스트 실행
    result = run_all_tests()
    print(f"모든 테스트 완료: {result}")
    
    print("\n" + "="*50)
    print("개별 UserInfo 테스트도 실행:")
    user_result = run_user_info_tests()
    print(f"UserInfo 테스트 완료: {user_result}")