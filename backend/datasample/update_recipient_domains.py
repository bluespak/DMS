#!/usr/bin/env python3
"""
Recipients Email Domain Update Script for DMS
모든 recipient 이메일 도메인을 @sample.recipient.com으로 변경하는 스크립트

Usage:
    python update_recipient_domains.py [--dry-run]
"""

import sys
import os
import argparse
import re
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

def create_recipient_model(db):
    """Recipient 모델 생성"""
    
    class Recipient(db.Model):
        __tablename__ = 'recipients'
        id = db.Column(db.Integer, primary_key=True)
        will_id = db.Column(db.Integer, nullable=False)
        recipient_email = db.Column(db.String(255), nullable=False)
        recipient_name = db.Column(db.String(100))
        relatedCode = db.Column(db.String(1))
        
        def to_dict(self):
            return {
                'id': self.id,
                'will_id': self.will_id,
                'recipient_email': self.recipient_email,
                'recipient_name': self.recipient_name,
                'relatedCode': self.relatedCode
            }
    
    return Recipient

def update_recipient_domains(dry_run=False):
    """모든 recipient 이메일 도메인을 @sample.recipient.com으로 변경"""
    
    # Flask 앱 및 DB 초기화
    app = create_app()
    db = SQLAlchemy(app)
    Recipient = create_recipient_model(db)
    
    success_count = 0
    error_count = 0
    errors = []
    
    with app.app_context():
        try:
            # 데이터베이스 연결 테스트
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
            print("✅ 데이터베이스 연결 성공")
        except Exception as e:
            print(f"❌ 데이터베이스 연결 실패: {e}")
            return False
        
        # 모든 Recipients 조회
        try:
            recipients = Recipient.query.all()
            print(f"📊 총 {len(recipients)}개의 recipient 발견")
        except Exception as e:
            print(f"❌ Recipients 데이터 조회 실패: {e}")
            return False
        
        if not recipients:
            print("⚠️  Recipients 데이터가 없습니다.")
            return False
        
        # 현재 도메인 통계
        print(f"\n📈 현재 도메인 분포:")
        domain_stats = {}
        for recipient in recipients:
            if '@' in recipient.recipient_email:
                domain = recipient.recipient_email.split('@')[1]
                domain_stats[domain] = domain_stats.get(domain, 0) + 1
        
        for domain, count in sorted(domain_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"   {domain}: {count}개")
        
        print(f"\n{'='*60}")
        print(f"{'DRY RUN 모드' if dry_run else '실제 이메일 도메인 업데이트'} - 시작")
        print(f"{'='*60}")
        
        for recipient in recipients:
            try:
                # 현재 이메일에서 사용자명 추출
                if '@' in recipient.recipient_email:
                    username = recipient.recipient_email.split('@')[0]
                    old_email = recipient.recipient_email
                    new_email = f"{username}@sample.recipient.com"
                    
                    # 이미 sample.recipient.com 도메인인 경우 건너뛰기
                    if recipient.recipient_email.endswith('@sample.recipient.com'):
                        continue
                    
                    print(f"🔄 ID {recipient.id:2d}: {recipient.recipient_name}")
                    print(f"   변경 전: {old_email}")
                    print(f"   변경 후: {new_email}")
                    
                    if not dry_run:
                        recipient.recipient_email = new_email
                    
                    success_count += 1
                else:
                    print(f"⚠️  ID {recipient.id}: 잘못된 이메일 형식 - {recipient.recipient_email}")
                    error_count += 1
                    errors.append(f"ID {recipient.id}: 잘못된 이메일 형식")
                
            except Exception as e:
                print(f"❌ ID {recipient.id}: 처리 중 오류: {str(e)}")
                error_count += 1
                errors.append(f"ID {recipient.id}: {str(e)}")
        
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
            print(f"\n📋 DRY RUN 완료 - 실제 데이터는 변경되지 않았습니다.")
        
        # 업데이트 후 도메인 확인 (실제 실행한 경우에만)
        if not dry_run and success_count > 0:
            print(f"\n📈 업데이트 후 도메인 확인:")
            updated_recipients = Recipient.query.all()
            new_domain_stats = {}
            for recipient in updated_recipients:
                if '@' in recipient.recipient_email:
                    domain = recipient.recipient_email.split('@')[1]
                    new_domain_stats[domain] = new_domain_stats.get(domain, 0) + 1
            
            for domain, count in sorted(new_domain_stats.items(), key=lambda x: x[1], reverse=True):
                print(f"   {domain}: {count}개")
    
    # 결과 요약
    print(f"\n{'='*60}")
    print(f"📊 이메일 도메인 업데이트 결과 요약")
    print(f"{'='*60}")
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {error_count}개")
    print(f"📊 총 처리: {len(recipients)}개")
    if success_count + error_count > 0:
        print(f"📈 성공률: {(success_count/(success_count+error_count)*100):.1f}%")
    
    if errors:
        print(f"\n⚠️  오류 목록:")
        for error in errors[:5]:  # 최대 5개까지만 표시
            print(f"   - {error}")
        if len(errors) > 5:
            print(f"   ... 및 {len(errors)-5}개 추가 오류")
    
    return success_count > 0

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='모든 recipient 이메일 도메인을 @sample.recipient.com으로 변경')
    parser.add_argument('--dry-run', action='store_true', help='실제 변경 없이 테스트만 실행')
    parser.add_argument('--version', action='version', version='DMS Recipient Domain Updater v1.0')
    
    args = parser.parse_args()
    
    print("🚀 DMS Recipients 이메일 도메인 업데이트 도구 v1.0")
    print("📧 모든 recipient 이메일을 @sample.recipient.com 도메인으로 변경합니다.")
    print("🔒 이는 실제 이메일로 데이터가 전송되는 것을 방지하기 위함입니다.")
    
    if args.dry_run:
        print("🔍 DRY RUN 모드로 실행합니다.")
    
    # 환경 변수 확인
    required_env_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_NAME']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 다음 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        print("💡 .env 파일을 확인하거나 환경 변수를 설정해주세요.")
        sys.exit(1)
    
    # 도메인 업데이트 실행
    success = update_recipient_domains(args.dry_run)
    
    if success:
        print("\n🎉 Recipients 이메일 도메인 업데이트가 성공적으로 완료되었습니다!")
        print("🔒 이제 모든 recipient 이메일이 안전한 테스트 도메인을 사용합니다.")
        sys.exit(0)
    else:
        print("\n💥 작업 중 오류가 발생했습니다.")
        sys.exit(1)

if __name__ == '__main__':
    main()