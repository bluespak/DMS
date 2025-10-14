def create_trigger_model(db):
    """Trigger 모델을 생성하는 팩토리 함수"""
    
    class Trigger(db.Model):
        __tablename__ = 'triggers'
        __table_args__ = {'extend_existing': True}
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.String(50), db.ForeignKey('UserInfo.user_id'), nullable=False)  # user_id 필드 참조로 변경
        trigger_type = db.Column(db.Enum('inactivity', 'date', 'manual'), nullable=False)
        trigger_date = db.Column(db.Date)  # 새로 추가된 필드
        trigger_value = db.Column(db.String(255))
        description = db.Column(db.Text)  # 새로 추가된 필드
        last_checked = db.Column(db.DateTime)
        is_triggered = db.Column(db.Boolean, default=False)
        status = db.Column(db.Enum('pending', 'completed', 'failed'), default='pending')  # 새로 추가된 필드
        
        def to_dict(self):
            return {
                'trigger_id': self.id,  # UI에서 사용하는 필드명에 맞춤
                'user_id': self.user_id,
                'trigger_type': self.trigger_type,
                'trigger_date': self.trigger_date.isoformat() if self.trigger_date else None,
                'trigger_value': self.trigger_value,
                'description': self.description,
                'last_checked': self.last_checked.isoformat() if self.last_checked else None,
                'is_triggered': self.is_triggered,
                'status': self.status
            }
    
    return Trigger
