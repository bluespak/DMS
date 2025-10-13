#!/usr/bin/env python3
"""
Simple Dispatch Log Creation Script for DMS
Recipients를 기반으로 간단한 DispatchLog 데이터를 생성하는 스크립트
"""

import sys
import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 환경 변수 로드
load_dotenv()

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from models.dispatchlog import create_dispatchlog_model
from models.recipients import create_recipient_model
from models.will import create_will_model

def create_app():
    """Flask 애플리케이션 생성"""
    app = Flask(__name__)
    app.config.from_object(Config)
    return app

def create_simple_dispatch_logs():
    """간단한 DispatchLog 데이터 생성"""
    print("🚀 DMS Dispatch Log 데이터 생성 도구 (Simple Version)")
    print("📧 Recipients를 기반으로 DispatchLog 데이터를 생성합니다.")
    
    app = create_app()
    db = SQLAlchemy(app)
    
    # 모델 생성
    DispatchLog = create_dispatchlog_model(db)
    Recipient = create_recipient_model(db)
    Will = create_will_model(db)
    
    try:
        with app.app_context():
            print("✅ 데이터베이스 연결 성공")
            
            # 기존 Recipients 조회
            recipients = Recipient.query.all()
            print(f"📊 총 {len(recipients)}명의 Recipients 발견")
            
            if not recipients:
                print("❌ Recipients 데이터가 없습니다. 먼저 Recipients를 생성해주세요.")
                return
            
            # 기존 DispatchLog 개수 확인
            existing_count = DispatchLog.query.count()
            print(f"📊 기존 DispatchLog: {existing_count}개")
            
            print("\n" + "="*60)
            print("실제 DispatchLog 데이터 생성 - 시작")
            print("="*60)
            
            created_count = 0
            
            # Recipients의 30%~70%에 대해 DispatchLog 생성
            recipients_to_process = random.sample(recipients, 
                                                random.randint(int(len(recipients)*0.3), 
                                                             int(len(recipients)*0.7)))
            
            for recipient in recipients_to_process:
                # 과거 1-30일 사이의 랜덤한 시간
                days_ago = random.randint(1, 30)
                hours_ago = random.randint(0, 23)
                minutes_ago = random.randint(0, 59)
                
                sent_time = datetime.utcnow() - timedelta(days=days_ago, 
                                                        hours=hours_ago, 
                                                        minutes=minutes_ago)
                
                # 상태 결정 (대부분 성공)
                statuses = ['pending', 'sent', 'failed']
                status_weights = [0.1, 0.8, 0.1]  # 80% 성공
                status = random.choices(statuses, weights=status_weights)[0]
                
                # DispatchLog 생성
                dispatch_log = DispatchLog(
                    will_id=recipient.will_id,
                    recipient_id=recipient.id,
                    sent_at=sent_time if status in ['sent'] else None,
                    status=status
                )
                
                db.session.add(dispatch_log)
                created_count += 1
                
                # Will 정보 조회
                will = Will.query.get(recipient.will_id)
                will_title = will.subject[:50] + "..." if will and len(will.subject) > 50 else (will.subject if will else "Unknown")
                
                status_emoji = {"pending": "⏳", "sent": "✅", "failed": "❌"}
                print(f"{status_emoji.get(status, '❓')} Log {created_count}: {recipient.recipient_name} "
                      f"({recipient.recipient_email})")
                print(f"   📄 Will: {will_title}")
                print(f"   📅 발송: {sent_time.strftime('%Y-%m-%d %H:%M:%S') if status == 'sent' else 'N/A'}")
                print(f"   📊 상태: {status}")
                
            # 데이터베이스 커밋
            db.session.commit()
            print("\n🎉 데이터베이스 커밋 완료!")
            
            print("\n" + "="*60)
            print("📊 DispatchLog 생성 결과 요약")
            print("="*60)
            print(f"✅ 생성된 로그: {created_count}개")
            print(f"📊 전체 Recipients: {len(recipients)}개")
            print(f"📈 로그 생성률: {(created_count/len(recipients)*100):.1f}%")
            
            # 상태별 통계
            status_counts = {}
            for log in DispatchLog.query.all():
                status_counts[log.status] = status_counts.get(log.status, 0) + 1
            
            print(f"\n📈 상태별 로그 통계:")
            for status, count in status_counts.items():
                print(f"   {status}: {count}개")
            
            print(f"\n🎉 DispatchLog 데이터 생성이 성공적으로 완료되었습니다!")
            
    except Exception as e:
        print(f"💥 작업 중 오류가 발생했습니다: {e}")
        return False
    
    return True

if __name__ == "__main__":
    create_simple_dispatch_logs()