def create_trigger_model(db):
    """Trigger 모델을 생성하는 팩토리 함수"""
    
    class Trigger(db.Model):
        __tablename__ = 'triggers'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('UserInfo.id'), nullable=False)
        trigger_type = db.Column(db.Enum('inactivity', 'date', 'manual'), nullable=False)
        trigger_value = db.Column(db.String(255))
        last_checked = db.Column(db.DateTime)
        is_triggered = db.Column(db.Boolean, default=False)
        
        def to_dict(self):
            return {
                'id': self.id,
                'user_id': self.user_id,
                'trigger_type': self.trigger_type,
                'trigger_value': self.trigger_value,
                'last_checked': self.last_checked.isoformat() if self.last_checked else None,
                'is_triggered': self.is_triggered
            }
    
    return Trigger
