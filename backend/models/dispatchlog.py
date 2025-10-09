def create_dispatchlog_model(db):
    """DispatchLog 모델을 생성하는 팩토리 함수"""
    
    class DispatchLog(db.Model):
        __tablename__ = 'dispatch_log'
        id = db.Column(db.Integer, primary_key=True)
        will_id = db.Column(db.Integer, db.ForeignKey('wills.id'), nullable=False)
        recipient_id = db.Column(db.Integer, db.ForeignKey('recipients.id'), nullable=False)
        sent_at = db.Column(db.DateTime)
        status = db.Column(db.Enum('pending', 'sent', 'failed'), default='pending')
        
        def to_dict(self):
            return {
                'id': self.id,
                'will_id': self.will_id,
                'recipient_id': self.recipient_id,
                'sent_at': self.sent_at.isoformat() if self.sent_at else None,
                'status': self.status
            }
    
    return DispatchLog
