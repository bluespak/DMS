/**
 * Frontend 로그를 파일 시스템에 저장하는 유틸리티
 * (개발 환경에서만 사용)
 */

import logger from './logger';

class LogFileManager {
  constructor() {
    this.isDevelopment = process.env.NODE_ENV === 'development';
    this.logQueue = [];
    this.isProcessing = false;
    this.batchSize = 10;
    this.flushInterval = 5000; // 5초마다 플러시
    
    if (this.isDevelopment) {
      this.startPeriodicFlush();
    }
  }

  /**
   * 주기적으로 로그를 플러시
   */
  startPeriodicFlush() {
    setInterval(() => {
      this.flushLogs();
    }, this.flushInterval);
  }

  /**
   * 로그를 큐에 추가
   */
  addToQueue(logEntry) {
    if (!this.isDevelopment) return;
    
    this.logQueue.push({
      ...logEntry,
      timestamp: new Date().toISOString(),
      sessionId: this.getSessionId()
    });

    // 큐가 배치 크기에 도달하면 즉시 플러시
    if (this.logQueue.length >= this.batchSize) {
      this.flushLogs();
    }
  }

  /**
   * 세션 ID 생성/조회
   */
  getSessionId() {
    let sessionId = sessionStorage.getItem('dms_session_id');
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('dms_session_id', sessionId);
    }
    return sessionId;
  }

  /**
   * 로그를 파일로 저장 (개발 환경에서는 콘솔에 출력 및 로컬 스토리지 저장)
   */
  async flushLogs() {
    if (this.isProcessing || this.logQueue.length === 0) return;

    this.isProcessing = true;
    const logsToProcess = [...this.logQueue];
    this.logQueue = [];

    try {
      // 날짜별로 로그 그룹화
      const logsByDate = this.groupLogsByDate(logsToProcess);

      for (const [date, logs] of Object.entries(logsByDate)) {
        await this.saveLogsToStorage(date, logs);
      }

      console.log(`[LogFileManager] ${logsToProcess.length}개 로그 처리 완료`);
    } catch (error) {
      console.error('[LogFileManager] 로그 저장 실패:', error);
      // 실패한 로그를 다시 큐에 추가
      this.logQueue.unshift(...logsToProcess);
    } finally {
      this.isProcessing = false;
    }
  }

  /**
   * 날짜별로 로그 그룹화
   */
  groupLogsByDate(logs) {
    return logs.reduce((groups, log) => {
      const date = log.timestamp.split('T')[0];
      if (!groups[date]) {
        groups[date] = [];
      }
      groups[date].push(log);
      return groups;
    }, {});
  }

  /**
   * 로그를 로컬 스토리지에 저장
   */
  async saveLogsToStorage(date, logs) {
    const storageKey = `dms_file_logs_${date}`;
    
    try {
      const existingLogs = JSON.parse(localStorage.getItem(storageKey) || '[]');
      const updatedLogs = [...existingLogs, ...logs];
      
      // 최대 500개까지만 보관
      if (updatedLogs.length > 500) {
        updatedLogs.splice(0, updatedLogs.length - 500);
      }
      
      localStorage.setItem(storageKey, JSON.stringify(updatedLogs));
      
      // 개발 환경에서는 파일 다운로드 준비
      if (this.isDevelopment && logs.length > 0) {
        this.prepareFileDownload(date, logs);
      }
    } catch (error) {
      console.error(`날짜 ${date}의 로그 저장 실패:`, error);
    }
  }

  /**
   * 파일 다운로드 준비 (개발 환경)
   */
  prepareFileDownload(date, logs) {
    const logContent = logs.map(log => {
      return `[${log.timestamp}] [${log.category?.toUpperCase() || 'UNKNOWN'}] [${log.level?.toUpperCase() || 'INFO'}] ${log.message}${log.data ? ` | Data: ${JSON.stringify(log.data)}` : ''}`;
    }).join('\n');

    // 브라우저 콘솔에 로그 파일 내용 출력
    console.log(`\n=== DMS Frontend Log File (${date}) ===`);
    console.log(logContent);
    console.log(`=== End of Log File ===\n`);
  }

  /**
   * 특정 날짜의 로그 다운로드
   */
  downloadLogsForDate(date) {
    const storageKey = `dms_file_logs_${date}`;
    const logs = JSON.parse(localStorage.getItem(storageKey) || '[]');
    
    if (logs.length === 0) {
      alert(`${date} 날짜의 로그가 없습니다.`);
      return;
    }

    const logContent = logs.map(log => {
      return `[${log.timestamp}] [${log.category?.toUpperCase() || 'UNKNOWN'}] [${log.level?.toUpperCase() || 'INFO'}] ${log.message}${log.data ? ` | Data: ${JSON.stringify(log.data)}` : ''}`;
    }).join('\n');

    const blob = new Blob([logContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `dms_frontend_${date}.log`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  /**
   * 모든 로그 다운로드
   */
  downloadAllLogs() {
    const allLogs = [];
    const keys = Object.keys(localStorage).filter(key => key.startsWith('dms_file_logs_'));
    
    keys.forEach(key => {
      const logs = JSON.parse(localStorage.getItem(key) || '[]');
      allLogs.push(...logs);
    });

    if (allLogs.length === 0) {
      alert('다운로드할 로그가 없습니다.');
      return;
    }

    // 시간순 정렬
    allLogs.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

    const logContent = allLogs.map(log => {
      return `[${log.timestamp}] [${log.category?.toUpperCase() || 'UNKNOWN'}] [${log.level?.toUpperCase() || 'INFO'}] ${log.message}${log.data ? ` | Data: ${JSON.stringify(log.data)}` : ''}`;
    }).join('\n');

    const blob = new Blob([logContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `dms_frontend_all_logs_${new Date().toISOString().split('T')[0]}.log`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  /**
   * 오래된 로그 정리
   */
  cleanupOldLogs(daysToKeep = 7) {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);
    const cutoffDateStr = cutoffDate.toISOString().split('T')[0];

    const keys = Object.keys(localStorage).filter(key => key.startsWith('dms_file_logs_'));
    let removedCount = 0;

    keys.forEach(key => {
      const date = key.replace('dms_file_logs_', '');
      if (date < cutoffDateStr) {
        localStorage.removeItem(key);
        removedCount++;
      }
    });

    console.log(`[LogFileManager] ${removedCount}개의 오래된 로그 파일 정리 완료`);
    return removedCount;
  }

  /**
   * 로그 통계 조회
   */
  getLogStats() {
    const stats = {
      totalFiles: 0,
      totalLogs: 0,
      categories: {},
      levels: {},
      dateRange: { start: null, end: null }
    };

    const keys = Object.keys(localStorage).filter(key => key.startsWith('dms_file_logs_'));
    stats.totalFiles = keys.length;

    keys.forEach(key => {
      const logs = JSON.parse(localStorage.getItem(key) || '[]');
      stats.totalLogs += logs.length;

      logs.forEach(log => {
        // 카테고리별 통계
        const category = log.category || 'unknown';
        stats.categories[category] = (stats.categories[category] || 0) + 1;

        // 레벨별 통계
        const level = log.level || 'info';
        stats.levels[level] = (stats.levels[level] || 0) + 1;

        // 날짜 범위
        const logDate = new Date(log.timestamp);
        if (!stats.dateRange.start || logDate < stats.dateRange.start) {
          stats.dateRange.start = logDate;
        }
        if (!stats.dateRange.end || logDate > stats.dateRange.end) {
          stats.dateRange.end = logDate;
        }
      });
    });

    return stats;
  }
}

// 전역 인스턴스 생성
const logFileManager = new LogFileManager();

// 기존 로거와 통합
const originalLog = logger.log.bind(logger);
logger.log = function(category, level, message, data = null) {
  const logEntry = originalLog(category, level, message, data);
  logFileManager.addToQueue(logEntry);
  return logEntry;
};

// 전역 객체에 로그 관리 함수 추가 (개발 환경에서 콘솔에서 사용 가능)
if (typeof window !== 'undefined') {
  window.dmsLogManager = {
    downloadLogs: (date) => logFileManager.downloadLogsForDate(date),
    downloadAllLogs: () => logFileManager.downloadAllLogs(),
    cleanupLogs: (days) => logFileManager.cleanupOldLogs(days),
    getStats: () => logFileManager.getLogStats(),
    flush: () => logFileManager.flushLogs()
  };
}

export default logFileManager;