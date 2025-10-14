// API 호출을 위한 Axios 설정 파일
import axios from 'axios';

// Axios 인스턴스 생성 (기본 설정 포함)
const api = axios.create({
  // baseURL은 proxy 설정으로 인해 상대 경로 사용
  baseURL: '',
  timeout: 10000, // 10초 타임아웃
  headers: {
    'Content-Type': 'application/json',
  },
});

// 로그 전송 큐 및 관리
class LogSender {
  constructor() {
    this.logQueue = [];
    this.isProcessing = false;
    this.batchSize = 10;
    this.flushInterval = 5000; // 5초마다 전송
    this.maxRetries = 3;
    
    this.startPeriodicFlush();
  }

  startPeriodicFlush() {
    setInterval(() => {
      this.flushLogs();
    }, this.flushInterval);
  }

  addLog(logEntry) {
    this.logQueue.push({
      ...logEntry,
      timestamp: new Date().toISOString(),
      sessionId: this.getSessionId(),
      userAgent: navigator.userAgent,
      url: window.location.href
    });

    // 큐가 배치 크기에 도달하면 즉시 전송
    if (this.logQueue.length >= this.batchSize) {
      this.flushLogs();
    }
  }

  getSessionId() {
    let sessionId = sessionStorage.getItem('dms_session_id');
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('dms_session_id', sessionId);
    }
    return sessionId;
  }

  async flushLogs() {
    if (this.isProcessing || this.logQueue.length === 0) return;

    this.isProcessing = true;
    const logsToSend = [...this.logQueue];
    this.logQueue = [];

    try {
      // 별도의 axios 인스턴스 사용 (무한 루프 방지)
      const logApi = axios.create({
        baseURL: '',
        timeout: 5000,
        headers: {
          'Content-Type': 'application/json',
        },
      });

      await logApi.post('/api/logs/frontend', {
        logs: logsToSend,
        source: 'frontend'
      });

      console.log(`[LogSender] ${logsToSend.length}개 로그 서버 전송 완료`);
    } catch (error) {
      console.error('[LogSender] 로그 전송 실패:', error);
      // 실패한 로그를 다시 큐에 추가 (최대 재시도 횟수 확인)
      const retriableLogs = logsToSend.filter(log => (log.retryCount || 0) < this.maxRetries);
      retriableLogs.forEach(log => {
        log.retryCount = (log.retryCount || 0) + 1;
      });
      this.logQueue.unshift(...retriableLogs);
    } finally {
      this.isProcessing = false;
    }
  }

  // 즉시 전송
  async flushNow() {
    await this.flushLogs();
  }
}

const logSender = new LogSender();

// 요청 인터셉터 (요청 전에 실행)
api.interceptors.request.use(
  (config) => {
    const requestInfo = {
      method: config.method?.toUpperCase(),
      url: config.url,
      headers: config.headers,
      data: config.data
    };

    console.log('📤 API 요청:', requestInfo.method, requestInfo.url);
    
    // 로그를 서버로 전송 (로그 API 호출은 제외)
    if (!config.url?.includes('/api/logs/')) {
      logSender.addLog({
        category: 'server',
        level: 'info',
        message: `API 요청 시작: ${requestInfo.method} ${requestInfo.url}`,
        data: {
          method: requestInfo.method,
          url: requestInfo.url,
          hasData: !!requestInfo.data,
          dataSize: requestInfo.data ? JSON.stringify(requestInfo.data).length : 0
        }
      });
    }
    
    return config;
  },
  (error) => {
    console.error('❌ 요청 에러:', error);
    
    // 요청 에러 로그 전송
    logSender.addLog({
      category: 'error',
      level: 'error',
      message: `API 요청 에러: ${error.message}`,
      data: {
        error: error.message,
        config: error.config ? {
          method: error.config.method,
          url: error.config.url
        } : null
      }
    });
    
    return Promise.reject(error);
  }
);

// 응답 인터셉터 (응답 후에 실행)
api.interceptors.response.use(
  (response) => {
    const responseInfo = {
      status: response.status,
      statusText: response.statusText,
      url: response.config.url,
      method: response.config.method?.toUpperCase(),
      dataSize: response.data ? JSON.stringify(response.data).length : 0
    };

    console.log('📥 API 응답:', responseInfo.status, responseInfo.url);
    
    // 성공 응답 로그 전송 (로그 API 호출은 제외)
    if (!response.config.url?.includes('/api/logs/')) {
      logSender.addLog({
        category: 'server',
        level: 'success',
        message: `API 응답 성공: ${responseInfo.method} ${responseInfo.url} - ${responseInfo.status}`,
        data: {
          method: responseInfo.method,
          url: responseInfo.url,
          status: responseInfo.status,
          statusText: responseInfo.statusText,
          responseSize: responseInfo.dataSize,
          duration: response.config.metadata?.endTime - response.config.metadata?.startTime || 0
        }
      });
    }
    
    return response;
  },
  (error) => {
    const errorInfo = {
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      method: error.config?.method?.toUpperCase(),
      message: error.message
    };

    console.error('❌ 응답 에러:', errorInfo.status, errorInfo.message);
    
    // 에러 응답 로그 전송 (로그 API 호출은 제외)
    if (!error.config?.url?.includes('/api/logs/')) {
      logSender.addLog({
        category: 'error',
        level: 'error',
        message: `API 응답 에러: ${errorInfo.method} ${errorInfo.url} - ${errorInfo.status || 'Network Error'}`,
        data: {
          method: errorInfo.method,
          url: errorInfo.url,
          status: errorInfo.status,
          statusText: errorInfo.statusText,
          errorMessage: errorInfo.message,
          errorResponse: error.response?.data
        }
      });
    }
    
    return Promise.reject(error);
  }
);

// 요청 시간 측정을 위한 미들웨어
api.interceptors.request.use(
  (config) => {
    config.metadata = { startTime: new Date().getTime() };
    return config;
  }
);

api.interceptors.response.use(
  (response) => {
    response.config.metadata.endTime = new Date().getTime();
    return response;
  },
  (error) => {
    if (error.config) {
      error.config.metadata = error.config.metadata || {};
      error.config.metadata.endTime = new Date().getTime();
    }
    return Promise.reject(error);
  }
);

// 전역 객체에 로그 관리 함수 추가
if (typeof window !== 'undefined') {
  window.dmsApiLogSender = {
    flushNow: () => logSender.flushNow(),
    getQueueSize: () => logSender.logQueue.length,
    addLog: (category, level, message, data) => logSender.addLog({ category, level, message, data })
  };
}

export default api;
export { logSender };