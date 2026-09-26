-- 개발용: 전체 테이블 삭제 및 재생성
-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS dmsdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE dmsdb;

-- 기존 테이블 삭제 (순서 중요: 외래키 관계 역순)
DROP TABLE IF EXISTS dispatch_log;
DROP TABLE IF EXISTS blockchain_outbox;
DROP TABLE IF EXISTS blockchain_events;
DROP TABLE IF EXISTS wills_versions;
DROP TABLE IF EXISTS recipients;
DROP TABLE IF EXISTS triggers;
DROP TABLE IF EXISTS wills;
DROP TABLE IF EXISTS UserInfo;

-- 사용자 정보 테이블
CREATE TABLE UserInfo (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  lastname VARCHAR(100),
  firstname VARCHAR(100),
  grade VARCHAR(3),
  password_hash VARCHAR(255),
  DOB DATE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 디지털 유언서 테이블
CREATE TABLE wills (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id VARCHAR(50) NOT NULL,
  subject VARCHAR(255),
  body TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  lastmodified_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES UserInfo(user_id),
  INDEX idx_wills_user_id (user_id)
);

-- 수신자 정보 테이블
CREATE TABLE recipients (
  id INT PRIMARY KEY AUTO_INCREMENT,
  will_id INT NOT NULL,
  recipient_email VARCHAR(255) NOT NULL,
  recipient_name VARCHAR(100),
  relatedCode CHAR(1),
  FOREIGN KEY (will_id) REFERENCES wills(id)
);

-- 트리거 설정 테이블
CREATE TABLE triggers (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id VARCHAR(50) NOT NULL,
  trigger_type ENUM('inactivity', 'date', 'manual', 'email', 'sms', 'notification') NOT NULL,
  trigger_value VARCHAR(255),
  trigger_date DATE,
  last_checked DATETIME,
  is_triggered BOOLEAN DEFAULT FALSE,
  status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
  description TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES UserInfo(user_id),
  INDEX idx_triggers_user_id (user_id),
  INDEX idx_triggers_status (status),
  INDEX idx_triggers_date (trigger_date),
  INDEX idx_triggers_created (created_at)
);

-- 발송 로그 테이블
CREATE TABLE dispatch_log (
  id INT PRIMARY KEY AUTO_INCREMENT,
  will_id INT NOT NULL,
  recipient_id INT NULL,
  sent_at DATETIME,
  delivered_at DATETIME,
  read_at DATETIME,
  status ENUM('pending', 'sent', 'delivered', 'read', 'failed') DEFAULT 'pending',
  type TINYINT NOT NULL,
  FOREIGN KEY (will_id) REFERENCES wills(id)
);

CREATE TABLE wills_versions (
  id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  will_id INT NOT NULL,
  version INT NOT NULL,
  pdf_path VARCHAR(1024) NOT NULL,
  hash CHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  blockchain_tx VARCHAR(66) NULL,
  blockchain_status ENUM('pending', 'submitted', 'confirmed', 'failed') NOT NULL DEFAULT 'pending',
  blockchain_block BIGINT NULL,
  encryption_key_id VARCHAR(255) NOT NULL,
  encryption_nonce VARBINARY(12) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  confirmed_at DATETIME NULL,
  UNIQUE KEY uq_wills_versions_will_version (will_id, version),
  INDEX idx_wills_versions_latest (will_id, version),
  INDEX idx_wills_versions_hash (hash),
  FOREIGN KEY (will_id) REFERENCES wills(id)
);

CREATE TABLE blockchain_events (
  id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  will_id INT NOT NULL,
  event_type VARCHAR(64) NOT NULL,
  tx_hash VARCHAR(66) NULL,
  payload JSON NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_blockchain_events_will_created (will_id, created_at),
  INDEX idx_blockchain_events_tx (tx_hash),
  FOREIGN KEY (will_id) REFERENCES wills(id)
);

CREATE TABLE blockchain_outbox (
  id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  will_version_id BIGINT NOT NULL,
  event_type VARCHAR(64) NOT NULL,
  payload JSON NOT NULL,
  status ENUM('pending', 'processing', 'completed', 'failed') NOT NULL DEFAULT 'pending',
  attempt_count INT NOT NULL DEFAULT 0,
  available_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  locked_at DATETIME NULL,
  locked_by VARCHAR(128) NULL,
  last_error TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  completed_at DATETIME NULL,
  UNIQUE KEY uq_blockchain_outbox_version_event (will_version_id, event_type),
  INDEX idx_blockchain_outbox_ready (status, available_at),
  FOREIGN KEY (will_version_id) REFERENCES wills_versions(id)
);
