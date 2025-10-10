-- dispatch_log 테이블에 새로운 컬럼과 상태 추가
-- 수신확인 기능을 위한 테이블 구조 업데이트

-- 1. 새로운 컬럼 추가
ALTER TABLE dispatch_log 
ADD COLUMN delivered_at DATETIME AFTER sent_at,
ADD COLUMN read_at DATETIME AFTER delivered_at;

-- 2. status ENUM에 새로운 상태 추가
ALTER TABLE dispatch_log 
MODIFY COLUMN status ENUM('pending', 'sent', 'delivered', 'read', 'failed') DEFAULT 'pending';

-- 확인 쿼리
DESCRIBE dispatch_log;