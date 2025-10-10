#!/usr/bin/env python3
"""
Will Data Creation Script for DMS
UserInfo 테이블의 사용자 수에 맞춰 1:1로 Will 데이터를 생성하는 스크립트 (업데이트된 컬럼 구조)

Usage:
    python create_will_data.py [--dry-run]
    
Example:
    python create_will_data.py
    python create_will_data.py --dry-run
"""

import sys
import os
import argparse
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 환경 변수 로드
load_dotenv()

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 로깅 시스템 import
from utils.logging_config import get_dms_logger, log_info, log_error, log_warning, log_debug

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from models.userinfo import create_userinfo_model

def create_app():
    """Flask 애플리케이션 생성"""
    app = Flask(__name__)
    app.config.from_object(Config)
    return app

def create_will_model_local(db):
    """Will 모델을 생성하는 로컬 팩토리 함수 (업데이트된 DB 구조에 맞춤)"""
    
    class Will(db.Model):
        __tablename__ = 'wills'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('UserInfo.id'), nullable=False)
        subject = db.Column(db.String(255))
        body = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        lastmodified_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def to_dict(self):
            return {
                'id': self.id,
                'user_id': self.user_id,
                'subject': self.subject,
                'body': self.body,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'lastmodified_at': self.lastmodified_at.isoformat() if self.lastmodified_at else None
            }
    
    return Will

