def create_dispatchlog_model(db):
    """DispatchLog 모델을 생성하는 팩토리 함수"""
    
    class DispatchLog(db.Model):
        __tablename__ = 'dispatch_log'
        id = db.Column(db.Integer, primary_key=True)
        will_id = db.Column(db.Integer, db.ForeignKey('wills.id'), nullable=False)
        recipient_id = db.Column(db.Integer, db.ForeignKey('recipients.id'), nullable=False)
        sent_at = db.Column(db.DateTime)
        delivered_at = db.Column(db.DateTime)  # 수신자 메일함 전달 시간
        read_at = db.Column(db.DateTime)       # 수신자 읽음 확인 시간
        status = db.Column(db.Enum('pending', 'sent', 'delivered', 'read', 'failed'), default='pending')
        
        def to_dict(self):
            return {
                'id': self.id,
                'will_id': self.will_id,
                'recipient_id': self.recipient_id,
                'sent_at': self.sent_at.isoformat() if self.sent_at else None,
                'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
                'read_at': self.read_at.isoformat() if self.read_at else None,
                'status': self.status
            }
    
    return DispatchLog
