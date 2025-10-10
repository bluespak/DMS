#!/usr/bin/env python3
"""
Recipients Data Creation Script for DMS
각 Will당 1~3명의 관련 사람들을 recipients 테이블에 생성하는 스크립트

Usage:
    python create_recipients_data.py [--dry-run]
    
Example:
    python create_recipients_data.py
    python create_recipients_data.py --dry-run
"""

import sys
import os
import argparse
import random
from datetime import datetime
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
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        lastmodified_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    class Recipient(db.Model):
        __tablename__ = 'recipients'
        id = db.Column(db.Integer, primary_key=True)
        will_id = db.Column(db.Integer, db.ForeignKey('wills.id'), nullable=False)
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
    
    return Will, Recipient

def generate_recipient_data():
    """다양한 관계의 수신자 데이터 템플릿"""
    
    # 관계 코드 정의
    relation_codes = {
        'F': 'Family',      # 가족
        'R': 'Relative',    # 친척
        'C': 'Close Friend', # 친한 친구
        'B': 'Business',    # 비즈니스 관계
        'O': 'Other'        # 기타
    }
    
    # 수신자 템플릿 (이름, 이메일 도메인, 관계코드)
    # 보안상 모든 이메일을 sample.recipient.com 도메인으로 설정
    safe_domain = "sample.recipient.com"
    recipient_templates = [
        # 가족 관계
        ("James Wilson", safe_domain, "F"),
        ("Mary Johnson", safe_domain, "F"),
        ("Michael Brown", safe_domain, "F"),
        ("Sarah Davis", safe_domain, "F"),
        ("David Miller", safe_domain, "F"),
        ("Emma Wilson", safe_domain, "F"),
        ("John Anderson", safe_domain, "F"),
        ("Lisa Thompson", safe_domain, "F"),
        
        # 친척 관계
        ("Robert Garcia", safe_domain, "R"),
        ("Jennifer Martinez", safe_domain, "R"),
        ("William Rodriguez", safe_domain, "R"),
        ("Jessica Lopez", safe_domain, "R"),
        ("Christopher Gonzalez", safe_domain, "R"),
        ("Amanda Hernandez", safe_domain, "R"),
        
        # 친한 친구
        ("Matthew Perez", safe_domain, "C"),
        ("Ashley Sanchez", safe_domain, "C"),
        ("Joshua Ramirez", safe_domain, "C"),
        ("Stephanie Torres", safe_domain, "C"),
        ("Daniel Flores", safe_domain, "C"),
        ("Nicole Rivera", safe_domain, "C"),
        ("Kevin Cooper", safe_domain, "C"),
        ("Melissa Reed", safe_domain, "C"),
        
        # 비즈니스 관계
        ("Steven Bailey", safe_domain, "B"),
        ("Michelle Rivera", safe_domain, "B"),
        ("Jason Cox", safe_domain, "B"),
        ("Kimberly Ward", safe_domain, "B"),
        ("Anthony Torres", safe_domain, "B"),
        
        # 기타
        ("Mark Phillips", safe_domain, "O"),
        ("Laura Campbell", safe_domain, "O"),
        ("Brian Parker", safe_domain, "O"),
        ("Rachel Evans", safe_domain, "O"),
        ("Scott Turner", safe_domain, "O"),
    ]
    
    return recipient_templates

def create_recipients_for_will(will_id, will_subject, recipient_templates):
    """특정 Will에 대한 수신자들 생성"""
    
    # 1~3명의 수신자를 랜덤하게 선택
    num_recipients = random.randint(1, 3)
    selected_templates = random.sample(recipient_templates, num_recipients)
    
    recipients = []
    
    for i, (name, email_domain, relation_code) in enumerate(selected_templates):
        # 이메일 생성 (이름 기반)
        email_prefix = name.lower().replace(" ", ".")
        email = f"{email_prefix}@{email_domain}"
        
        recipient_data = {
            'will_id': will_id,
            'recipient_name': name,
            'recipient_email': email,
            'relatedCode': relation_code
        }
        
        recipients.append(recipient_data)
    
    return recipients

