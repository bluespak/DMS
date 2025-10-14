/**
 * DMS Frontend 로그 관리 시스템
 * Backend와 유사한 로그 구조를 제공하며 서버로 로그 전송
 */

class Logger {
  constructor() {
    this.logs = {
      system: [],
      data: [],
      server: [],
      error: []
    };
    this.maxLogs = 1000; // 메모리에 유지할 최대 로그 수
    this.isProduction = process.env.NODE_ENV === 'production';
    this.apiLogSender = null; // API 로그 전송자 (나중에 주입)
  }

  /**
   * API 로그 전송자 설정
   */
  setApiLogSender(apiLogSender) {
    this.apiLogSender = apiLogSender;
  }

  /**
   * 현재 시간을 ISO 형식으로 반환
   */
  getCurrentTimestamp() {
    return new Date().toISOString();
  }

  /**
   * 로그 레벨에 따른 색상 반환
   */
  getLogColor(level) {
    const colors = {
      info: '#2196F3',
      warn: '#FF9800',
      error: '#F44336',
      success: '#4CAF50',
      debug: '#9C27B0'
    };
    return colors[level] || '#000000';
  }

  /**
   * 로그를 콘솔과 메모리에 기록
   */
  log(category, level, message, data = null) {
    const timestamp = this.getCurrentTimestamp();
    const logEntry = {
      timestamp,
      category,
      level,
      message,
      data,
      url: window.location.href,
      userAgent: navigator.userAgent
    };

    // 메모리에 저장
    if (!this.logs[category]) {
      this.logs[category] = [];
    }
    
    this.logs[category].push(logEntry);

    // 최대 로그 수 제한
    if (this.logs[category].length > this.maxLogs) {
      this.logs[category] = this.logs[category].slice(-this.maxLogs);
    }

    // 콘솔 출력 (개발 모드에서만)
    if (!this.isProduction) {
      const style = `color: ${this.getLogColor(level)}; font-weight: bold;`;
      const logMessage = `[${timestamp}] [${category.toUpperCase()}] [${level.toUpperCase()}] ${message}`;
      
      switch (level) {
        case 'error':
          console.error(logMessage, data || '');
          break;
        case 'warn':
          console.warn(logMessage, data || '');
          break;
        case 'info':
        case 'success':
          console.log(`%c${logMessage}`, style, data || '');
          break;
        case 'debug':
          console.debug(logMessage, data || '');
          break;
        default:
          console.log(logMessage, data || '');
      }
    }

    // 로컬 스토리지에도 저장 (선택적)
    this.saveToLocalStorage(category, logEntry);

    // API를 통해 서버로 로그 전송
    if (this.apiLogSender) {
      this.apiLogSender.addLog(logEntry);
    }

    return logEntry;
  }

  /**
   * 시스템 로그 기록
   */
  system(level, message, data = null) {
    return this.log('system', level, message, data);
  }

  /**
   * 데이터 로그 기록 (API 호출, 데이터 처리 등)
   */
  data(level, message, data = null) {
    return this.log('data', level, message, data);
  }

  /**
   * 서버 통신 로그 기록
   */
  server(level, message, data = null) {
    return this.log('server', level, message, data);
  }

  /**
   * 에러 로그 기록
   */
  error(message, error = null) {
    const errorData = error ? {
      name: error.name,
      message: error.message,
      stack: error.stack,
      response: error.response?.data
    } : null;
    
    return this.log('error', 'error', message, errorData);
  }

  /**
   * 성공 로그 기록
   */
  success(category, message, data = null) {
    return this.log(category, 'success', message, data);
  }

  /**
   * 정보 로그 기록
   */
  info(category, message, data = null) {
    return this.log(category, 'info', message, data);
  }

  /**
   * 경고 로그 기록
   */
  warn(category, message, data = null) {
    return this.log(category, 'warn', message, data);
  }

  /**
   * 디버그 로그 기록
   */
  debug(category, message, data = null) {
    return this.log(category, 'debug', message, data);
  }

  /**
   * 로컬 스토리지에 로그 저장
   */
  saveToLocalStorage(category, logEntry) {
    try {
      const storageKey = `dms_logs_${category}`;
      const existingLogs = JSON.parse(localStorage.getItem(storageKey) || '[]');
      
      existingLogs.push(logEntry);
      
      // 최대 100개만 로컬 스토리지에 보관
      if (existingLogs.length > 100) {
        existingLogs.splice(0, existingLogs.length - 100);
      }
      
      localStorage.setItem(storageKey, JSON.stringify(existingLogs));
    } catch (error) {
      console.error('로컬 스토리지 저장 실패:', error);
    }
  }

  /**
   * 특정 카테고리의 로그 조회
   */
  getLogs(category) {
    return this.logs[category] || [];
  }

  /**
   * 모든 로그 조회
   */
  getAllLogs() {
    return this.logs;
  }

  /**
   * 로그 클리어
   */
  clearLogs(category = null) {
    if (category) {
      this.logs[category] = [];
      localStorage.removeItem(`dms_logs_${category}`);
    } else {
      this.logs = {
        system: [],
        data: [],
        server: [],
        error: []
      };
      // 모든 로그 관련 로컬 스토리지 클리어
      Object.keys(localStorage).forEach(key => {
        if (key.startsWith('dms_logs_')) {
          localStorage.removeItem(key);
        }
      });
    }
  }

  /**
   * 로그를 JSON 형태로 다운로드
   */
  downloadLogs(category = null) {
    const logsToDownload = category ? { [category]: this.logs[category] } : this.logs;
    const dataStr = JSON.stringify(logsToDownload, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `dms_logs_${category || 'all'}_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  /**
   * API 호출 로그 기록 헬퍼
   */
  logApiCall(method, url, data = null, response = null) {
    const message = `${method.toUpperCase()} ${url}`;
    
    if (response) {
      if (response.success || (response.status >= 200 && response.status < 300)) {
        this.server('success', `${message} - 성공`, {
          request: data,
          response: response.data || response,
          status: response.status
        });
      } else {
        this.server('error', `${message} - 실패`, {
          request: data,
          response: response.data || response,
          status: response.status,
          error: response.error
        });
      }
    } else {
      this.server('info', `${message} - 요청 시작`, { request: data });
    }
  }

  /**
   * 사용자 액션 로그 기록
   */
  logUserAction(action, target, data = null) {
    this.system('info', `사용자 액션: ${action} - ${target}`, {
      action,
      target,
      data,
      timestamp: this.getCurrentTimestamp()
    });
  }

  /**
   * 페이지 네비게이션 로그 기록
   */
  logNavigation(from, to) {
    this.system('info', `페이지 이동: ${from} → ${to}`, {
      from,
      to,
      timestamp: this.getCurrentTimestamp()
    });
  }
}

// 전역 로거 인스턴스 생성
const logger = new Logger();

// 전역 에러 핸들러 설정
window.addEventListener('error', (event) => {
  logger.error('전역 JavaScript 에러', {
    message: event.message,
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno,
    error: event.error
  });
});

// Promise rejection 핸들러 설정
window.addEventListener('unhandledrejection', (event) => {
  logger.error('처리되지 않은 Promise rejection', {
    reason: event.reason,
    promise: event.promise
  });
});

export default logger;