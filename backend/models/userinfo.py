def create_userinfo_model(db):
    """UserInfo 모델을 생성하는 팩토리 함수"""
    
    class UserInfo(db.Model):
        __tablename__ = 'UserInfo'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.String(50), unique=True, nullable=False)  # 새로운 사용자 ID 필드
        email = db.Column(db.String(255), nullable=True)  # lowercase to match schema
        lastname = db.Column(db.String(100), nullable=True)  # lowercase to match schema
        firstname = db.Column(db.String(100), nullable=True)  # lowercase to match schema
        grade = db.Column(db.String(3), nullable=True)  # lowercase to match schema
        password_hash = db.Column(db.String(255), nullable=True)  # 비밀번호 해시
        DOB = db.Column(db.Date, nullable=True)
        created_at = db.Column(db.DateTime, server_default=db.func.now())
        
        def to_dict(self):
            return {
                'id': self.id,
                'user_id': self.user_id,  # user_id 추가
                'lastname': self.lastname,
                'firstname': self.firstname,
                'email': self.email,
                'grade': self.grade,
                'DOB': self.DOB.isoformat() if self.DOB else None,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }
    
    return UserInfo
