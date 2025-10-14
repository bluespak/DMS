"""
Authentication Routes
사용자 인증을 처리하는 API 엔드포인트
"""
from flask import Blueprint, request, jsonify, session
import hashlib
import os
from datetime import datetime, timedelta
import jwt
from functools import wraps

def init_auth_routes(db, UserInfo):
    """인증 라우트 초기화"""
    auth_bp = Blueprint('auth', __name__)
    
    # JWT 시크릿 키 (환경변수에서 가져오거나 기본값 사용)
    JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-this-in-production')
    JWT_EXPIRES_HOURS = int(os.getenv('JWT_EXPIRES_HOURS', '24'))
    
    def hash_password(password):
        """비밀번호 해싱"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_token(user_id):
        """JWT 토큰 생성"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRES_HOURS),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    
    def verify_token(token):
        """JWT 토큰 검증"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def require_auth(f):
        """인증 필수 데코레이터"""
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'success': False, 'message': '토큰이 필요합니다'}), 401
            
            if token.startswith('Bearer '):
                token = token[7:]
            
            user_id = verify_token(token)
            if not user_id:
                return jsonify({'success': False, 'message': '유효하지 않은 토큰입니다'}), 401
            
            # 사용자 존재 확인
            user = db.session.query(UserInfo).filter_by(user_id=user_id).first()
            if not user:
                return jsonify({'success': False, 'message': '사용자를 찾을 수 없습니다'}), 401
            
            # 현재 사용자 정보를 함수에 전달
            return f(user, *args, **kwargs)
        return decorated
    
    @auth_bp.route('/api/auth/login', methods=['POST'])
    def login():
        """사용자 로그인"""
        try:
            data = request.get_json()
            
            if not data or not data.get('user_id') or not data.get('password'):
                return jsonify({
                    'success': False,
                    'message': '사용자 ID와 비밀번호를 입력해주세요'
                }), 400
            
            user_id = data['user_id'].strip()
            password = data['password']
            
            # 사용자 조회
            user = db.session.query(UserInfo).filter_by(user_id=user_id).first()
            
            if not user:
                return jsonify({
                    'success': False,
                    'message': '존재하지 않는 사용자입니다'
                }), 401
            
            # 비밀번호 검증
            hashed_password = hash_password(password)
            if user.password_hash != hashed_password:
                return jsonify({
                    'success': False,
                    'message': '비밀번호가 일치하지 않습니다'
                }), 401
            
            # JWT 토큰 생성
            token = generate_token(user_id)
            
            # 성공 응답
            return jsonify({
                'success': True,
                'message': '로그인 성공',
                'token': token,
                'user': {
                    'user_id': user.user_id,
                    'email': user.Email,
                    'firstname': user.FirstName,
                    'lastname': user.LastName,
                    'grade': user.Grade
                }
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'로그인 중 오류가 발생했습니다: {str(e)}'
            }), 500
    
    @auth_bp.route('/api/auth/register', methods=['POST'])
    def register():
        """사용자 회원가입"""
        try:
            data = request.get_json()
            
            required_fields = ['user_id', 'password', 'email', 'firstname', 'lastname']
            for field in required_fields:
                if not data or not data.get(field):
                    return jsonify({
                        'success': False,
                        'message': f'{field}는 필수 입력 항목입니다'
                    }), 400
            
            user_id = data['user_id'].strip()
            password = data['password']
            email = data['email'].strip()
            firstname = data['firstname'].strip()
            lastname = data['lastname'].strip()
            grade = data.get('grade', 'Standard')
            dob = data.get('DOB')
            
            # 중복 사용자 확인
            existing_user = db.session.query(UserInfo).filter(
                (UserInfo.user_id == user_id) | (UserInfo.Email == email)
            ).first()
            
            if existing_user:
                if existing_user.user_id == user_id:
                    return jsonify({
                        'success': False,
                        'message': '이미 존재하는 사용자 ID입니다'
                    }), 409
                else:
                    return jsonify({
                        'success': False,
                        'message': '이미 등록된 이메일입니다'
                    }), 409
            
            # 비밀번호 해싱
            hashed_password = hash_password(password)
            
            # 새 사용자 생성
            new_user = UserInfo(
                user_id=user_id,
                password_hash=hashed_password,
                Email=email,
                FirstName=firstname,
                LastName=lastname,
                Grade=grade,
                DOB=datetime.strptime(dob, '%Y-%m-%d').date() if dob else None
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            # JWT 토큰 생성
            token = generate_token(user_id)
            
            return jsonify({
                'success': True,
                'message': '회원가입 성공',
                'token': token,
                'user': {
                    'user_id': user_id,
                    'email': email,
                    'firstname': firstname,
                    'lastname': lastname,
                    'grade': grade
                }
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'회원가입 중 오류가 발생했습니다: {str(e)}'
            }), 500
    
    @auth_bp.route('/api/auth/verify', methods=['GET'])
    @require_auth
    def verify_token_endpoint(current_user):
        """토큰 검증"""
        return jsonify({
            'success': True,
            'message': '유효한 토큰입니다',
            'user': {
                'user_id': current_user.user_id,
                'email': current_user.Email,
                'firstname': current_user.FirstName,
                'lastname': current_user.LastName,
                'grade': current_user.grade
            }
        })
    
    @auth_bp.route('/api/auth/logout', methods=['POST'])
    def logout():
        """로그아웃 (클라이언트에서 토큰 삭제)"""
        return jsonify({
            'success': True,
            'message': '로그아웃 되었습니다'
        })
    
    return auth_bp