def create_userinfo_model(db):
    """UserInfo 모델을 생성하는 팩토리 함수"""
    
    class UserInfo(db.Model):
        __tablename__ = 'UserInfo'
        id = db.Column(db.Integer, primary_key=True)
        LastName = db.Column(db.Text, nullable=True)
        FirstName = db.Column(db.Text, nullable=True)
        Email = db.Column(db.Text, nullable=True)
        Grade = db.Column(db.Text, nullable=True)
        DOB = db.Column(db.Date, nullable=True)
        created_at = db.Column(db.DateTime, server_default=db.func.now())
        
        def to_dict(self):
            return {
                'id': self.id,
                'LastName': self.LastName,
                'FirstName': self.FirstName,
                'Email': self.Email,
                'Grade': self.Grade,
                'DOB': self.DOB.isoformat() if self.DOB else None,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }
    
    return UserInfo
