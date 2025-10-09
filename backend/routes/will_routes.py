from flask import Blueprint, jsonify, request
from datetime import datetime
import logging

# Will 라우트 블루프린트 생성
will_bp = Blueprint('will', __name__, url_prefix='/api/wills')

# 로거 설정
logger = logging.getLogger(__name__)

def init_will_routes(db, Will):
    """Will 라우트를 초기화하고 모델을 주입"""
    
    # 1. GET /api/wills - 모든 유언장 조회
    @will_bp.route('', methods=['GET'])
    def get_all_wills():
        try:
            wills = Will.query.all()
            wills_list = [will.to_dict() for will in wills]
            logger.info(f"✅ 모든 유언장 조회 성공: {len(wills_list)}개")
            return jsonify({
                'success': True,
                'data': wills_list,
                'count': len(wills_list)
            }), 200
        except Exception as e:
            logger.error(f"❌ 유언장 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 2. GET /api/wills/<id> - 특정 유언장 조회
    @will_bp.route('/<int:will_id>', methods=['GET'])
    def get_will(will_id):
        try:
            will = Will.query.get(will_id)
            if not will:
                logger.warning(f"⚠️ 유언장 ID {will_id} 찾을 수 없음")
                return jsonify({
                    'success': False,
                    'error': 'Will not found'
                }), 404
            
            logger.info(f"✅ 유언장 ID {will_id} 조회 성공")
            return jsonify({
                'success': True,
                'data': will.to_dict()
            }), 200
        except Exception as e:
            logger.error(f"❌ 유언장 ID {will_id} 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 3. POST /api/wills - 신규 유언장 생성
    @will_bp.route('', methods=['POST'])
    def create_will():
        try:
            data = request.get_json()
            
            # 필수 데이터 검증
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            if not data.get('subject') or not data.get('body'):
                return jsonify({
                    'success': False,
                    'error': 'Subject and body are required'
                }), 400
            
            # 새 유언장 생성
            new_will = Will(
                subject=data.get('subject'),
                body=data.get('body')
            )
            
            db.session.add(new_will)
            db.session.commit()
            
            logger.info(f"✅ 신규 유언장 생성 성공: ID {new_will.id}")
            return jsonify({
                'success': True,
                'data': new_will.to_dict(),
                'message': 'Will created successfully'
            }), 201
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 유언장 생성 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 4. PUT /api/wills/<id> - 유언장 정보 수정
    @will_bp.route('/<int:will_id>', methods=['PUT'])
    def update_will(will_id):
        try:
            will = Will.query.get(will_id)
            if not will:
                return jsonify({
                    'success': False,
                    'error': 'Will not found'
                }), 404
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            # 데이터 업데이트
            if 'subject' in data:
                will.subject = data['subject']
            if 'body' in data:
                will.body = data['body']
            
            db.session.commit()
            
            logger.info(f"✅ 유언장 ID {will_id} 업데이트 성공")
            return jsonify({
                'success': True,
                'data': will.to_dict(),
                'message': 'Will updated successfully'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 유언장 ID {will_id} 업데이트 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 5. DELETE /api/wills/<id> - 유언장 삭제
    @will_bp.route('/<int:will_id>', methods=['DELETE'])
    def delete_will(will_id):
        try:
            will = Will.query.get(will_id)
            if not will:
                return jsonify({
                    'success': False,
                    'error': 'Will not found'
                }), 404
            
            db.session.delete(will)
            db.session.commit()
            
            logger.info(f"✅ 유언장 ID {will_id} 삭제 성공")
            return jsonify({
                'success': True,
                'message': f'Will ID {will_id} deleted successfully'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 유언장 ID {will_id} 삭제 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    return will_bp