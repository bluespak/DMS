#!/usr/bin/env python3
"""
트리거 샘플 데이터 생성 스크립트
UI 테스트를 위한 다양한 트리거 이력 데이터를 생성합니다.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import app, db
from models.trigger import create_trigger_model
from datetime import datetime, timedelta
import random

def create_trigger_sample_data():
    """트리거 샘플 데이터 생성"""
    with app.app_context():
        try:
            # 트리거 모델 가져오기
            Trigger = create_trigger_model(db)
            
            # 기존 데이터 삭제
            print("🗑️  기존 트리거 데이터 삭제 중...")
            Trigger.query.delete()
            
            # 실제 데이터베이스에서 사용자 ID 목록을 SQL로 직접 가져오기
            result = db.session.execute(db.text("SELECT user_id FROM UserInfo ORDER BY user_id"))
            user_ids = [row[0] for row in result.fetchall()]
            
            if not user_ids:
                print("❌ 데이터베이스에 사용자가 없습니다. 먼저 사용자 데이터를 생성해주세요.")
                return
                
            print(f"📋 발견된 사용자: {len(user_ids)}명 - {user_ids}")
            
            # 트리거 타입별 설정
            trigger_types = ['email', 'sms', 'notification']
            status_options = ['pending', 'completed', 'failed']
            
            # 샘플 설명 템플릿
            descriptions = {
                'email': [
                    '생일 축하 메시지 발송',
                    '월간 뉴스레터 발송',
                    '이벤트 안내 메일',
                    '서비스 업데이트 공지',
                    '유언서 발송 예정'
                ],
                'sms': [
                    '긴급 알림 SMS',
                    '예약 확인 문자',
                    '보안 인증 코드',
                    '서비스 점검 안내',
                    '유언서 SMS 알림'
                ],
                'notification': [
                    '앱 푸시 알림',
                    '시스템 점검 알림',
                    '새 기능 안내',
                    '보안 경고 알림',
                    '유언서 처리 완료 알림'
                ]
            }
            
            trigger_count = 0
            
            # 각 사용자별로 3-7개의 트리거 생성
            for user_id in user_ids:
                num_triggers = random.randint(3, 7)
                
                for i in range(num_triggers):
                    # 랜덤 트리거 타입 선택
                    trigger_type = random.choice(trigger_types)
                    
                    # 과거부터 미래까지 다양한 날짜 생성
                    base_date = datetime.now()
                    date_offset = random.randint(-180, 90)  # 과거 6개월 ~ 미래 3개월
                    trigger_date = base_date + timedelta(days=date_offset)
                    
                    # 상태 결정 (과거 날짜는 주로 completed, 미래 날짜는 pending)
                    if trigger_date.date() < datetime.now().date():
                        # 과거 트리거: 80% completed, 15% failed, 5% pending
                        status = random.choices(
                            ['completed', 'failed', 'pending'],
                            weights=[80, 15, 5]
                        )[0]
                    else:
                        # 미래 트리거: 90% pending, 10% completed
                        status = random.choices(
                            ['pending', 'completed'],
                            weights=[90, 10]
                        )[0]
                    
                    # 설명 선택
                    description = random.choice(descriptions[trigger_type])
                    
                    # 트리거 값 설정 (기존 컬럼과의 호환성을 위해)
                    if trigger_type == 'email':
                        trigger_value = f"email_job_{i+1}"
                    elif trigger_type == 'sms':
                        trigger_value = f"sms_job_{i+1}"
                    else:
                        trigger_value = f"notification_job_{i+1}"
                    
                    # 트리거 생성
                    trigger = Trigger(
                        user_id=user_id,
                        trigger_type='manual',  # 기존 ENUM에 맞춤
                        trigger_date=trigger_date.date(),
                        trigger_value=trigger_value,
                        description=f"[{trigger_type.upper()}] {description}",
                        status=status,
                        last_checked=datetime.now() if status != 'pending' else None,
                        is_triggered=(status == 'completed')
                    )
                    
                    db.session.add(trigger)
                    trigger_count += 1
            
            # 데이터베이스에 저장
            db.session.commit()
            
            print(f"✅ 트리거 샘플 데이터 생성 완료!")
            print(f"   - 생성된 트리거 수: {trigger_count}개")
            print(f"   - 사용자 수: {len(user_ids)}명")
            print(f"   - 사용자당 평균: {trigger_count/len(user_ids):.1f}개")
            
            # 타입별 통계
            print("\n📊 트리거 타입별 통계:")
            for trigger_type in trigger_types:
                count = Trigger.query.filter(
                    Trigger.description.like(f'[{trigger_type.upper()}]%')
                ).count()
                print(f"   - {trigger_type.upper()}: {count}개")
            
            # 상태별 통계
            print("\n📊 상태별 통계:")
            for status in status_options:
                count = Trigger.query.filter(Trigger.status == status).count()
                print(f"   - {status.upper()}: {count}개")
                
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("🚀 트리거 샘플 데이터 생성 시작...")
    create_trigger_sample_data()
    print("🎉 트리거 샘플 데이터 생성 완료!")