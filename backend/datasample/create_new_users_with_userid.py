#!/usr/bin/env python3
"""
새로운 사용자 데이터 생성기 (user_id 필드 포함)
- user_id 필드가 추가된 새로운 스키마에 맞춰 사용자 데이터 생성
- 기존 데이터를 모두 삭제하고 새로운 데이터로 교체
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import create_app
from models.userinfo import create_userinfo_model
from datetime import datetime, date
import random

def generate_user_id(first_name, last_name, index):
    """사용자 ID 생성 (예: michael.anderson.001)"""
    return f"{first_name.lower()}.{last_name.lower()}.{index:03d}"

def create_new_users():
    """새로운 user_id 필드가 포함된 사용자 데이터 생성"""
    
    app = create_app()
    
    with app.app_context():
        from flask_sqlalchemy import SQLAlchemy
        db = SQLAlchemy()
        db.init_app(app)
        
        # UserInfo 모델 생성
        UserInfo = create_userinfo_model(db)
        
        # 기존 데이터 모두 삭제
        print("🗑️ 기존 사용자 데이터 삭제 중...")
        UserInfo.query.delete()
        db.session.commit()
        print("✅ 기존 데이터 삭제 완료")
        
        # 샘플 사용자 데이터 (50명)
        sample_users = [
            ("Michael", "Anderson", "michael.anderson@example.com", "Pre"),
            ("Sarah", "Johnson", "sarah.johnson@example.com", "Gol"),
            ("David", "Williams", "david.williams@example.com", "Sta"),
            ("Emily", "Brown", "emily.brown@example.com", "Pre"),
            ("James", "Davis", "james.davis@example.com", "Gol"),
            ("Jessica", "Miller", "jessica.miller@example.com", "Sta"),
            ("Christopher", "Wilson", "christopher.wilson@example.com", "Pre"),
            ("Ashley", "Moore", "ashley.moore@example.com", "Gol"),
            ("Matthew", "Taylor", "matthew.taylor@example.com", "Sta"),
            ("Amanda", "Thomas", "amanda.thomas@example.com", "Pre"),
            ("Joshua", "Jackson", "joshua.jackson@example.com", "Gol"),
            ("Megan", "White", "megan.white@example.com", "Sta"),
            ("Daniel", "Harris", "daniel.harris@example.com", "Pre"),
            ("Lauren", "Martin", "lauren.martin@example.com", "Gol"),
            ("Andrew", "Thompson", "andrew.thompson@example.com", "Sta"),
            ("Nicole", "Garcia", "nicole.garcia@example.com", "Pre"),
            ("Kevin", "Martinez", "kevin.martinez@example.com", "Gol"),
            ("Stephanie", "Robinson", "stephanie.robinson@example.com", "Sta"),
            ("Ryan", "Clark", "ryan.clark@example.com", "Pre"),
            ("Rachel", "Rodriguez", "rachel.rodriguez@example.com", "Gol"),
            ("Brandon", "Lewis", "brandon.lewis@example.com", "Sta"),
            ("Samantha", "Lee", "samantha.lee@example.com", "Pre"),
            ("Justin", "Walker", "justin.walker@example.com", "Gol"),
            ("Brittany", "Hall", "brittany.hall@example.com", "Sta"),
            ("Tyler", "Allen", "tyler.allen@example.com", "Pre"),
            ("Kimberly", "Young", "kimberly.young@example.com", "Gol"),
            ("Jonathan", "Hernandez", "jonathan.hernandez@example.com", "Sta"),
            ("Melissa", "King", "melissa.king@example.com", "Pre"),
            ("Nathan", "Wright", "nathan.wright@example.com", "Gol"),
            ("Heather", "Lopez", "heather.lopez@example.com", "Sta"),
            ("Jason", "Hill", "jason.hill@example.com", "Pre"),
            ("Christina", "Scott", "christina.scott@example.com", "Gol"),
            ("Jacob", "Green", "jacob.green@example.com", "Sta"),
            ("Rebecca", "Adams", "rebecca.adams@example.com", "Pre"),
            ("Alexander", "Baker", "alexander.baker@example.com", "Gol"),
            ("Michelle", "Gonzalez", "michelle.gonzalez@example.com", "Sta"),
            ("Zachary", "Nelson", "zachary.nelson@example.com", "Pre"),
            ("Kayla", "Carter", "kayla.carter@example.com", "Gol"),
            ("Benjamin", "Mitchell", "benjamin.mitchell@example.com", "Sta"),
            ("Victoria", "Perez", "victoria.perez@example.com", "Pre"),
            ("Eric", "Roberts", "eric.roberts@example.com", "Gol"),
            ("Danielle", "Turner", "danielle.turner@example.com", "Sta"),
            ("Aaron", "Phillips", "aaron.phillips@example.com", "Pre"),
            ("Courtney", "Campbell", "courtney.campbell@example.com", "Gol"),
            ("Trevor", "Parker", "trevor.parker@example.com", "Sta"),
            ("Chelsea", "Evans", "chelsea.evans@example.com", "Pre"),
            ("Mason", "Edwards", "mason.edwards@example.com", "Gol"),
            ("Alexis", "Collins", "alexis.collins@example.com", "Sta"),
            ("Lucas", "Stewart", "lucas.stewart@example.com", "Pre"),
            ("Hannah", "Sanchez", "hannah.sanchez@example.com", "Gol"),
            ("Caleb", "Morris", "caleb.morris@example.com", "Sta")
        ]
        
        print("👥 새로운 사용자 데이터 생성 중...")
        
        for index, (first_name, last_name, email, grade) in enumerate(sample_users, 1):
            # user_id 생성
            user_id = generate_user_id(first_name, last_name, index)
            
            # 랜덤 생년월일 생성 (1950-1990년)
            birth_year = random.randint(1950, 1990)
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)  # 28일로 제한하여 모든 월에서 유효하도록
            dob = date(birth_year, birth_month, birth_day)
            
            # 새 사용자 생성
            new_user = UserInfo(
                user_id=user_id,  # 새로운 user_id 필드
                FirstName=first_name,
                LastName=last_name,
                Email=email,
                Grade=grade,
                DOB=dob
            )
            
            db.session.add(new_user)
            
            if index % 10 == 0:
                print(f"  📝 {index}명 처리 완료...")
        
        # 데이터베이스에 저장
        db.session.commit()
        print(f"✅ 총 {len(sample_users)}명의 새로운 사용자 데이터 생성 완료!")
        
        # 생성된 데이터 확인
        total_users = UserInfo.query.count()
        print(f"📊 데이터베이스 총 사용자 수: {total_users}명")
        
        # 처음 5명 샘플 출력
        print("\n🔍 생성된 사용자 샘플:")
        sample_users_check = UserInfo.query.limit(5).all()
        for user in sample_users_check:
            print(f"  - {user.user_id}: {user.FirstName} {user.LastName} ({user.Grade})")

if __name__ == "__main__":
    create_new_users()