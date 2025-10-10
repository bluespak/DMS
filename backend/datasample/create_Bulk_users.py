#!/usr/bin/env python3
"""
Bulk User Creation Script for DMS
파라미터로 받은 JSON 파일을 읽어서 UserInfo 테이블에 일괄 삽입하는 스크립트

Usage:
    python create_Bulk_users.py <json_file_path>
    
Example:
    python create_Bulk_users.py sample_new_users_50.json
    python create_Bulk_users.py ../doc/sample_users_50.json
"""

import sys
import os
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 환경 변수 로드
load_dotenv()

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from models.userinfo import create_userinfo_model

def create_app():
    """Flask 애플리케이션 생성"""
    app = Flask(__name__)
    app.config.from_object(Config)
    return app

def parse_date(date_string):
    """날짜 문자열을 datetime.date 객체로 변환"""
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError as e:
        print(f"Date parsing error: {e}")
        return None

def load_json_file(file_path):
    """JSON 파일을 로드하여 사용자 데이터 반환"""
    try:
        # 상대 경로 처리
        if not os.path.isabs(file_path):
            # datasample 폴더 기준으로 상대 경로 처리
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_dir, file_path)
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(f"✅ JSON 파일 로드 성공: {file_path}")
            print(f"📊 총 {len(data)}명의 사용자 데이터 발견")
            return data
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 오류: {e}")
        return None
    except Exception as e:
        print(f"❌ 파일 로드 오류: {e}")
        return None

def validate_user_data(user_data):
    """사용자 데이터 유효성 검사"""
    required_fields = ['LastName', 'FirstName', 'Email']
    
    for field in required_fields:
        if field not in user_data or not user_data[field]:
            return False, f"필수 필드 누락: {field}"
    
    # 이메일 기본 검증
    if '@' not in user_data['Email']:
        return False, "유효하지 않은 이메일 형식"
    
    return True, None

def create_bulk_users(json_file_path, dry_run=False):
    """JSON 파일의 사용자 데이터를 DB에 일괄 삽입"""
    
    # JSON 데이터 로드
    users_data = load_json_file(json_file_path)
    if not users_data:
        return False
    
    # Flask 앱 및 DB 초기화
    app = create_app()
    db = SQLAlchemy(app)
    UserInfo = create_userinfo_model(db)
    
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
        
        print(f"\n{'='*50}")
        print(f"{'DRY RUN 모드' if dry_run else '실제 데이터 삽입'} - 시작")
        print(f"{'='*50}")
        
        for idx, user_data in enumerate(users_data, 1):
            try:
                # 데이터 유효성 검사
                is_valid, error_msg = validate_user_data(user_data)
                if not is_valid:
                    print(f"⚠️  사용자 {idx}: 유효성 검사 실패 - {error_msg}")
                    error_count += 1
                    errors.append(f"사용자 {idx}: {error_msg}")
                    continue
                
                # 날짜 변환
                dob = None
                if user_data.get('DOB'):
                    dob = parse_date(user_data['DOB'])
                
                # UserInfo 객체 생성
                new_user = UserInfo(
                    LastName=user_data['LastName'],
                    FirstName=user_data['FirstName'],
                    Email=user_data['Email'],
                    Grade=user_data.get('Grade', 'Standard'),
                    DOB=dob
                )
                
                if not dry_run:
                    # DB에 추가
                    db.session.add(new_user)
                
                print(f"✅ 사용자 {idx:2d}: {user_data['FirstName']} {user_data['LastName']} - {user_data['Email']}")
                success_count += 1
                
            except Exception as e:
                print(f"❌ 사용자 {idx}: 처리 중 오류 - {str(e)}")
                error_count += 1
                errors.append(f"사용자 {idx}: {str(e)}")
        
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
    print(f"\n{'='*50}")
    print(f"📊 처리 결과 요약")
    print(f"{'='*50}")
    print(f"✅ 성공: {success_count}명")
    print(f"❌ 실패: {error_count}명")
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
    parser = argparse.ArgumentParser(description='JSON 파일에서 사용자 데이터를 읽어 DB에 일괄 삽입')
    parser.add_argument('json_file', help='사용자 데이터가 담긴 JSON 파일 경로')
    parser.add_argument('--dry-run', action='store_true', help='실제 삽입 없이 테스트만 실행')
    parser.add_argument('--version', action='version', version='DMS Bulk User Creator v1.0')
    
    args = parser.parse_args()
    
    print("🚀 DMS 사용자 일괄 생성 도구")
    print(f"📁 JSON 파일: {args.json_file}")
    
    if args.dry_run:
        print("🔍 DRY RUN 모드로 실행합니다.")
    
    # 환경 변수 확인
    required_env_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_NAME']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 다음 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        print("💡 .env 파일을 확인하거나 환경 변수를 설정해주세요.")
        sys.exit(1)
    
    # 사용자 일괄 생성 실행
    success = create_bulk_users(args.json_file, args.dry_run)
    
    if success:
        print("\n🎉 작업이 성공적으로 완료되었습니다!")
        sys.exit(0)
    else:
        print("\n💥 작업 중 오류가 발생했습니다.")
        sys.exit(1)

if __name__ == '__main__':
    main()