def generate_will_content(user):
    """사용자 정보를 기반으로 Will 내용 생성 (subject와 body 분리)"""
    will_templates = [
        {
            "subject": f"Digital Legacy Will of {user.FirstName} {user.LastName}",
            "body": f"""This is the last will and testament of {user.FirstName} {user.LastName}.

I, {user.FirstName} {user.LastName}, being of sound mind and disposing memory, do hereby make, publish and declare this to be my Last Will and Testament.

FIRST: I direct that all my just debts, funeral expenses, and costs of administration be paid from my estate.

SECOND: I give, devise and bequeath all of my digital assets, including but not limited to:
- Email accounts and digital communications
- Social media accounts and profiles  
- Digital photographs and videos
- Online financial accounts
- Digital documents and files

To be managed according to the instructions set forth in this digital legacy system.

THIRD: I appoint the designated recipients in this system to receive and manage my digital legacy according to my wishes.

This will was created on {datetime.now().strftime('%B %d, %Y')} through the Digital Memory System.

Signed: {user.FirstName} {user.LastName}
Email: {user.Email}
Member Grade: {user.Grade}"""
        },
        {
            "subject": f"Personal Memory Archive - {user.FirstName} {user.LastName}",
            "body": f"""Dear Family and Friends,

This digital will contains my personal memories, thoughts, and final wishes that I want to share with you through the Digital Memory System.

About Me:
Name: {user.FirstName} {user.LastName}
Email: {user.Email}
Member Grade: {user.Grade}

My Digital Legacy Instructions:
1. Please preserve my digital memories and share them with family members
2. Use my digital assets responsibly and in accordance with my values
3. Continue to honor my memory through the stories and experiences we shared

Personal Message:
Thank you for being part of my life journey. This digital legacy system will help ensure that our memories together are preserved for future generations.

The love and connections we built together will continue to live on through these digital memories.

With love and gratitude,
{user.FirstName} {user.LastName}

Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        },
        {
            "subject": f"Final Instructions and Wishes - {user.FirstName} {user.LastName}",
            "body": f"""DIGITAL WILL AND FINAL INSTRUCTIONS

Name: {user.FirstName} {user.LastName}
Email: {user.Email}
Membership Level: {user.Grade}
Document Created: {datetime.now().strftime('%Y-%m-%d')}

DIGITAL ASSET DISTRIBUTION:
This document serves as my official digital will, created through the Digital Memory System platform.

My Wishes:
- All digital memories, photos, and documents stored in this system should be shared with my designated recipients
- My online accounts and digital presence should be managed according to the privacy settings I have established
- Please respect my digital privacy while honoring my memory

Special Instructions:
- Share my favorite memories and stories with future generations
- Use this digital legacy to remember the good times we shared
- Continue the traditions and values that were important to me

I trust that this digital legacy system will help preserve my memory and maintain our connections even after I'm gone.

This is my final digital testament, created with love and thoughtful consideration for those I leave behind.

{user.FirstName} {user.LastName}
Digital Legacy Created: {datetime.now().strftime('%B %Y')}"""
        }
    ]
    
    # 사용자 ID를 기반으로 템플릿 선택 (순환)
    template_index = (user.id - 1) % len(will_templates)
    return will_templates[template_index]

def create_will_data(dry_run=False):
    """UserInfo 데이터를 기반으로 Will 데이터를 1:1로 생성 (업데이트된 구조)"""
    
    # Flask 앱 및 DB 초기화
    app = create_app()
    db = SQLAlchemy(app)
    UserInfo = create_userinfo_model(db)
    Will = create_will_model_local(db)
    
    success_count = 0
    error_count = 0
    errors = []
    
    with app.app_context():
        try:
            # 데이터베이스 연결 테스트
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
            log_info("✅ 데이터베이스 연결 성공")
            print("✅ 데이터베이스 연결 성공")
        except Exception as e:
            log_error(f"❌ 데이터베이스 연결 실패: {e}")
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
        
        mode = "DRY RUN 모드" if dry_run else "실제 Will 데이터 생성"
        log_info(f"{mode} 시작 - 총 {len(users)}명 사용자 처리 예정")
        print(f"\n{'='*60}")
        print(f"{mode} - 시작")
        print(f"{'='*60}")
        
        for user in users:
            try:
                # 이미 Will이 있는지 확인 (user_id로 중복 체크)
                existing_will = Will.query.filter_by(user_id=user.id).first()
                
                if existing_will:
                    print(f"⚠️  사용자 {user.id:2d}: {user.FirstName} {user.LastName} - 이미 Will 존재 (ID: {existing_will.id})")
                    continue
                
                # Will 내용 생성
                will_content = generate_will_content(user)
                
                # Will 객체 생성 (업데이트된 구조)
                new_will = Will(
                    user_id=user.id,
                    subject=will_content["subject"],
                    body=will_content["body"],
                    created_at=datetime.utcnow(),
                    lastmodified_at=datetime.utcnow()
                )
                
                if not dry_run:
                    # DB에 추가
                    db.session.add(new_will)
                
                print(f"✅ 사용자 {user.id:2d}: {user.FirstName} {user.LastName} -> Will 생성")
                print(f"   📝 제목: {will_content['subject']}")
                print(f"   📄 내용: {will_content['body'][:80]}...")
                success_count += 1
                
            except Exception as e:
                print(f"❌ 사용자 {user.id}: {user.FirstName} {user.LastName} - 처리 중 오류: {str(e)}")
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
    print(f"📊 Will 생성 결과 요약")
    print(f"{'='*60}")
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {error_count}개")
    print(f"📊 총 처리: {len(users)}명")
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
    parser = argparse.ArgumentParser(description='UserInfo 사용자에 맞춰 Will 데이터를 1:1로 생성 (업데이트된 구조)')
    parser.add_argument('--dry-run', action='store_true', help='실제 삽입 없이 테스트만 실행')
    parser.add_argument('--version', action='version', version='DMS Will Creator v2.0 (Updated Schema)')
    
    args = parser.parse_args()
    
    print("🚀 DMS Will 데이터 생성 도구 v2.0")
    print("📋 UserInfo 사용자들에게 1:1로 Will을 생성합니다. (user_id, subject, lastmodified_at 포함)")
    
    if args.dry_run:
        print("🔍 DRY RUN 모드로 실행합니다.")
    
    # 환경 변수 확인
    required_env_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_NAME']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 다음 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        print("💡 .env 파일을 확인하거나 환경 변수를 설정해주세요.")
        sys.exit(1)
    
    # Will 데이터 생성 실행
    success = create_will_data(args.dry_run)
    
    if success:
        print("\n🎉 Will 데이터 생성이 성공적으로 완료되었습니다!")
        sys.exit(0)
    else:
        print("\n💥 작업 중 오류가 발생했습니다.")
        sys.exit(1)

if __name__ == '__main__':
    main()