-- 사용자 정보 테이블
-- grade 멤버십 등급:
--   Pre: Premium (프리미엄) - 최고 등급, 비활성 기간 30-90일
--   Gol: Gold (골드) - 중간 등급, 비활성 기간 60-120일
--   Sta: Standard (스탠다드) - 기본 등급, 비활성 기간 90-180일
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
-- 각 사용자당 1:1 관계로 유언서 생성
-- subject: 유언서 제목 (자동 생성되는 개인화된 제목)
-- body: 유언서 본문 (3가지 템플릿 중 사용자별 순환 적용)
-- lastmodified_at: 자동 업데이트되는 수정 시간
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
-- relatedCode 관계 코드:
--   F: Family (가족)
--   R: Relative (친척)
--   C: Close Friend (친한 친구)
--   B: Business (비즈니스 관계)
--   O: Other (기타)
-- 보안상 모든 이메일은 @sample.recipient.com 도메인 사용
CREATE TABLE recipients (
  id INT PRIMARY KEY AUTO_INCREMENT,
  will_id INT NOT NULL,
  recipient_email VARCHAR(255) NOT NULL,  -- 테스트용: @sample.recipient.com
  recipient_name VARCHAR(100),
  relatedCode CHAR(1),                     -- 관계 코드 (F/R/C/B/O)
  FOREIGN KEY (will_id) REFERENCES wills(id)
);

-- 트리거 설정 테이블
-- trigger_type 종류:
--   inactivity: 비활성 트리거 (멤버십 등급별 다른 기간 적용)
--   date: 날짜 트리거 (특정 날짜에 활성화)
--   manual: 수동 트리거 (사용자가 직접 활성화)
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
-- 트리거 활성화시 유언서가 수신자들에게 발송되는 기록
-- status 상태:
--   pending: 발송 대기 중
--   sent: 발송 완료 (이메일 서버로 전송됨)
--   delivered: 수신자 메일함에 전달됨
--   read: 수신자가 읽음 확인
--   failed: 발송 실패
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