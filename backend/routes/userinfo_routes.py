from flask import Blueprint, jsonify, request
from datetime import datetime
import logging

# UserInfo 라우트 블루프린트 생성
userinfo_bp = Blueprint('userinfo', __name__, url_prefix='/api/users')

# 로거 설정
logger = logging.getLogger(__name__)

def init_userinfo_routes(db, UserInfo):
    """UserInfo 라우트를 초기화하고 모델을 주입"""
    
    # 1. GET /api/users - 모든 사용자 조회
    @userinfo_bp.route('', methods=['GET'])
    def get_all_users():
        try:
            users = UserInfo.query.all()
            users_list = [user.to_dict() for user in users]
            logger.info(f"✅ 모든 사용자 조회 성공: {len(users_list)}명")
            return jsonify({
                'success': True,
                'data': users_list,
                'count': len(users_list)
            }), 200
        except Exception as e:
            logger.error(f"❌ 사용자 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 2. GET /api/users/<user_id> - 특정 사용자 조회 (user_id 문자열 기반)
    @userinfo_bp.route('/<string:user_id>', methods=['GET'])
    def get_user(user_id):
        try:
            user = UserInfo.query.filter_by(user_id=user_id).first()
            if not user:
                logger.warning(f"⚠️ 사용자 ID {user_id} 찾을 수 없음")
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
            logger.info(f"✅ 사용자 ID {user_id} 조회 성공")
            return jsonify({
                'success': True,
                'data': user.to_dict()
            }), 200
        except Exception as e:
            logger.error(f"❌ 사용자 ID {user_id} 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 3. POST /api/users - 신규 사용자 생성
    @userinfo_bp.route('', methods=['POST'])
    def create_user():
        try:
            data = request.get_json()
            
            # 필수 데이터 검증
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            # DOB 문자열을 date 객체로 변환
            dob = None
            if data.get('DOB'):
                try:
                    dob = datetime.strptime(data['DOB'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({
                        'success': False,
                        'error': 'Invalid date format. Use YYYY-MM-DD'
                    }), 400
            
            # 새 사용자 생성
            new_user = UserInfo(
                user_id=data.get('user_id'),
                lastname=data.get('lastname'),
                firstname=data.get('firstname'),
                email=data.get('email'),
                grade=data.get('grade'),
                DOB=dob
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            logger.info(f"✅ 신규 사용자 생성 성공: ID {new_user.id}")
            return jsonify({
                'success': True,
                'data': new_user.to_dict(),
                'message': 'User created successfully'
            }), 201
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 사용자 생성 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 4. PUT /api/users/<id> - 사용자 정보 수정
    @userinfo_bp.route('/<int:user_id>', methods=['PUT'])
    def update_user(user_id):
        try:
            user = UserInfo.query.get(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            # 데이터 업데이트
            if 'lastname' in data:
                user.lastname = data['lastname']
            if 'firstname' in data:
                user.firstname = data['firstname']
            if 'email' in data:
                user.email = data['email']
            if 'grade' in data:
                user.grade = data['grade']
            if 'DOB' in data:
                if data['DOB']:
                    try:
                        user.DOB = datetime.strptime(data['DOB'], '%Y-%m-%d').date()
                    except ValueError:
                        return jsonify({
                            'success': False,
                            'error': 'Invalid date format. Use YYYY-MM-DD'
                        }), 400
                else:
                    user.DOB = None
            
            db.session.commit()
            
            logger.info(f"✅ 사용자 ID {user_id} 업데이트 성공")
            return jsonify({
                'success': True,
                'data': user.to_dict(),
                'message': 'User updated successfully'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 사용자 ID {user_id} 업데이트 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 5. DELETE /api/users/<id> - 사용자 삭제
    @userinfo_bp.route('/<int:user_id>', methods=['DELETE'])
    def delete_user(user_id):
        try:
            user = UserInfo.query.get(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
            db.session.delete(user)
            db.session.commit()
            
            logger.info(f"✅ 사용자 ID {user_id} 삭제 성공")
            return jsonify({
                'success': True,
                'message': f'User ID {user_id} deleted successfully'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 사용자 ID {user_id} 삭제 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    return userinfo_bp