def create_recipients_data(dry_run=False):
    """모든 Will에 대해 Recipients 데이터를 생성"""
    
    # Flask 앱 및 DB 초기화
    app = create_app()
    db = SQLAlchemy(app)
    Will, Recipient = create_models(db)
    
    success_count = 0
    error_count = 0
    errors = []
    total_recipients = 0
    
    with app.app_context():
        try:
            # 데이터베이스 연결 테스트
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
            print("✅ 데이터베이스 연결 성공")
        except Exception as e:
            print(f"❌ 데이터베이스 연결 실패: {e}")
            return False
        
        # 모든 Will 조회
        try:
            wills = Will.query.all()
            print(f"📊 총 {len(wills)}개의 Will 발견")
        except Exception as e:
            print(f"❌ Will 데이터 조회 실패: {e}")
            return False
        
        if not wills:
            print("⚠️  Will 데이터가 없습니다. 먼저 Will을 생성해주세요.")
            return False
        
        # 수신자 템플릿 로드
        recipient_templates = generate_recipient_data()
        
        print(f"\n{'='*60}")
        print(f"{'DRY RUN 모드' if dry_run else '실제 Recipients 데이터 생성'} - 시작")
        print(f"{'='*60}")
        
        for will in wills:
            try:
                # 이미 Recipients가 있는지 확인
                existing_recipients = Recipient.query.filter_by(will_id=will.id).all()
                
                if existing_recipients:
                    print(f"⚠️  Will {will.id:2d}: 이미 {len(existing_recipients)}명의 수신자 존재")
                    continue
                
                # Will에 대한 수신자들 생성
                recipients_data = create_recipients_for_will(
                    will.id, 
                    will.subject or f"Will #{will.id}", 
                    recipient_templates
                )
                
                print(f"✅ Will {will.id:2d}: {len(recipients_data)}명의 수신자 생성")
                print(f"   📄 제목: {(will.subject or 'No Subject')[:50]}...")
                
                # 각 수신자 정보 출력 및 DB 추가
                for recipient_data in recipients_data:
                    recipient = Recipient(
                        will_id=recipient_data['will_id'],
                        recipient_name=recipient_data['recipient_name'],
                        recipient_email=recipient_data['recipient_email'],
                        relatedCode=recipient_data['relatedCode']
                    )
                    
                    relation_names = {
                        'F': '가족', 'R': '친척', 'C': '친구', 
                        'B': '비즈니스', 'O': '기타'
                    }
                    relation_name = relation_names.get(recipient_data['relatedCode'], '알 수 없음')
                    
                    print(f"   👤 {recipient_data['recipient_name']} ({relation_name})")
                    print(f"      📧 {recipient_data['recipient_email']}")
                    
                    if not dry_run:
                        db.session.add(recipient)
                    
                    total_recipients += 1
                
                success_count += 1
                
            except Exception as e:
                print(f"❌ Will {will.id}: 처리 중 오류: {str(e)}")
                error_count += 1
                errors.append(f"Will {will.id}: {str(e)}")
        
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
    print(f"📊 Recipients 생성 결과 요약")
    print(f"{'='*60}")
    print(f"✅ 성공한 Will: {success_count}개")
    print(f"👥 총 생성된 수신자: {total_recipients}명")
    print(f"❌ 실패한 Will: {error_count}개")
    print(f"📊 총 처리된 Will: {len(wills)}개")
    if success_count + error_count > 0:
        print(f"📈 성공률: {(success_count/(success_count+error_count)*100):.1f}%")
        print(f"👥 평균 수신자 수: {(total_recipients/success_count):.1f}명/Will")
    
    # 관계별 통계
    if not dry_run and total_recipients > 0:
        with app.app_context():
            try:
                relation_stats = db.session.execute(db.text("""
                    SELECT relatedCode, COUNT(*) as count 
                    FROM recipients 
                    GROUP BY relatedCode 
                    ORDER BY count DESC
                """)).fetchall()
                
                print(f"\n📈 관계별 수신자 통계:")
                relation_names = {
                    'F': '가족', 'R': '친척', 'C': '친구', 
                    'B': '비즈니스', 'O': '기타'
                }
                for code, count in relation_stats:
                    relation_name = relation_names.get(code, '알 수 없음')
                    print(f"   {relation_name} ({code}): {count}명")
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
    parser = argparse.ArgumentParser(description='각 Will에 대해 1~3명의 Recipients 데이터를 생성')
    parser.add_argument('--dry-run', action='store_true', help='실제 삽입 없이 테스트만 실행')
    parser.add_argument('--version', action='version', version='DMS Recipients Creator v1.0')
    
    args = parser.parse_args()
    
    print("🚀 DMS Recipients 데이터 생성 도구 v1.0")
    print("👥 각 Will에 대해 1~3명의 관련 사람들을 수신자로 등록합니다.")
    
    if args.dry_run:
        print("🔍 DRY RUN 모드로 실행합니다.")
    
    # 환경 변수 확인
    required_env_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_NAME']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 다음 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        print("💡 .env 파일을 확인하거나 환경 변수를 설정해주세요.")
        sys.exit(1)
    
    # Recipients 데이터 생성 실행
    success = create_recipients_data(args.dry_run)
    
    if success:
        print("\n🎉 Recipients 데이터 생성이 성공적으로 완료되었습니다!")
        print("💡 이제 각 Will마다 1~3명의 관련 사람들이 수신자로 등록되었습니다.")
        sys.exit(0)
    else:
        print("\n💥 작업 중 오류가 발생했습니다.")
        sys.exit(1)

if __name__ == '__main__':
    main()