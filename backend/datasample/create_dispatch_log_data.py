#!/usr/bin/env python3
"""
Dispatch Log Data Creation Script for DMS
일부 will과 recipient에 대해 실제 발송된 것처럼 보이는 dispatch_log 데이터를 생성하는 스크립트

Usage:
    python create_dispatch_log_data.py [--dry-run]
    
Example:
    python create_dispatch_log_data.py
    python create_dispatch_log_data.py --dry-run
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
    
    class Will(db.Model):
        __tablename__ = 'wills'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, nullable=False)
        subject = db.Column(db.String(255))
        body = db.Column(db.Text)
    
    class Recipient(db.Model):
        __tablename__ = 'recipients'
        id = db.Column(db.Integer, primary_key=True)
        will_id = db.Column(db.Integer, nullable=False)
        recipient_email = db.Column(db.String(255), nullable=False)
        recipient_name = db.Column(db.String(100))
        relatedCode = db.Column(db.String(1))
    
    class DispatchLog(db.Model):
        __tablename__ = 'dispatch_log'
        id = db.Column(db.Integer, primary_key=True)
        will_id = db.Column(db.Integer, db.ForeignKey('wills.id'), nullable=False)
        recipient_id = db.Column(db.Integer, db.ForeignKey('recipients.id'), nullable=False)
        sent_at = db.Column(db.DateTime)
        delivered_at = db.Column(db.DateTime)
        read_at = db.Column(db.DateTime)
        status = db.Column(db.Enum('pending', 'sent', 'delivered', 'read', 'failed'), default='pending')
        
        def to_dict(self):
            return {
                'id': self.id,
                'will_id': self.will_id,
                'recipient_id': self.recipient_id,
                'sent_at': self.sent_at.isoformat() if self.sent_at else None,
                'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
                'read_at': self.read_at.isoformat() if self.read_at else None,
                'status': self.status
            }
    
    return Will, Recipient, DispatchLog

def generate_dispatch_timeline(base_time):
    """발송 타임라인을 생성하는 함수"""
    timelines = []
    
    # 다양한 상태의 발송 시나리오 생성
    scenarios = [
        # 완전히 성공한 케이스 (읽음까지)
        {
            'status': 'read',
            'sent_delay': random.randint(1, 30),      # 1-30분 후 발송
            'delivered_delay': random.randint(5, 120), # 5분-2시간 후 전달
            'read_delay': random.randint(30, 2880)     # 30분-2일 후 읽음
        },
        # 전달까지만 성공한 케이스
        {
            'status': 'delivered',
            'sent_delay': random.randint(1, 60),
            'delivered_delay': random.randint(10, 240),
            'read_delay': None
        },
        # 발송만 성공한 케이스
        {
            'status': 'sent',
            'sent_delay': random.randint(1, 45),
            'delivered_delay': None,
            'read_delay': None
        },
        # 발송 실패 케이스
        {
            'status': 'failed',
            'sent_delay': None,
            'delivered_delay': None,
            'read_delay': None
        },
        # 대기 중인 케이스
        {
            'status': 'pending',
            'sent_delay': None,
            'delivered_delay': None,
            'read_delay': None
        }
    ]
    
    # 상태별 가중치 (실제 발송 시스템과 유사하게)
    scenario_weights = [0.35, 0.25, 0.20, 0.10, 0.10]  # read, delivered, sent, failed, pending
    
    scenario = random.choices(scenarios, weights=scenario_weights)[0]
    
    result = {
        'status': scenario['status'],
        'sent_at': None,
        'delivered_at': None,
        'read_at': None
    }
    
    current_time = base_time
    
    if scenario['sent_delay'] is not None:
        result['sent_at'] = current_time + timedelta(minutes=scenario['sent_delay'])
        current_time = result['sent_at']
    
    if scenario['delivered_delay'] is not None and result['sent_at']:
        result['delivered_at'] = current_time + timedelta(minutes=scenario['delivered_delay'])
        current_time = result['delivered_at']
    
    if scenario['read_delay'] is not None and result['delivered_at']:
        result['read_at'] = current_time + timedelta(minutes=scenario['read_delay'])
    
    return result

def create_dispatch_log_data(dry_run=False):
    """일부 Will과 Recipient에 대해 Dispatch Log 데이터를 생성"""
    
    # Flask 앱 및 DB 초기화
    app = create_app()
    db = SQLAlchemy(app)
    Will, Recipient, DispatchLog = create_models(db)
    
    success_count = 0
    error_count = 0
    errors = []
    total_logs = 0
    
    with app.app_context():
        try:
            # 데이터베이스 연결 테스트
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
            print("✅ 데이터베이스 연결 성공")
        except Exception as e:
            print(f"❌ 데이터베이스 연결 실패: {e}")
            return False
        
        # 기존 dispatch_log 데이터 확인
        try:
            existing_logs = DispatchLog.query.count()
            print(f"📊 기존 dispatch_log 레코드: {existing_logs}개")
        except Exception as e:
            print(f"❌ 기존 데이터 조회 실패: {e}")
            return False
        
        # Will과 Recipients 데이터 조회
        try:
            # 전체 Will 중 30-50% 정도만 발송된 것으로 시뮬레이션
            all_wills = Will.query.all()
            selected_will_count = max(1, int(len(all_wills) * random.uniform(0.3, 0.5)))
            selected_wills = random.sample(all_wills, selected_will_count)
            
            print(f"📊 총 {len(all_wills)}개 Will 중 {len(selected_wills)}개 Will 발송 시뮬레이션")
        except Exception as e:
            print(f"❌ Will 데이터 조회 실패: {e}")
            return False
        
        print(f"\n{'='*60}")
        print(f"{'DRY RUN 모드' if dry_run else '실제 Dispatch Log 데이터 생성'} - 시작")
        print(f"{'='*60}")
        
        for will in selected_wills:
            try:
                # 해당 Will의 모든 Recipients 조회
                recipients = Recipient.query.filter_by(will_id=will.id).all()
                
                if not recipients:
                    print(f"⚠️  Will {will.id}: 수신자가 없어 건너뜀")
                    continue
                
                # 발송 기준 시간 (과거 1-30일 사이)
                base_time = datetime.utcnow() - timedelta(days=random.randint(1, 30))
                
                print(f"📧 Will {will.id:2d}: {will.subject[:40]}... - {len(recipients)}명 수신자")
                print(f"   📅 발송 기준 시간: {base_time.strftime('%Y-%m-%d %H:%M')}")
                
                will_success = 0
                
                for recipient in recipients:
                    try:
                        # 이미 dispatch_log가 있는지 확인
                        existing_log = DispatchLog.query.filter_by(
                            will_id=will.id, 
                            recipient_id=recipient.id
                        ).first()
                        
                        if existing_log:
                            continue
                        
                        # 발송 타임라인 생성
                        timeline = generate_dispatch_timeline(base_time)
                        
                        # DispatchLog 생성
                        dispatch_log = DispatchLog(
                            will_id=will.id,
                            recipient_id=recipient.id,
                            sent_at=timeline['sent_at'],
                            delivered_at=timeline['delivered_at'],
                            read_at=timeline['read_at'],
                            status=timeline['status']
                        )
                        
                        # 상태별 아이콘
                        status_icons = {
                            'pending': '⏳',
                            'sent': '📤',
                            'delivered': '📬',
                            'read': '👁️',
                            'failed': '❌'
                        }
                        
                        status_icon = status_icons.get(timeline['status'], '❓')
                        
                        print(f"   {status_icon} {recipient.recipient_name}: {timeline['status']}")
                        
                        if timeline['sent_at']:
                            print(f"      📤 발송: {timeline['sent_at'].strftime('%m-%d %H:%M')}")
                        if timeline['delivered_at']:
                            print(f"      📬 전달: {timeline['delivered_at'].strftime('%m-%d %H:%M')}")
                        if timeline['read_at']:
                            print(f"      👁️  읽음: {timeline['read_at'].strftime('%m-%d %H:%M')}")
                        
                        if not dry_run:
                            db.session.add(dispatch_log)
                        
                        will_success += 1
                        total_logs += 1
                        
                    except Exception as e:
                        print(f"❌ Recipient {recipient.id}: 처리 중 오류: {str(e)}")
                        error_count += 1
                        errors.append(f"Recipient {recipient.id}: {str(e)}")
                
                if will_success > 0:
                    success_count += 1
                
            except Exception as e:
                print(f"❌ Will {will.id}: 처리 중 오류: {str(e)}")
                error_count += 1
                errors.append(f"Will {will.id}: {str(e)}")
        
        # 커밋 또는 롤백
        if not dry_run and total_logs > 0:
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
    print(f"📊 Dispatch Log 생성 결과 요약")
    print(f"{'='*60}")
    print(f"✅ 발송 처리된 Will: {success_count}개")
    print(f"📧 총 생성된 발송 로그: {total_logs}개")
    print(f"❌ 실패한 처리: {error_count}개")
    
    # 상태별 통계 (실제 실행한 경우에만)
    if not dry_run and total_logs > 0:
        with app.app_context():
            try:
                status_stats = db.session.execute(db.text("""
                    SELECT status, COUNT(*) as count 
                    FROM dispatch_log 
                    GROUP BY status 
                    ORDER BY count DESC
                """)).fetchall()
                
                print(f"\n📈 발송 상태별 통계:")
                status_names = {
                    'pending': '⏳ 대기 중',
                    'sent': '📤 발송 완료',
                    'delivered': '📬 전달 완료',
                    'read': '👁️ 읽음 완료',
                    'failed': '❌ 발송 실패'
                }
                
                total_count = sum(count for _, count in status_stats)
                for status, count in status_stats:
                    status_name = status_names.get(status, f'알 수 없음 ({status})')
                    percentage = (count / total_count * 100) if total_count > 0 else 0
                    print(f"   {status_name}: {count}개 ({percentage:.1f}%)")
                
                # 성공률 계산
                success_statuses = ['sent', 'delivered', 'read']
                success_count = sum(count for status, count in status_stats if status in success_statuses)
                success_rate = (success_count / total_count * 100) if total_count > 0 else 0
                print(f"\n🎯 전체 발송 성공률: {success_rate:.1f}%")
                
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
    parser = argparse.ArgumentParser(description='일부 Will에 대해 실제 발송된 것처럼 보이는 dispatch_log 데이터를 생성')
    parser.add_argument('--dry-run', action='store_true', help='실제 삽입 없이 테스트만 실행')
    parser.add_argument('--version', action='version', version='DMS Dispatch Log Creator v1.0')
    
    args = parser.parse_args()
    
    print("🚀 DMS Dispatch Log 데이터 생성 도구 v1.0")
    print("📧 일부 Will에 대해 실제 발송된 것처럼 보이는 로그 데이터를 생성합니다.")
    
    if args.dry_run:
        print("🔍 DRY RUN 모드로 실행합니다.")
    
    # 환경 변수 확인
    required_env_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_NAME']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 다음 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        print("💡 .env 파일을 확인하거나 환경 변수를 설정해주세요.")
        sys.exit(1)
    
    # Dispatch Log 데이터 생성 실행
    success = create_dispatch_log_data(args.dry_run)
    
    if success:
        print("\n🎉 Dispatch Log 데이터 생성이 성공적으로 완료되었습니다!")
        print("📊 이제 일부 Will이 실제로 발송된 것처럼 보이는 로그 데이터가 있습니다.")
        print("💡 다양한 발송 상태:")
        print("   ⏳ pending: 발송 대기 중")
        print("   📤 sent: 발송 완료")
        print("   📬 delivered: 전달 완료")  
        print("   👁️ read: 읽음 완료")
        print("   ❌ failed: 발송 실패")
        sys.exit(0)
    else:
        print("\n💥 작업 중 오류가 발생했습니다.")
        sys.exit(1)

if __name__ == '__main__':
    main()