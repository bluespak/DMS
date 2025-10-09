from flask import Blueprint

def init_home_routes():
    """홈페이지 라우트를 초기화하는 함수"""
    
    home_bp = Blueprint('home', __name__)
    
    @home_bp.route('/', methods=['GET'])
    def home():
        """홈 페이지"""
        return '''
        <html>
            <head>
                <title>DMS API</title>
                <meta charset="UTF-8">
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        text-align: center; 
                        margin-top: 50px;
                        background-color: #f5f5f5;
                    }
                    .container {
                        max-width: 600px;
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
                        background-color: #3498db;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                        transition: background-color 0.3s;
                    }
                    .button:hover {
                        background-color: #2980b9;
                    }
                    .api-list {
                        text-align: left;
                        margin-top: 30px;
                    }
                    .api-item {
                        background-color: #ecf0f1;
                        padding: 10px;
                        margin: 5px 0;
                        border-radius: 3px;
                        font-family: monospace;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚀 DMS API Service</h1>
                    <p>디지털 메시지 서비스 API에 오신 것을 환영합니다!</p>
                    
                    <a href="/api/docs" class="button">📖 API 문서 보기</a>
                    <a href="/api/health" class="button">💚 시스템 상태 확인</a>
                    <a href="/test" class="button">🧪 API 테스트 실행</a>
                    
                    <div class="api-list">
                        <h3>🔗 주요 API 엔드포인트:</h3>
                        <div class="api-item">GET /api/users - 사용자 관리</div>
                        <div class="api-item">GET /api/wills - 유언장 관리</div>
                        <div class="api-item">GET /api/recipients - 수신자 관리</div>
                        <div class="api-item">GET /api/triggers - 트리거 관리</div>
                        <div class="api-item">GET /api/dispatch-logs - 발송 로그</div>
                    </div>
                </div>
            </body>
        </html>
        '''
    
    return home_bp