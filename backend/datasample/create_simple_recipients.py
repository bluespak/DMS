#!/usr/bin/env python3
"""
간단한 수신인 데이터 생성
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import app, db, Will
from models.recipients import create_recipient_model

def create_simple_recipients():
    """간단한 수신인 데이터 생성"""
    
    with app.app_context():
        print("👥 간단한 수신인 데이터 생성 시작...")
        
        # Recipients 모델 생성
        Recipients = create_recipient_model(db)
        
        # 기존 수신인 데이터 삭제
        Recipients.query.delete()
        db.session.commit()
        
        # 모든 Will 조회
        wills = Will.query.all()
        
        # 수신인 템플릿
        recipients_templates = [
            # Will 1 - Michael Anderson
            [
                ("Emma Anderson", "emma.anderson@sample.recipient.com", "F"),  # Family
                ("Dr. Robert Smith", "dr.robert.smith@sample.recipient.com", "B"),  # Business
                ("Mason Taylor", "mason.taylor@sample.recipient.com", "C")  # Close Friend
            ],
            # Will 2 - Sarah Johnson  
            [
                ("Olivia Johnson", "olivia.johnson@sample.recipient.com", "F"),
                ("Attorney Lisa Connor", "lisa.connor@sample.recipient.com", "B"), 
                ("Isabella Garcia", "isabella.garcia@sample.recipient.com", "C"),
                ("Noah Williams", "noah.williams@sample.recipient.com", "R")  # Relative
            ],
            # Will 3 - David Williams
            [
                ("Ava Williams", "ava.williams@sample.recipient.com", "F"),
                ("Lucas Martinez", "lucas.martinez@sample.recipient.com", "C"),
                ("CPA Michael Johnson", "michael.johnson@sample.recipient.com", "B")
            ],
            # Will 4 - Emily Brown
            [
                ("William Brown", "william.brown@sample.recipient.com", "F"),
                ("Sophia Miller", "sophia.miller@sample.recipient.com", "R"),
                ("Alexander Clark", "alexander.clark@sample.recipient.com", "C"),
                ("Manager Jennifer White", "jennifer.white@sample.recipient.com", "B")
            ],
            # Will 5 - James Davis
            [
                ("Charlotte Davis", "charlotte.davis@sample.recipient.com", "F"),
                ("Benjamin Lewis", "benjamin.lewis@sample.recipient.com", "C"),
                ("Director David Lee", "david.lee@sample.recipient.com", "B")
            ]
        ]
        
        for i, will in enumerate(wills):
            if i < len(recipients_templates):
                recipients_data = recipients_templates[i]
                
                for name, email, code in recipients_data:
                    recipient = Recipients(
                        will_id=will.id,
                        recipient_name=name,
                        recipient_email=email,
                        relatedCode=code
                    )
                    db.session.add(recipient)
                
                print(f"  📧 Will ID {will.id} ({will.user_id}): {len(recipients_data)}명 수신인 생성")
        
        db.session.commit()
        print("✅ 수신인 데이터 생성 완료!")
        
        # 결과 확인
        total_recipients = Recipients.query.count()
        print(f"📊 총 수신인 수: {total_recipients}명")

if __name__ == "__main__":
    create_simple_recipients()