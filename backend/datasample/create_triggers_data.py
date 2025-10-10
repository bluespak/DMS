#!/usr/bin/env python3
"""
Triggers Data Creation Script for DMS
각 사용자에 대해 다양한 트리거 데이터를 생성하는 스크립트

Usage:
    python create_triggers_data.py [--dry-run]
    
Example:
    python create_triggers_data.py
    python create_triggers_data.py --dry-run
"""

import sys
import os
import argparse
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

def create_app():
    """Flask 애플리케이션 생성"""
    app = Flask(__name__)
    app.config.from_object(Config)
    return app

def create_models(db):
    """모델들을 생성하는 함수"""
    
    class UserInfo(db.Model):
        __tablename__ = 'UserInfo'
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(255), unique=True, nullable=False)
        lastname = db.Column(db.String(100))
        firstname = db.Column(db.String(100))
        grade = db.Column(db.String(3))
        DOB = db.Column(db.Date)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    class Trigger(db.Model):
        __tablename__ = 'triggers'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('UserInfo.id'), nullable=False)
        trigger_type = db.Column(db.Enum('inactivity', 'date', 'manual'), nullable=False)
        trigger_value = db.Column(db.String(255))
        last_checked = db.Column(db.DateTime)
        is_triggered = db.Column(db.Boolean, default=False)
        
        def to_dict(self):
            return {
                'id': self.id,
                'user_id': self.user_id,
                'trigger_type': self.trigger_type,
                'trigger_value': self.trigger_value,
                'last_checked': self.last_checked.isoformat() if self.last_checked else None,
                'is_triggered': self.is_triggered
            }
    
    return UserInfo, Trigger

def generate_trigger_data(user_id, user_name, user_grade):
    """사용자 정보를 기반으로 트리거 데이터 생성"""
    
    triggers = []
    
    # 1. Inactivity 트리거 (모든 사용자에게 추가)
    # 등급에 따른 비활성 기간 설정
    inactivity_days = {
        'Pre': random.choice([30, 60, 90]),      # Premium: 30-90일
        'Gol': random.choice([60, 90, 120]),     # Gold: 60-120일  
        'Sta': random.choice([90, 120, 180])     # Standard: 90-180일
    }
    
    days = inactivity_days.get(user_grade, 90)  # 기본값 90일
    
    triggers.append({
        'user_id': user_id,
        'trigger_type': 'inactivity',
        'trigger_value': str(days),
        'last_checked': datetime.utcnow() - timedelta(days=random.randint(1, 30)),
        'is_triggered': False
    })
    
    # 2. Date 트리거 (약 70%의 사용자에게 추가)
    if random.random() < 0.7:
        # 향후 6개월~2년 사이의 날짜 설정
        future_days = random.randint(180, 730)
        future_date = datetime.utcnow() + timedelta(days=future_days)
        
        triggers.append({
            'user_id': user_id,
            'trigger_type': 'date',
            'trigger_value': future_date.strftime('%Y-%m-%d'),
            'last_checked': datetime.utcnow() - timedelta(days=random.randint(1, 7)),
            'is_triggered': False
        })
    
    # 3. Manual 트리거 (약 30%의 사용자에게 추가)
    if random.random() < 0.3:
        manual_reasons = [
            'Emergency activation',
            'Family request',
            'Medical condition',
            'Travel notification',
            'Legal requirement',
            'Annual review',
            'Account verification'
        ]
        
        triggers.append({
            'user_id': user_id,
            'trigger_type': 'manual',
            'trigger_value': random.choice(manual_reasons),
            'last_checked': datetime.utcnow() - timedelta(days=random.randint(0, 14)),
            'is_triggered': random.choice([True, False])  # Manual은 가끔 트리거됨
        })
    
    return triggers

