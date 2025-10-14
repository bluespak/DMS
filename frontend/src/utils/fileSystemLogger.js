/**
 * 실제 파일 시스템에 로그를 저장하는 유틸리티
 * Node.js 환경에서만 작동 (개발 서버에서 사용)
 */

const fs = require('fs');
const path = require('path');

class FileSystemLogger {
  constructor() {
    this.logsDir = path.join(__dirname, '../../logs');
    this.logQueue = [];
    this.isProcessing = false;
    this.batchSize = 50;
    this.flushInterval = 10000; // 10초마다 플러시
    
    // 로그 디렉토리 생성
    this.ensureLogDirectories();
    
    // 주기적 플러시 시작
    this.startPeriodicFlush();
  }

  /**
   * 로그 디렉토리 생성
   */
  ensureLogDirectories() {
    const directories = ['system', 'data', 'server', 'error'];
    
    directories.forEach(dir => {
      const fullPath = path.join(this.logsDir, dir);
      if (!fs.existsSync(fullPath)) {
        fs.mkdirSync(fullPath, { recursive: true });
      }
    });
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
    this.logQueue.push({
      ...logEntry,
      timestamp: new Date().toISOString(),
      processId: process.pid
    });

    // 큐가 배치 크기에 도달하면 즉시 플러시
    if (this.logQueue.length >= this.batchSize) {
      this.flushLogs();
    }
  }

  /**
   * 로그를 파일로 저장
   */
  async flushLogs() {
    if (this.isProcessing || this.logQueue.length === 0) return;

    this.isProcessing = true;
    const logsToProcess = [...this.logQueue];
    this.logQueue = [];

    try {
      // 카테고리별로 로그 그룹화
      const logsByCategory = this.groupLogsByCategory(logsToProcess);

      // 각 카테고리별로 파일에 저장
      for (const [category, logs] of Object.entries(logsByCategory)) {
        await this.saveLogsToFile(category, logs);
      }

      console.log(`[FileSystemLogger] ${logsToProcess.length}개 로그 파일에 저장 완료`);
    } catch (error) {
      console.error('[FileSystemLogger] 로그 저장 실패:', error);
      // 실패한 로그를 다시 큐에 추가
      this.logQueue.unshift(...logsToProcess);
    } finally {
      this.isProcessing = false;
    }
  }

  /**
   * 카테고리별로 로그 그룹화
   */
  groupLogsByCategory(logs) {
    return logs.reduce((groups, log) => {
      const category = log.category || 'system';
      if (!groups[category]) {
        groups[category] = [];
      }
      groups[category].push(log);
      return groups;
    }, {});
  }

  /**
   * 로그를 파일에 저장
   */
  async saveLogsToFile(category, logs) {
    const today = new Date().toISOString().split('T')[0];
    const fileName = `${today}.log`;
    const filePath = path.join(this.logsDir, category, fileName);

    try {
      const logContent = logs.map(log => {
        const timestamp = log.timestamp;
        const level = (log.level || 'info').toUpperCase();
        const message = log.message || '';
        const data = log.data ? ` | Data: ${JSON.stringify(log.data)}` : '';
        const sessionId = log.sessionId ? ` | Session: ${log.sessionId}` : '';
        const processId = log.processId ? ` | PID: ${log.processId}` : '';
        
        return `[${timestamp}] [${level}] ${message}${data}${sessionId}${processId}`;
      }).join('\n') + '\n';

      // 파일에 추가 (append)
      await fs.promises.appendFile(filePath, logContent);
      
      console.log(`[FileSystemLogger] ${category} 카테고리 로그 ${logs.length}개 저장: ${filePath}`);
    } catch (error) {
      console.error(`[FileSystemLogger] ${category} 로그 저장 실패:`, error);
      throw error;
    }
  }

  /**
   * 오래된 로그 파일 정리
   */
  async cleanupOldLogs(daysToKeep = 7) {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);
    const cutoffDateStr = cutoffDate.toISOString().split('T')[0];

    const directories = ['system', 'data', 'server', 'error'];
    let removedCount = 0;

    for (const dir of directories) {
      const dirPath = path.join(this.logsDir, dir);
      
      try {
        const files = await fs.promises.readdir(dirPath);
        
        for (const file of files) {
          if (file.endsWith('.log')) {
            const fileDate = file.replace('.log', '');
            if (fileDate < cutoffDateStr) {
              const filePath = path.join(dirPath, file);
              await fs.promises.unlink(filePath);
              removedCount++;
              console.log(`[FileSystemLogger] 오래된 로그 파일 삭제: ${filePath}`);
            }
          }
        }
      } catch (error) {
        console.error(`[FileSystemLogger] ${dir} 디렉토리 정리 실패:`, error);
      }
    }

    console.log(`[FileSystemLogger] ${removedCount}개의 오래된 로그 파일 정리 완료`);
    return removedCount;
  }

  /**
   * 로그 파일 통계
   */
  async getLogFileStats() {
    const stats = {
      totalFiles: 0,
      categories: {},
      sizes: {}
    };

    const directories = ['system', 'data', 'server', 'error'];

    for (const dir of directories) {
      const dirPath = path.join(this.logsDir, dir);
      
      try {
        const files = await fs.promises.readdir(dirPath);
        const logFiles = files.filter(file => file.endsWith('.log'));
        
        stats.categories[dir] = logFiles.length;
        stats.totalFiles += logFiles.length;

        let totalSize = 0;
        for (const file of logFiles) {
          const filePath = path.join(dirPath, file);
          const stat = await fs.promises.stat(filePath);
          totalSize += stat.size;
        }
        
        stats.sizes[dir] = totalSize;
      } catch (error) {
        console.error(`[FileSystemLogger] ${dir} 통계 조회 실패:`, error);
        stats.categories[dir] = 0;
        stats.sizes[dir] = 0;
      }
    }

    return stats;
  }
}

module.exports = FileSystemLogger;