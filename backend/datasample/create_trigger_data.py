#!/usr/bin/env python3
"""
트리거 샘플 데이터 생성 스크립트
사용자별로 다양한 트리거 이력을 생성합니다.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import random
from app.app import app
from models.trigger import Trigger
from models.userinfo import UserInfo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config

def create_trigger_sample_data():
    """트리거 샘플 데이터 생성"""
    
    # 데이터베이스 연결
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("🔧 트리거 샘플 데이터 생성을 시작합니다...")
    
    try:
        # 기존 트리거 데이터 확인
        existing_triggers = session.query(Trigger).count()
        print(f"📊 기존 트리거 데이터: {existing_triggers}개")
        
        # 사용자 목록 가져오기
        users = session.query(UserInfo).limit(10).all()
        if not users:
            print("❌ 사용자 데이터가 없습니다. 먼저 사용자 데이터를 생성해주세요.")
            return
        
        print(f"👥 {len(users)}명의 사용자에 대한 트리거 데이터를 생성합니다.")
        
        # 트리거 타입과 상태 정의
        trigger_types = ['email', 'sms', 'notification']
        trigger_statuses = ['completed', 'pending', 'failed']
        
        # 설명 템플릿
        descriptions = [
            "정기 상속 확인 알림",
            "유언장 업데이트 요청",
            "수익자 정보 확인 필요",
            "법적 검토 완료 통지",
            "상속세 관련 안내",
            "유언장 갱신 제안",
            "긴급 연락처 확인",
            "법정 대리인 지정 안내",
            "재산 목록 업데이트 요청",
            "상속 절차 진행 상황 안내"
        ]
        
        # 각 사용자별로 트리거 데이터 생성
        created_count = 0
        
        for user in users:
            # 사용자당 2-8개의 트리거 생성
            trigger_count = random.randint(2, 8)
            
            for i in range(trigger_count):
                # 과거 30일 ~ 미래 30일 범위의 날짜 생성
                days_offset = random.randint(-30, 30)
                trigger_date = datetime.now() + timedelta(days=days_offset)
                
                # 과거 날짜면 completed나 failed, 미래 날짜면 pending
                if days_offset < 0:
                    status = random.choice(['completed', 'failed'])
                else:
                    status = 'pending'
                
                trigger_data = Trigger(
                    user_id=user.user_id,
                    trigger_type=random.choice(trigger_types),
                    trigger_date=trigger_date.date(),
                    status=status,
                    description=random.choice(descriptions),
                    created_at=datetime.now() - timedelta(days=random.randint(1, 60)),
                    updated_at=datetime.now() - timedelta(days=random.randint(0, 10))
                )
                
                session.add(trigger_data)
                created_count += 1
        
        # 데이터베이스에 저장
        session.commit()
        print(f"✅ {created_count}개의 트리거 데이터가 성공적으로 생성되었습니다!")
        
        # 생성된 데이터 요약
        total_triggers = session.query(Trigger).count()
        completed_count = session.query(Trigger).filter(Trigger.status == 'completed').count()
        pending_count = session.query(Trigger).filter(Trigger.status == 'pending').count()
        failed_count = session.query(Trigger).filter(Trigger.status == 'failed').count()
        
        print(f"\n📊 트리거 데이터 요약:")
        print(f"   총 트리거: {total_triggers}개")
        print(f"   완료: {completed_count}개")
        print(f"   대기중: {pending_count}개")
        print(f"   실패: {failed_count}개")
        
        # 타입별 분포
        email_count = session.query(Trigger).filter(Trigger.trigger_type == 'email').count()
        sms_count = session.query(Trigger).filter(Trigger.trigger_type == 'sms').count()
        notification_count = session.query(Trigger).filter(Trigger.trigger_type == 'notification').count()
        
        print(f"\n📋 타입별 분포:")
        print(f"   📧 이메일: {email_count}개")
        print(f"   📱 SMS: {sms_count}개")
        print(f"   🔔 알림: {notification_count}개")
        
    except Exception as e:
        session.rollback()
        print(f"❌ 오류 발생: {e}")
        raise
    finally:
        session.close()

def show_trigger_samples():
    """생성된 트리거 샘플 데이터 조회"""
    
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("\n🔍 생성된 트리거 샘플 데이터 (최근 10개):")
        print("-" * 100)
        
        triggers = session.query(Trigger).join(UserInfo).order_by(Trigger.created_at.desc()).limit(10).all()
        
        for trigger in triggers:
            user = session.query(UserInfo).filter(UserInfo.user_id == trigger.user_id).first()
            user_name = f"{user.FirstName} {user.LastName}" if user else "Unknown"
            
            type_emoji = {
                'email': '📧',
                'sms': '📱', 
                'notification': '🔔'
            }.get(trigger.trigger_type, '📋')
            
            status_emoji = {
                'completed': '✅',
                'pending': '⏳',
                'failed': '❌'
            }.get(trigger.status, '❓')
            
            print(f"{type_emoji} {trigger.trigger_type.upper()} | {user_name} ({trigger.user_id})")
            print(f"   날짜: {trigger.trigger_date} | 상태: {status_emoji} {trigger.status}")
            print(f"   설명: {trigger.description}")
            print(f"   생성: {trigger.created_at.strftime('%Y-%m-%d %H:%M')}")
            print("-" * 100)
            
    except Exception as e:
        print(f"❌ 데이터 조회 오류: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    with app.app_context():
        create_trigger_sample_data()
        show_trigger_samples()
        
        print("\n🎉 트리거 데이터 생성이 완료되었습니다!")
        print("💡 API 테스트: curl -X GET 'http://localhost:5000/api/triggers/user/user001'")