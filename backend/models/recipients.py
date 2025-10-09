def create_recipient_model(db):
    """Recipient 모델을 생성하는 팩토리 함수"""
    
    class Recipient(db.Model):
        __tablename__ = 'recipients'
        id = db.Column(db.Integer, primary_key=True)
        will_id = db.Column(db.Integer, db.ForeignKey('wills.id'), nullable=False)
        recipient_email = db.Column(db.String(255), nullable=False)
        recipient_name = db.Column(db.String(100))
        relatedCode = db.Column(db.String(1))  # 'A', 'B', 'C' 등으로 구분
        
        def to_dict(self):
            return {
                'id': self.id,
                'will_id': self.will_id,
                'recipient_email': self.recipient_email,
                'recipient_name': self.recipient_name,
                'relatedCode': self.relatedCode
            }
    
    return Recipient

