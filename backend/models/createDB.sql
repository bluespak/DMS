-- 데이터베이스 생성
CREATE DATABASE dmsdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 생성된 DB 사용
USE dmsdb;

-- 기존 테이블 삭제 (순서 중요: 외래키 관계 역순)
DROP TABLE IF EXISTS dispatch_log;
DROP TABLE IF EXISTS recipients;
DROP TABLE IF EXISTS triggers;
DROP TABLE IF EXISTS wills;
DROP TABLE IF EXISTS UserInfo;

-- 사용자 정보 테이블
CREATE TABLE UserInfo (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id VARCHAR(50) UNIQUE NOT NULL,  -- 새로운 사용자 ID 필드
  email VARCHAR(255) UNIQUE NOT NULL,
  lastname VARCHAR(100),
  firstname VARCHAR(100),
  grade VARCHAR(3),                    -- 멤버십 등급 (Pre/Gol/Sta)
  password_hash VARCHAR(255),
  DOB DATE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 디지털 유언서 테이블
CREATE TABLE wills (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id VARCHAR(50) NOT NULL,        -- 사용자 ID 외래키 (1:1 관계)
  subject VARCHAR(255),                -- 유언서 제목
  body TEXT,                          -- 유언서 본문
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  lastmodified_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES UserInfo(user_id),
  INDEX idx_wills_user_id (user_id)
);

-- 수신자 정보 테이블
CREATE TABLE recipients (
  id INT PRIMARY KEY AUTO_INCREMENT,
  will_id INT NOT NULL,
  recipient_email VARCHAR(255) NOT NULL,  -- 테스트용: @sample.recipient.com
  recipient_name VARCHAR(100),
  relatedCode CHAR(1),                     -- 관계 코드 (F/R/C/B/O)
  FOREIGN KEY (will_id) REFERENCES wills(id)
);

-- 트리거 설정 테이블
CREATE TABLE triggers (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id VARCHAR(50) NOT NULL,        -- 사용자 ID 외래키
  trigger_type ENUM('inactivity', 'date', 'manual') NOT NULL,
  trigger_value VARCHAR(255),          -- 예: '30'일, '2025-12-01', 'Family request'
  last_checked DATETIME,
  is_triggered BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (user_id) REFERENCES UserInfo(user_id),
  INDEX idx_triggers_user_id (user_id)
);

-- 발송 로그 테이블
CREATE TABLE dispatch_log (
  id INT PRIMARY KEY AUTO_INCREMENT,
  will_id INT NOT NULL,
  recipient_id INT NOT NULL,
  sent_at DATETIME,                    -- 실제 발송 시간
  delivered_at DATETIME,               -- 수신자 메일함 전달 시간
  read_at DATETIME,                    -- 수신자 읽음 확인 시간
  status ENUM('pending', 'sent', 'delivered', 'read', 'failed') DEFAULT 'pending',
  FOREIGN KEY (will_id) REFERENCES wills(id),
  FOREIGN KEY (recipient_id) REFERENCES recipients(id)
);