-- 운영/배포용: 테이블이 없을 때만 생성
CREATE DATABASE IF NOT EXISTS dmsdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE dmsdb;

CREATE TABLE IF NOT EXISTS UserInfo (
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

CREATE TABLE IF NOT EXISTS wills (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id VARCHAR(50) NOT NULL,
  subject VARCHAR(255),
  body TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  lastmodified_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES UserInfo(user_id),
  INDEX idx_wills_user_id (user_id)
);

CREATE TABLE IF NOT EXISTS recipients (
  id INT PRIMARY KEY AUTO_INCREMENT,
  will_id INT NOT NULL,
  recipient_email VARCHAR(255) NOT NULL,
  recipient_name VARCHAR(100),
  relatedCode CHAR(1),
  FOREIGN KEY (will_id) REFERENCES wills(id)
);

CREATE TABLE IF NOT EXISTS wills_versions (
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
  CONSTRAINT fk_wills_versions_will FOREIGN KEY (will_id) REFERENCES wills(id)
);

CREATE TABLE IF NOT EXISTS blockchain_events (
  id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  will_id INT NOT NULL,
  event_type VARCHAR(64) NOT NULL,
  tx_hash VARCHAR(66) NULL,
  payload JSON NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_blockchain_events_will_created (will_id, created_at),
  INDEX idx_blockchain_events_tx (tx_hash),
  CONSTRAINT fk_blockchain_events_will FOREIGN KEY (will_id) REFERENCES wills(id)
);

CREATE TABLE IF NOT EXISTS blockchain_outbox (
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
  CONSTRAINT fk_blockchain_outbox_version FOREIGN KEY (will_version_id) REFERENCES wills_versions(id)
);

CREATE TABLE IF NOT EXISTS triggers (
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

CREATE TABLE IF NOT EXISTS dispatch_log (
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
