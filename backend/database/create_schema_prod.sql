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