def create_triggers_data(dry_run=False):
    """모든 사용자에 대해 Triggers 데이터를 생성"""
    
    # Flask 앱 및 DB 초기화
    app = create_app()
    db = SQLAlchemy(app)
    UserInfo, Trigger = create_models(db)
    
    success_count = 0
    error_count = 0
    errors = []
    total_triggers = 0
    
    with app.app_context():
        try:
            # 데이터베이스 연결 테스트
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
            print("✅ 데이터베이스 연결 성공")
        except Exception as e:
            print(f"❌ 데이터베이스 연결 실패: {e}")
            return False
        
        # 모든 사용자 조회
        try:
            users = UserInfo.query.all()
            print(f"📊 총 {len(users)}명의 사용자 발견")
        except Exception as e:
            print(f"❌ 사용자 데이터 조회 실패: {e}")
            return False
        
        if not users:
            print("⚠️  사용자 데이터가 없습니다. 먼저 사용자를 생성해주세요.")
            return False
        
        print(f"\n{'='*60}")
        print(f"{'DRY RUN 모드' if dry_run else '실제 Triggers 데이터 생성'} - 시작")
        print(f"{'='*60}")
        
        for user in users:
            try:
                # 이미 Triggers가 있는지 확인
                existing_triggers = Trigger.query.filter_by(user_id=user.id).all()
                
                if existing_triggers:
                    print(f"⚠️  사용자 {user.id:2d}: {user.firstname} {user.lastname} - 이미 {len(existing_triggers)}개의 트리거 존재")
                    continue
                
                # 사용자에 대한 트리거들 생성
                triggers_data = generate_trigger_data(
                    user.id, 
                    f"{user.firstname} {user.lastname}",
                    user.grade
                )
                
                print(f"✅ 사용자 {user.id:2d}: {user.firstname} {user.lastname} ({user.grade}) - {len(triggers_data)}개 트리거 생성")
                
                # 각 트리거 정보 출력 및 DB 추가
                for trigger_data in triggers_data:
                    trigger = Trigger(
                        user_id=trigger_data['user_id'],
                        trigger_type=trigger_data['trigger_type'],
                        trigger_value=trigger_data['trigger_value'],
                        last_checked=trigger_data['last_checked'],
                        is_triggered=trigger_data['is_triggered']
                    )
                    
                    # 트리거 타입별 한국어 표시
                    type_names = {
                        'inactivity': '비활성', 
                        'date': '날짜', 
                        'manual': '수동'
                    }
                    type_name = type_names.get(trigger_data['trigger_type'], '알 수 없음')
                    
                    status_icon = "🔴" if trigger_data['is_triggered'] else "⚪"
                    
                    if trigger_data['trigger_type'] == 'inactivity':
                        print(f"   {status_icon} {type_name}: {trigger_data['trigger_value']}일 비활성")
                    elif trigger_data['trigger_type'] == 'date':
                        print(f"   {status_icon} {type_name}: {trigger_data['trigger_value']}")
                    else:  # manual
                        print(f"   {status_icon} {type_name}: {trigger_data['trigger_value']}")
                    
                    if not dry_run:
                        db.session.add(trigger)
                    
                    total_triggers += 1
                
                success_count += 1
                
            except Exception as e:
                print(f"❌ 사용자 {user.id}: {user.firstname} {user.lastname} - 처리 중 오류: {str(e)}")
                error_count += 1
                errors.append(f"사용자 {user.id}: {str(e)}")
        
        # 커밋 또는 롤백
        if not dry_run and success_count > 0:
            try:
                db.session.commit()
                print(f"\n🎉 데이터베이스 커밋 완료!")
            except Exception as e:
                db.session.rollback()
                print(f"\n❌ 데이터베이스 커밋 실패: {e}")
                return False
        elif dry_run:
            print(f"\n📋 DRY RUN 완료 - 실제 데이터는 삽입되지 않았습니다.")
    
    # 결과 요약
    print(f"\n{'='*60}")
    print(f"📊 Triggers 생성 결과 요약")
    print(f"{'='*60}")
    print(f"✅ 성공한 사용자: {success_count}명")
    print(f"🎯 총 생성된 트리거: {total_triggers}개")
    print(f"❌ 실패한 사용자: {error_count}명")
    print(f"📊 총 처리된 사용자: {len(users)}명")
    if success_count + error_count > 0:
        print(f"📈 성공률: {(success_count/(success_count+error_count)*100):.1f}%")
        print(f"🎯 평균 트리거 수: {(total_triggers/success_count):.1f}개/사용자")
    
    # 트리거 타입별 통계
    if not dry_run and total_triggers > 0:
        with app.app_context():
            try:
                trigger_stats = db.session.execute(db.text("""
                    SELECT trigger_type, COUNT(*) as count, 
                           SUM(CASE WHEN is_triggered = 1 THEN 1 ELSE 0 END) as triggered_count
                    FROM triggers 
                    GROUP BY trigger_type 
                    ORDER BY count DESC
                """)).fetchall()
                
                print(f"\n📈 트리거 타입별 통계:")
                type_names = {
                    'inactivity': '비활성', 
                    'date': '날짜', 
                    'manual': '수동'
                }
                for trigger_type, count, triggered_count in trigger_stats:
                    type_name = type_names.get(trigger_type, '알 수 없음')
                    print(f"   {type_name} ({trigger_type}): {count}개 (활성화: {triggered_count}개)")
            except Exception as e:
                print(f"⚠️  통계 조회 중 오류: {e}")
    
    if errors:
        print(f"\n⚠️  오류 목록:")
        for error in errors[:5]:  # 최대 5개까지만 표시
            print(f"   - {error}")
        if len(errors) > 5:
            print(f"   ... 및 {len(errors)-5}개 추가 오류")
    
    return success_count > 0

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='각 사용자에 대해 다양한 트리거 데이터를 생성')
    parser.add_argument('--dry-run', action='store_true', help='실제 삽입 없이 테스트만 실행')
    parser.add_argument('--version', action='version', version='DMS Triggers Creator v1.0')
    
    args = parser.parse_args()
    
    print("🚀 DMS Triggers 데이터 생성 도구 v1.0")
    print("⏰ 각 사용자에 대해 비활성/날짜/수동 트리거를 생성합니다.")
    
    if args.dry_run:
        print("🔍 DRY RUN 모드로 실행합니다.")
    
    # 환경 변수 확인
    required_env_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_NAME']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 다음 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        print("💡 .env 파일을 확인하거나 환경 변수를 설정해주세요.")
        sys.exit(1)
    
    # Triggers 데이터 생성 실행
    success = create_triggers_data(args.dry_run)
    
    if success:
        print("\n🎉 Triggers 데이터 생성이 성공적으로 완료되었습니다!")
        print("⏰ 이제 각 사용자마다 다양한 트리거 조건이 설정되었습니다.")
        print("💡 트리거 타입:")
        print("   - 비활성 (inactivity): 일정 기간 비활성시 활성화")
        print("   - 날짜 (date): 특정 날짜에 활성화")
        print("   - 수동 (manual): 사용자가 직접 활성화")
        sys.exit(0)
    else:
        print("\n💥 작업 중 오류가 발생했습니다.")
        sys.exit(1)

if __name__ == '__main__':
    main()