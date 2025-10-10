-- dispatch_log 테이블 업데이트 SQL
-- 수신확인 기능을 위한 새로운 컬럼과 상태 추가

-- 1. 새로운 컬럼 추가
ALTER TABLE dispatch_log 
ADD COLUMN delivered_at DATETIME AFTER sent_at;

ALTER TABLE dispatch_log 
ADD COLUMN read_at DATETIME AFTER delivered_at;

-- 2. status ENUM에 새로운 상태 추가 (기존: pending, sent, failed → 새로운: pending, sent, delivered, read, failed)
ALTER TABLE dispatch_log 
MODIFY COLUMN status ENUM('pending', 'sent', 'delivered', 'read', 'failed') DEFAULT 'pending';

-- 3. 업데이트 결과 확인
DESCRIBE dispatch_log;

-- 4. 기존 데이터 확인 (있다면)
SELECT COUNT(*) as total_records FROM dispatch_log;
SELECT status, COUNT(*) as count FROM dispatch_log GROUP BY status;