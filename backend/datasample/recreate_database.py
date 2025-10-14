#!/usr/bin/env python3
"""
데이터베이스 완전 재생성 스크립트
- 기존 테이블 모두 삭제
- 새로운 스키마로 테이블 재생성
- 새로운 사용자 및 Will 데이터 생성
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Flask 앱 직접 import
from app.app import app, db
from models.userinfo import create_userinfo_model
from models.will import create_will_model
from datetime import datetime, date
import random

def recreate_database():
    """데이터베이스 완전 재생성"""
    
    with app.app_context():
        
        print("🔧 데이터베이스 재생성 시작...")
        
        # 모든 테이블 삭제 및 재생성
        print("🗑️ 기존 테이블 삭제 중...")
        db.drop_all()
        
        print("🏗️ 새로운 테이블 생성 중...")
        db.create_all()
        
        print("✅ 데이터베이스 스키마 재생성 완료!")
        
        # 모델 생성
        UserInfo = create_userinfo_model(db)
        Will = create_will_model(db)
        
        # 샘플 사용자 데이터
        sample_users = [
            ("Michael", "Anderson", "michael.anderson@example.com", "Pre"),
            ("Sarah", "Johnson", "sarah.johnson@example.com", "Gol"), 
            ("David", "Williams", "david.williams@example.com", "Sta")
        ]
        
        print("👥 사용자 데이터 생성 중...")
        
        for index, (first_name, last_name, email, grade) in enumerate(sample_users, 1):
            # user_id 생성
            user_id = f"{first_name.lower()}.{last_name.lower()}.{index:03d}"
            
            # 랜덤 생년월일
            birth_year = random.randint(1960, 1990)
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)
            dob = date(birth_year, birth_month, birth_day)
            
            # 새 사용자 생성
            new_user = UserInfo(
                user_id=user_id,
                FirstName=first_name,
                LastName=last_name,
                Email=email,
                Grade=grade,
                DOB=dob
            )
            
            db.session.add(new_user)
            print(f"  📝 사용자 생성: {user_id} ({first_name} {last_name})")
        
        db.session.commit()
        print("✅ 사용자 데이터 생성 완료!")
        
        # Will 데이터 생성
        print("📜 Will 데이터 생성 중...")
        
        users = UserInfo.query.all()
        for user in users:
            full_name = f"{user.FirstName} {user.LastName}"
            
            subject = f"Digital Legacy Will of {full_name}"
            body = f"""This is the last will and testament of {full_name}.

I, {full_name}, being of sound mind and disposing memory, do hereby make, publish and declare this to be my Last Will and Testament.

This will was created on {datetime.now().strftime("%B %d, %Y")} through the Digital Memory System.

Signed: {full_name}
Email: {user.Email}
Member Grade: {user.Grade}"""
            
            new_will = Will(
                user_id=user.user_id,  # 문자열 user_id 사용
                subject=subject,
                body=body
            )
            
            db.session.add(new_will)
            print(f"  📜 Will 생성: {user.user_id}")
        
        db.session.commit()
        print("✅ Will 데이터 생성 완료!")
        
        # 결과 확인
        total_users = UserInfo.query.count()
        total_wills = Will.query.count()
        
        print(f"\n📊 데이터베이스 재생성 완료!")
        print(f"   👥 총 사용자: {total_users}명")
        print(f"   📜 총 Will: {total_wills}개")
        
        print("\n🔍 생성된 데이터 샘플:")
        for user in UserInfo.query.all():
            print(f"  - {user.user_id}: {user.FirstName} {user.LastName} ({user.Grade})")

if __name__ == "__main__":
    recreate_database()