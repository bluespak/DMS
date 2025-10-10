from datetime import datetime

def create_will_model(db):
    """Will 모델을 생성하는 팩토리 함수"""
    
    class Will(db.Model):
        __tablename__ = 'wills'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('UserInfo.id'), nullable=False)
        subject = db.Column(db.String(255))
        body = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        lastmodified_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def to_dict(self):
            return {
                'id': self.id,
                'user_id': self.user_id,
                'subject': self.subject,
                'body': self.body,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'lastmodified_at': self.lastmodified_at.isoformat() if self.lastmodified_at else None
            }
    
    return Will
