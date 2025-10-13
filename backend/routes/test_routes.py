from flask import Blueprint
import os
import sys
import subprocess
from datetime import datetime

def init_test_routes():
    """테스트 관련 라우트를 초기화하는 함수"""
    
    test_bp = Blueprint('test', __name__)
    
    @test_bp.route('/test', methods=['GET'])
    def test_page():
        """테스트 실행 페이지"""
        return '''
        <html>
            <head>
                <title>DMS API 테스트</title>
                <meta charset="UTF-8">
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        text-align: center; 
                        margin-top: 50px;
                        background-color: #f5f5f5;
                    }
                    .container {
                        max-width: 800px;
                        margin: 0 auto;
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    }
                    h1 { color: #2c3e50; }
                    .button {
                        display: inline-block;
                        padding: 15px 30px;
                        margin: 10px;
                        background-color: #e74c3c;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                        transition: background-color 0.3s;
                        cursor: pointer;
                        border: none;
                        font-size: 16px;
                    }
                    .button:hover {
                        background-color: #c0392b;
                    }
                    .back-button {
                        background-color: #95a5a6;
                    }
                    .back-button:hover {
                        background-color: #7f8c8d;
                    }
                    .info {
                        text-align: left;
                        background-color: #ecf0f1;
                        padding: 20px;
                        margin: 20px 0;
                        border-radius: 5px;
                    }
                </style>
                <script>
                    function runAllTests() {
                        document.getElementById('runAllBtn').disabled = true;
                        document.getElementById('runAllBtn').innerText = '🔄 모든 테스트 실행 중...';
                        
                        // 결과 영역 표시
                        document.getElementById('testResults').style.display = 'block';
                        document.getElementById('testResults').innerHTML = '<div style="text-align: center; padding: 20px;"><div style="display: inline-block; width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite;"></div><br><br>테스트 실행 중...</div><style>@keyframes spin {0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); }}</style>';
                        
                        window.location.href = '/run-tests';
                    }
                    
                    function showTerminalInstructions() {
                        const instructions = `
터미널에서 테스트 실행 방법:

1. PowerShell 또는 Command Prompt를 열어주세요
2. 다음 명령어를 실행해주세요:

   cd "C:\\\\Users\\\\blues\\\\OneDrive\\\\Documents\\\\GitHub\\\\DMS\\\\backend\\\\tests"
   python simple_test_runner.py

3. 또는 특정 테스트만 실행하려면:
   python -m unittest test_userinfo_api.TestUserInfoAPI
   python -m unittest test_will_api.TestWillAPI
   python -m unittest test_recipients_api.TestRecipientsAPI
   python -m unittest test_triggers_api.TestTriggersAPI
   python -m unittest test_dispatchlog_api.TestDispatchLogAPI
`;
                        alert(instructions);
                    }
                </script>
            </head>
            <body>
                <div class="container">
                    <h1>🧪 DMS API 테스트</h1>
                    <p>DMS 시스템의 모든 API에 대한 종합적인 테스트를 실행합니다.</p>
                    
                    <div class="info">
                        <h3>📋 테스트 가능한 API 모듈:</h3>
                        <ul>
                            <li>✅ <strong>UserInfo API</strong>: 사용자 관리 (11개 테스트)</li>
                            <li>✅ <strong>Will API</strong>: 디지털 유언 관리 (12개 테스트)</li>
                            <li>✅ <strong>Recipients API</strong>: 수신자 관리 (12개 테스트)</li>
                            <li>✅ <strong>Triggers API</strong>: 트리거 시스템 (7개 테스트)</li>
                            <li>✅ <strong>DispatchLog API</strong>: 발송 로그 (10개 테스트)</li>
                        </ul>
                        <p><strong>총 52개의 테스트 케이스</strong>로 모든 CRUD 작업과 에러 처리를 검증합니다.</p>
                        <p><strong>🎯 완전한 API 생태계</strong>: 모든 API가 완벽하게 작동하며 상세한 모듈별 결과를 제공합니다.</p>
                    </div>
                    
                    <button id="runAllBtn" onclick="runAllTests()" class="button">🚀 모든 테스트 실행</button>
                    <button onclick="showTerminalInstructions()" class="button" style="background-color: #34495e;">📋 터미널 실행 방법</button>
                    <a href="/" class="button back-button">🏠 홈으로 돌아가기</a>
                    
                    <!-- 테스트 결과 표시 영역 -->
                    <div id="testResults" style="display: none; margin-top: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;">
                        <h2>📊 테스트 결과</h2>
                        <div id="resultContent">
                            <!-- 테스트 결과가 여기에 표시됩니다 -->
                        </div>
                    </div>
                </div>
            </body>
        </html>
        '''
    
    @test_bp.route('/run-tests', methods=['GET'])
    def run_tests():
        """테스트 실행 및 결과 페이지"""
        try:
            # 항상 모든 테스트 실행
            from flask import request
            
            # 경로 계산
            current_file = os.path.abspath(__file__)
            route_dir = os.path.dirname(current_file)
            backend_dir = os.path.dirname(route_dir)
            test_dir = os.path.join(backend_dir, 'tests')
            
            # 별도 프로세스에서 테스트 실행 (Flask App Context 충돌 방지)
            import subprocess
            import json
            
            # 테스트 러너 경로
            runner_file = os.path.join(test_dir, 'simple_test_runner.py')
            runner_script = os.path.join(test_dir, 'run_tests_standalone.py')
            
            # 스탠드얼론 러너 스크립트 생성
            standalone_script = '''
import sys
import os
import json

# UTF-8 출력을 위한 설정
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, backend_dir)

try:
    from simple_test_runner import run_all_tests
    result = run_all_tests()
    print(json.dumps(result, ensure_ascii=True))
except Exception as e:
    error_result = {
        'success': False,
        'total_tests': 0,
        'total_failures': 0,
        'total_errors': 1,
        'modules': {},
        'summary': f'테스트 실행 중 오류 발생: {str(e)}'
    }
    print(json.dumps(error_result, ensure_ascii=True))
'''
            
            # 임시 스크립트 파일 생성
            with open(runner_script, 'w', encoding='utf-8') as f:
                f.write(standalone_script)
            
            # test_result 변수 초기화
            test_result = {
                'success': False,
                'total_tests': 0,
                'total_failures': 0,
                'total_errors': 0,
                'modules': {},
                'summary': '테스트 초기화 중...'
            }
            
            try:
                # Windows 환경을 위한 환경 변수 설정
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                env['PYTHONLEGACYWINDOWSSTDIO'] = '0'
                
                # 별도 프로세스에서 테스트 실행
                result = subprocess.run(
                    [sys.executable, runner_script],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    env=env,
                    cwd=test_dir,
                    timeout=300  # 5분 타임아웃
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    test_result = json.loads(result.stdout.strip())
                    success = test_result['success']
                    total_tests = test_result['total_tests']
                    modules = test_result['modules']
                    summary = test_result['summary']
                else:
                    # 프로세스 실행 실패
                    success = False
                    total_tests = 0
                    modules = {}
                    summary = f'테스트 프로세스 실행 실패: {result.stderr if result.stderr else "알 수 없는 오류"}'
                    # test_result도 업데이트
                    test_result.update({
                        'success': False,
                        'total_tests': 0,
                        'total_failures': 0,
                        'total_errors': 1,
                        'modules': {},
                        'summary': summary
                    })
                    
            except subprocess.TimeoutExpired:
                success = False
                total_tests = 0
                modules = {}
                summary = '테스트 실행 시간 초과 (5분)'
                # test_result도 업데이트
                test_result.update({
                    'success': False,
                    'total_tests': 0,
                    'total_failures': 0,
                    'total_errors': 1,
                    'modules': {},
                    'summary': summary
                })
            except Exception as e:
                success = False
                total_tests = 0
                modules = {}
                summary = f'테스트 실행 중 오류 발생: {str(e)}'
                # test_result도 업데이트
                test_result.update({
                    'success': False,
                    'total_tests': 0,
                    'total_failures': 0,
                    'total_errors': 1,
                    'modules': {},
                    'summary': summary
                })
            finally:
                # 임시 스크립트 파일 삭제
                if os.path.exists(runner_script):
                    try:
                        os.remove(runner_script)
                    except:
                        pass
            
            # 모듈별 결과를 생성하는 함수
            def generate_module_card(module_name, module_result):
                status_color = '#27ae60' if module_result['success'] else '#e74c3c'
                status_icon = '✅' if module_result['success'] else '❌'
                
                # 실패/오류 상세 정보
                details_html = ''
                if module_result['failure_details'] or module_result['error_details']:
                    details_html = '<div class="details">'
                    if module_result['failure_details']:
                        details_html += '<h5>실패한 테스트:</h5><ul>'
                        for detail in module_result['failure_details']:
                            details_html += f'<li>{detail}</li>'
                        details_html += '</ul>'
                    if module_result['error_details']:
                        details_html += '<h5>오류가 발생한 테스트:</h5><ul>'
                        for detail in module_result['error_details']:
                            details_html += f'<li>{detail}</li>'
                        details_html += '</ul>'
                    details_html += '</div>'
                
                return f'''
                <div class="module-card" style="border-left: 4px solid {status_color};">
                    <div class="module-header">
                        <h3>{status_icon} {module_name}</h3>
                        <div class="module-stats">
                            <span class="stat">총 {module_result['tests_run']}개</span>
                            <span class="stat success">성공 {module_result['tests_run'] - module_result['failures'] - module_result['errors']}개</span>
                            {f'<span class="stat error">실패 {module_result["failures"]}개</span>' if module_result['failures'] > 0 else ''}
                            {f'<span class="stat error">오류 {module_result["errors"]}개</span>' if module_result['errors'] > 0 else ''}
                        </div>
                    </div>
                    {details_html}
                    <div class="module-output">
                        <details>
                            <summary>테스트 출력 보기</summary>
                            <pre>{module_result['stdout'] if module_result['stdout'] else '출력 없음'}</pre>
                            {f'<div class="stderr"><strong>에러:</strong><pre>{module_result["stderr"]}</pre></div>' if module_result['stderr'] else ''}
                        </details>
                    </div>
                </div>
                '''
            
            # 전체 성공률 계산
            success_rate = 0
            if total_tests > 0:
                success_count = total_tests - test_result['total_failures'] - test_result['total_errors']
                success_rate = round((success_count / total_tests) * 100, 1)
            
            # HTML 결과 페이지 생성  
            result_html = f'''
            <html>
                <head>
                    <title>테스트 결과 - DMS API</title>
                    <meta charset="UTF-8">
                    <style>
                        body {{ 
                            font-family: Arial, sans-serif; 
                            margin: 20px;
                            background-color: #f5f5f5;
                        }}
                        .container {{
                            max-width: 1200px;
                            margin: 0 auto;
                            background: white;
                            padding: 40px;
                            border-radius: 10px;
                            box-shadow: 0 0 10px rgba(0,0,0,0.1);
                        }}
                        h1 {{ color: #2c3e50; }}
                        .success {{ color: #27ae60; }}
                        .error {{ color: #e74c3c; }}
                        .summary {{
                            background-color: {'#d5f4e6' if success else '#fdf2f2'};
                            border: 1px solid {'#27ae60' if success else '#e74c3c'};
                            padding: 20px;
                            border-radius: 5px;
                            margin: 20px 0;
                        }}
                        .test-info {{
                            display: grid;
                            grid-template-columns: 1fr 1fr 1fr 1fr;
                            gap: 20px;
                            margin: 20px 0;
                        }}
                        .info-card {{
                            background-color: #ecf0f1;
                            padding: 15px;
                            border-radius: 5px;
                            text-align: center;
                        }}
                        .info-card h3 {{
                            margin: 0 0 10px 0;
                            color: #2c3e50;
                            font-size: 14px;
                        }}
                        .info-card .number {{
                            font-size: 2em;
                            font-weight: bold;
                            color: {'#27ae60' if success else '#e74c3c'};
                        }}
                        .module-card {{
                            background-color: #fdfdfd;
                            margin: 15px 0;
                            padding: 20px;
                            border-radius: 8px;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        }}
                        .module-header {{
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-bottom: 10px;
                        }}
                        .module-header h3 {{
                            margin: 0;
                            color: #2c3e50;
                        }}
                        .module-stats {{
                            display: flex;
                            gap: 15px;
                        }}
                        .stat {{
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-size: 12px;
                            background-color: #ecf0f1;
                        }}
                        .stat.success {{
                            background-color: #d5f4e6;
                            color: #27ae60;
                        }}
                        .stat.error {{
                            background-color: #fdf2f2;
                            color: #e74c3c;
                        }}
                        .details {{
                            margin: 10px 0;
                            padding: 10px;
                            background-color: #fdf2f2;
                            border-radius: 4px;
                        }}
                        .details h5 {{
                            margin: 0 0 5px 0;
                            color: #e74c3c;
                        }}
                        .details ul {{
                            margin: 5px 0;
                            padding-left: 20px;
                        }}
                        .module-output {{
                            margin-top: 10px;
                        }}
                        .module-output details {{
                            background-color: #f8f9fa;
                            padding: 10px;
                            border-radius: 4px;
                        }}
                        .module-output summary {{
                            cursor: pointer;
                            font-weight: bold;
                            color: #2c3e50;
                        }}
                        .module-output pre {{
                            background-color: #2c3e50;
                            color: #ecf0f1;
                            padding: 10px;
                            border-radius: 4px;
                            overflow-x: auto;
                            font-size: 12px;
                            margin: 10px 0;
                        }}
                        .stderr {{
                            margin-top: 10px;
                        }}
                        .button {{
                            display: inline-block;
                            padding: 15px 30px;
                            margin: 10px;
                            background-color: #3498db;
                            color: white;
                            text-decoration: none;
                            border-radius: 5px;
                            transition: background-color 0.3s;
                        }}
                        .button:hover {{
                            background-color: #2980b9;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>🧪 DMS API 테스트 결과</h1>
                        <p>실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 테스트 유형: 전체 API</p>
                        
                        <div class="summary">
                            <h2 class="{'success' if success else 'error'}">
                                {'✅ 모든 테스트 성공!' if success else '❌ 일부 테스트 실패'}
                            </h2>
                            <p>{summary}</p>
                        </div>
                        
                        <div class="test-info">
                            <div class="info-card">
                                <h3>총 테스트</h3>
                                <div class="number">{total_tests}</div>
                            </div>
                            <div class="info-card">
                                <h3>성공</h3>
                                <div class="number" style="color: #27ae60;">{total_tests - test_result['total_failures'] - test_result['total_errors']}</div>
                            </div>
                            <div class="info-card">
                                <h3>실패/오류</h3>
                                <div class="number" style="color: #e74c3c;">{test_result['total_failures'] + test_result['total_errors']}</div>
                            </div>
                            <div class="info-card">
                                <h3>성공률</h3>
                                <div class="number">{success_rate}%</div>
                            </div>
                        </div>
                        
                        <h2>📋 모듈별 테스트 결과:</h2>
                        {''.join([generate_module_card(name, result) for name, result in modules.items()])}
                        
                        <div style="text-align: center; margin-top: 30px;">
                            <a href="/test" class="button">🔄 다시 테스트</a>
                            <a href="/" class="button">🏠 홈으로 돌아가기</a>
                        </div>
                    </div>
                </body>
            </html>
            '''
            
            return result_html
            
        except Exception as e:
            # 에러 발생 시 에러 페이지 (상세 디버깅 정보 포함)
            import traceback
            current_file = os.path.abspath(__file__)
            route_dir = os.path.dirname(current_file)
            backend_dir = os.path.dirname(route_dir)
            test_dir = os.path.join(backend_dir, 'tests')
            
            error_html = f'''
            <html>
                <head>
                    <title>테스트 에러 - DMS API</title>
                    <meta charset="UTF-8">
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        .container {{ max-width: 1000px; margin: 0 auto; padding: 40px; }}
                        .error {{ color: #e74c3c; }}
                        .debug {{ background: #f8f8f8; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                        .button {{ 
                            display: inline-block; padding: 15px 30px; margin: 10px;
                            background-color: #3498db; color: white; text-decoration: none;
                            border-radius: 5px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1 class="error">❌ 테스트 실행 에러</h1>
                        <p>테스트 실행 중 오류가 발생했습니다:</p>
                        
                        <h3>에러 메시지:</h3>
                        <div class="debug">{str(e)}</div>
                        
                        <h3>디버깅 정보:</h3>
                        <div class="debug">
                            현재 파일: {current_file}<br>
                            라우트 디렉토리: {route_dir}<br>
                            백엔드 디렉토리: {backend_dir}<br>
                            테스트 디렉토리: {test_dir}<br>
                            테스트 디렉토리 존재: {os.path.exists(test_dir)}<br>
                            Python 실행 파일: {sys.executable if 'sys' in locals() else 'N/A'}
                        </div>
                        
                        <h3>전체 스택 트레이스:</h3>
                        <div class="debug"><pre>{traceback.format_exc()}</pre></div>
                        
                        <a href="/test" class="button">🔄 다시 시도</a>
                        <a href="/" class="button">🏠 홈으로 돌아가기</a>
                    </div>
                </body>
            </html>
            '''
            return error_html
    
    return test_bp