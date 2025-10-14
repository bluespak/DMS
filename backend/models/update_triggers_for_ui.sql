-- 트리거 테이블을 UI에 맞게 업데이트
USE dmsdb;

-- 새로운 컬럼들 추가
ALTER TABLE triggers 
ADD COLUMN trigger_date DATE AFTER trigger_type,
ADD COLUMN description TEXT AFTER trigger_value,
ADD COLUMN status ENUM('pending', 'completed', 'failed') DEFAULT 'pending' AFTER is_triggered;

-- 기존 데이터가 있다면 trigger_date 값을 설정 (예시)
UPDATE triggers 
SET trigger_date = CASE 
    WHEN trigger_type = 'date' AND trigger_value IS NOT NULL THEN STR_TO_DATE(trigger_value, '%Y-%m-%d')
    WHEN trigger_type = 'inactivity' THEN DATE_ADD(CURDATE(), INTERVAL CAST(IFNULL(trigger_value, '30') AS SIGNED) DAY)
    ELSE CURDATE()
END
WHERE trigger_date IS NULL;

-- 기존 데이터에 기본 설명 추가
UPDATE triggers 
SET description = CASE 
    WHEN trigger_type = 'date' THEN CONCAT('날짜 트리거: ', IFNULL(trigger_value, '날짜 미설정'))
    WHEN trigger_type = 'inactivity' THEN CONCAT('비활성 트리거: ', IFNULL(trigger_value, '30'), '일')
    WHEN trigger_type = 'manual' THEN '수동 트리거'
    ELSE '트리거 설명 없음'
END
WHERE description IS NULL OR description = '';

-- 상태 업데이트 (is_triggered 기반)
UPDATE triggers 
SET status = CASE 
    WHEN is_triggered = 1 THEN 'completed'
    ELSE 'pending'
END;