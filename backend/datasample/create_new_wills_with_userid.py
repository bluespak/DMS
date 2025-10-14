#!/usr/bin/env python3
"""
새로운 Will 데이터 생성기 (user_id 문자열 기반)
- user_id 필드가 문자열로 변경된 새로운 스키마에 맞춰 Will 데이터 생성
- 기존 Will 데이터를 모두 삭제하고 새로운 데이터로 교체
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import create_app
from models.userinfo import create_userinfo_model
from models.will import create_will_model
from datetime import datetime
import random

def create_new_wills():
    """새로운 user_id 기반 Will 데이터 생성"""
    
    app = create_app()
    
    with app.app_context():
        from flask_sqlalchemy import SQLAlchemy
        db = SQLAlchemy()
        db.init_app(app)
        
        # 모델 생성
        UserInfo = create_userinfo_model(db)
        Will = create_will_model(db)
        
        # 기존 Will 데이터 모두 삭제
        print("🗑️ 기존 Will 데이터 삭제 중...")
        Will.query.delete()
        db.session.commit()
        print("✅ 기존 Will 데이터 삭제 완료")
        
        # 모든 사용자 조회
        users = UserInfo.query.all()
        if not users:
            print("❌ 사용자 데이터가 없습니다. 먼저 create_new_users_with_userid.py를 실행하세요.")
            return
        
        print(f"👥 {len(users)}명의 사용자에 대한 Will 데이터 생성 중...")
        
        # Will 템플릿들
        will_templates = [
            # 템플릿 1: 정식 유언서
            {
                "subject": "Digital Legacy Will of {name}",
                "body": """This is the last will and testament of {name}.

I, {name}, being of sound mind and disposing memory, do hereby make, publish and declare this to be my Last Will and Testament.

FIRST: I direct that all my just debts, funeral expenses, and costs of administration be paid from my estate.

SECOND: I give, devise and bequeath all of my digital assets, including but not limited to:
- Email accounts and digital communications
- Social media accounts and profiles  
- Digital photographs and videos
- Online financial accounts
- Digital documents and files

To be managed according to the instructions set forth in this digital legacy system.

THIRD: I appoint the designated recipients in this system to receive and manage my digital legacy according to my wishes.

This will was created on {date} through the Digital Memory System.

Signed: {name}
Email: {email}
Member Grade: {grade}"""
            },
            # 템플릿 2: 개인적인 메모리 아카이브
            {
                "subject": "Personal Memory Archive - {name}",
                "body": """Dear Family and Friends,

This digital will contains my personal memories, thoughts, and final wishes that I want to share with you through the Digital Memory System.

About Me:
Name: {name}
Email: {email}
Member Grade: {grade}

My Digital Legacy Instructions:
1. Please preserve my digital memories and share them with family members
2. Use my digital assets responsibly and in accordance with my values
3. Continue to honor my memory through the stories and experiences we shared

Personal Message:
Thank you for being part of my life journey. This digital legacy system will help ensure that our memories together are preserved for future generations.

The love and connections we built together will continue to live on through these digital memories.

With love and gratitude,
{name}

Created: {date}"""
            },
            # 템플릿 3: 디지털 자산 관리 지침
            {
                "subject": "Final Instructions and Wishes - {name}",
                "body": """DIGITAL WILL AND FINAL INSTRUCTIONS

Name: {name}
Email: {email}
Membership Level: {grade_full}
Document Created: {date_short}

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

{name}
Digital Legacy Created: {month} {year}"""
            }
        ]
        
        # 각 사용자에 대해 Will 생성
        for index, user in enumerate(users, 1):
            # 템플릿 순환 선택
            template = will_templates[index % len(will_templates)]
            
            # 이름 조합
            full_name = f"{user.FirstName} {user.LastName}"
            
            # 등급 전체 이름 매핑
            grade_mapping = {
                "Pre": "Premium",
                "Gol": "Gold", 
                "Sta": "Standard"
            }
            grade_full = grade_mapping.get(user.Grade, "Standard")
            
            # 날짜 정보
            now = datetime.now()
            date_str = now.strftime("%B %d, %Y")
            date_short = now.strftime("%Y-%m-%d")
            month = now.strftime("%B")
            year = now.strftime("%Y")
            
            # 템플릿에 데이터 삽입
            subject = template["subject"].format(
                name=full_name
            )
            
            body = template["body"].format(
                name=full_name,
                email=user.Email,
                grade=grade_full,
                grade_full=grade_full,
                date=date_str,
                date_short=date_short,
                month=month,
                year=year
            )
            
            # Will 생성
            new_will = Will(
                user_id=user.user_id,  # 문자열 user_id 사용
                subject=subject,
                body=body
            )
            
            db.session.add(new_will)
            
            if index % 10 == 0:
                print(f"  📜 {index}개 Will 처리 완료...")
        
        # 데이터베이스에 저장
        db.session.commit()
        print(f"✅ 총 {len(users)}개의 새로운 Will 데이터 생성 완료!")
        
        # 생성된 데이터 확인
        total_wills = Will.query.count()
        print(f"📊 데이터베이스 총 Will 수: {total_wills}개")
        
        # 처음 3개 Will 샘플 출력
        print("\n🔍 생성된 Will 샘플:")
        sample_wills = Will.query.limit(3).all()
        for will in sample_wills:
            print(f"  - Will ID {will.id}: {will.subject}")
            print(f"    사용자: {will.user_id}")
            print(f"    내용 길이: {len(will.body)} 문자")
            print()

if __name__ == "__main__":
    create_new_wills()