#!/usr/bin/env python3
"""
새로운 user_id 기반 샘플 데이터 생성
- 기존 데이터 삭제 후 새로운 user_id 포함 데이터 생성
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Flask 앱과 이미 정의된 모델들 import
from app.app import app, db, UserInfo, Will
from datetime import datetime, date
import random

def create_sample_data():
    """새로운 user_id 기반 샘플 데이터 생성"""
    
    with app.app_context():
        print("🔧 샘플 데이터 생성 시작...")
        
        # 기존 데이터 삭제
        print("🗑️ 기존 데이터 삭제 중...")
        Will.query.delete()
        UserInfo.query.delete()
        db.session.commit()
        print("✅ 기존 데이터 삭제 완료!")
        
        # 샘플 사용자 데이터
        sample_users = [
            ("Michael", "Anderson", "michael.anderson@example.com", "Pre"),
            ("Sarah", "Johnson", "sarah.johnson@example.com", "Gol"), 
            ("David", "Williams", "david.williams@example.com", "Sta"),
            ("Emily", "Brown", "emily.brown@example.com", "Pre"),
            ("James", "Davis", "james.davis@example.com", "Gol")
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

FIRST: I direct that all my just debts, funeral expenses, and costs of administration be paid from my estate.

SECOND: I give, devise and bequeath all of my digital assets, including but not limited to:
- Email accounts and digital communications
- Social media accounts and profiles  
- Digital photographs and videos
- Online financial accounts
- Digital documents and files

To be managed according to the instructions set forth in this digital legacy system.

THIRD: I appoint the designated recipients in this system to receive and manage my digital legacy according to my wishes.

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
        
        print(f"\n📊 샘플 데이터 생성 완료!")
        print(f"   👥 총 사용자: {total_users}명")
        print(f"   📜 총 Will: {total_wills}개")
        
        print("\n🔍 생성된 데이터 샘플:")
        for user in UserInfo.query.all():
            print(f"  - {user.user_id}: {user.FirstName} {user.LastName} ({user.Grade})")

if __name__ == "__main__":
    create_sample_data()