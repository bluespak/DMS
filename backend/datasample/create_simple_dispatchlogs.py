#!/usr/bin/env python3
"""
간단한 DispatchLog 데이터 생성
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import app, db, Will
from models.dispatchlog import create_dispatchlog_model
from models.recipients import create_recipient_model
from datetime import datetime, timedelta
import random

def create_simple_dispatchlogs():
    """간단한 DispatchLog 데이터 생성"""
    
    with app.app_context():
        print("📋 간단한 DispatchLog 데이터 생성 시작...")
        
        # 모델 생성
        DispatchLog = create_dispatchlog_model(db)
        Recipients = create_recipient_model(db)
        
        # 기존 DispatchLog 데이터 삭제
        DispatchLog.query.delete()
        db.session.commit()
        
        # 모든 Will 조회
        wills = Will.query.all()
        
        # DispatchLog 템플릿
        dispatch_templates = [
            # Will 1 - Michael Anderson
            [
                ("emma.anderson@sample.recipient.com", "Emma Anderson", "SENT", -5),
                ("dr.robert.smith@sample.recipient.com", "Dr. Robert Smith", "DELIVERED", -3),
                ("mason.taylor@sample.recipient.com", "Mason Taylor", "PENDING", 0)
            ],
            # Will 2 - Sarah Johnson  
            [
                ("olivia.johnson@sample.recipient.com", "Olivia Johnson", "SENT", -7),
                ("lisa.connor@sample.recipient.com", "Attorney Lisa Connor", "DELIVERED", -4),
                ("isabella.garcia@sample.recipient.com", "Isabella Garcia", "FAILED", -2),
                ("noah.williams@sample.recipient.com", "Noah Williams", "PENDING", 0)
            ],
            # Will 3 - David Williams
            [
                ("ava.williams@sample.recipient.com", "Ava Williams", "DELIVERED", -6),
                ("lucas.martinez@sample.recipient.com", "Lucas Martinez", "SENT", -1),
                ("michael.johnson@sample.recipient.com", "CPA Michael Johnson", "PENDING", 0)
            ],
            # Will 4 - Emily Brown
            [
                ("william.brown@sample.recipient.com", "William Brown", "SENT", -8),
                ("sophia.miller@sample.recipient.com", "Sophia Miller", "DELIVERED", -5),
                ("alexander.clark@sample.recipient.com", "Alexander Clark", "FAILED", -3),
                ("jennifer.white@sample.recipient.com", "Manager Jennifer White", "PENDING", 0)
            ],
            # Will 5 - James Davis
            [
                ("charlotte.davis@sample.recipient.com", "Charlotte Davis", "DELIVERED", -4),
                ("benjamin.lewis@sample.recipient.com", "Benjamin Lewis", "SENT", -2),
                ("david.lee@sample.recipient.com", "Director David Lee", "PENDING", 0)
            ]
        ]
        
        for i, will in enumerate(wills):
            if i < len(dispatch_templates):
                dispatch_data = dispatch_templates[i]
                
                for email, name, status, days_offset in dispatch_data:
                    # 해당 Will의 수신인 중에서 이메일이 일치하는 수신인 찾기
                    recipient = Recipients.query.filter_by(will_id=will.id, recipient_email=email).first()
                    
                    if recipient:
                        # 날짜 계산 (과거 또는 현재)
                        dispatch_date = datetime.now() + timedelta(days=days_offset)
                        
                        # 상태에 따른 날짜 설정
                        sent_at = dispatch_date if status.lower() in ['sent', 'delivered', 'read'] else None
                        delivered_at = dispatch_date if status.lower() in ['delivered', 'read'] else None
                        read_at = dispatch_date if status.lower() == 'read' else None
                        
                        dispatch_log = DispatchLog(
                            will_id=will.id,
                            recipient_id=recipient.id,
                            sent_at=sent_at,
                            delivered_at=delivered_at,
                            read_at=read_at,
                            status=status.lower()
                        )
                        db.session.add(dispatch_log)
                    else:
                        print(f"  ⚠️ 수신인을 찾을 수 없음: {email} (Will ID: {will.id})")
                
                print(f"  📧 Will ID {will.id} ({will.user_id}): {len(dispatch_data)}개 DispatchLog 생성")
        
        db.session.commit()
        print("✅ DispatchLog 데이터 생성 완료!")
        
        # 결과 확인
        total_logs = DispatchLog.query.count()
        print(f"📊 총 DispatchLog 수: {total_logs}개")

if __name__ == "__main__":
    create_simple_dispatchlogs()