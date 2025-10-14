// 환경변수 설정 관리
// React에서는 REACT_APP_ 접두사가 있는 환경변수만 사용 가능

const config = {
  // 앱 기본 정보
  app: {
    name: process.env.REACT_APP_NAME || 'DMS Frontend',
    version: process.env.REACT_APP_VERSION || '1.0.0',
    debugMode: process.env.REACT_APP_DEBUG_MODE === 'true',
    logLevel: process.env.REACT_APP_LOG_LEVEL || 'info'
  },

  // API 설정
  api: {
    baseUrl: process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000',
    backendPort: parseInt(process.env.REACT_APP_BACKEND_PORT) || 5000,
    timeout: 10000 // 10초
  },

  // 페이지네이션 설정
  pagination: {
    usersPerPage: parseInt(process.env.REACT_APP_USERS_PER_PAGE) || 5,
    maxPageButtons: parseInt(process.env.REACT_APP_MAX_PAGE_BUTTONS) || 10
  },

  // UI 설정
  ui: {
    animationDuration: 300,
    toastDuration: 3000
  }
};

// 개발 모드에서 설정 정보 로그 출력
if (config.app.debugMode) {
  console.log('🔧 앱 설정:', config);
}

export default config;