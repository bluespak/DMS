-- 트리거 테이블 구조 업데이트
-- 기존 필드를 유지하면서 새로운 관리 기능에 필요한 필드들 추가

ALTER TABLE triggers 
ADD COLUMN trigger_date DATE AFTER trigger_value,
ADD COLUMN status ENUM('pending', 'completed', 'failed') DEFAULT 'pending' AFTER is_triggered,
ADD COLUMN description TEXT AFTER status,
ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP AFTER description,
ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_at;

-- 인덱스 추가
ALTER TABLE triggers 
ADD INDEX idx_triggers_status (status),
ADD INDEX idx_triggers_date (trigger_date),
ADD INDEX idx_triggers_created (created_at);

-- 새로운 트리거 타입 추가를 위한 enum 수정
-- 주의: MySQL에서 ENUM 수정은 테이블 재생성이 필요할 수 있습니다
-- ALTER TABLE triggers MODIFY COLUMN trigger_type ENUM('inactivity', 'date', 'manual', 'email', 'sms', 'notification') NOT NULL;