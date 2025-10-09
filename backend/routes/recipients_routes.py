from flask import Blueprint, jsonify, request
import logging

# Recipients 라우트 블루프린트 생성
recipients_bp = Blueprint('recipients', __name__, url_prefix='/api/recipients')

# 로거 설정
logger = logging.getLogger(__name__)

def init_recipients_routes(db, Recipient):
    """Recipients 라우트를 초기화하고 모델을 주입"""
    
    # 1. GET /api/recipients - 모든 수신자 조회
    @recipients_bp.route('', methods=['GET'])
    def get_all_recipients():
        try:
            recipients = Recipient.query.all()
            recipients_list = [recipient.to_dict() for recipient in recipients]
            logger.info(f"✅ 모든 수신자 조회 성공: {len(recipients_list)}명")
            return jsonify({
                'success': True,
                'data': recipients_list,
                'count': len(recipients_list)
            }), 200
        except Exception as e:
            logger.error(f"❌ 수신자 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 2. GET /api/recipients/will/<will_id> - 특정 유언장의 수신자들 조회
    @recipients_bp.route('/will/<int:will_id>', methods=['GET'])
    def get_recipients_by_will(will_id):
        try:
            recipients = Recipient.query.filter_by(will_id=will_id).all()
            recipients_list = [recipient.to_dict() for recipient in recipients]
            logger.info(f"✅ 유언장 ID {will_id}의 수신자 조회 성공: {len(recipients_list)}명")
            return jsonify({
                'success': True,
                'data': recipients_list,
                'count': len(recipients_list)
            }), 200
        except Exception as e:
            logger.error(f"❌ 유언장 ID {will_id} 수신자 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 3. GET /api/recipients/<id> - 특정 수신자 조회
    @recipients_bp.route('/<int:recipient_id>', methods=['GET'])
    def get_recipient(recipient_id):
        try:
            recipient = Recipient.query.get(recipient_id)
            if not recipient:
                logger.warning(f"⚠️ 수신자 ID {recipient_id} 찾을 수 없음")
                return jsonify({
                    'success': False,
                    'error': 'Recipient not found'
                }), 404
            
            logger.info(f"✅ 수신자 ID {recipient_id} 조회 성공")
            return jsonify({
                'success': True,
                'data': recipient.to_dict()
            }), 200
        except Exception as e:
            logger.error(f"❌ 수신자 ID {recipient_id} 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 4. POST /api/recipients - 신규 수신자 생성
    @recipients_bp.route('', methods=['POST'])
    def create_recipient():
        try:
            data = request.get_json()
            
            # 필수 데이터 검증
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            if not data.get('will_id') or not data.get('recipient_email'):
                return jsonify({
                    'success': False,
                    'error': 'will_id and recipient_email are required'
                }), 400
            
            # 새 수신자 생성
            new_recipient = Recipient(
                will_id=data.get('will_id'),
                recipient_email=data.get('recipient_email'),
                recipient_name=data.get('recipient_name'),
                relatedCode=data.get('relatedCode')
            )
            
            db.session.add(new_recipient)
            db.session.commit()
            
            logger.info(f"✅ 신규 수신자 생성 성공: ID {new_recipient.id}")
            return jsonify({
                'success': True,
                'data': new_recipient.to_dict(),
                'message': 'Recipient created successfully'
            }), 201
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 수신자 생성 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 5. PUT /api/recipients/<id> - 수신자 정보 수정
    @recipients_bp.route('/<int:recipient_id>', methods=['PUT'])
    def update_recipient(recipient_id):
        try:
            recipient = Recipient.query.get(recipient_id)
            if not recipient:
                return jsonify({
                    'success': False,
                    'error': 'Recipient not found'
                }), 404
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            # 데이터 업데이트
            if 'will_id' in data:
                recipient.will_id = data['will_id']
            if 'recipient_email' in data:
                recipient.recipient_email = data['recipient_email']
            if 'recipient_name' in data:
                recipient.recipient_name = data['recipient_name']
            if 'relatedCode' in data:
                recipient.relatedCode = data['relatedCode']
            
            db.session.commit()
            
            logger.info(f"✅ 수신자 ID {recipient_id} 업데이트 성공")
            return jsonify({
                'success': True,
                'data': recipient.to_dict(),
                'message': 'Recipient updated successfully'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 수신자 ID {recipient_id} 업데이트 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 6. DELETE /api/recipients/<id> - 수신자 삭제
    @recipients_bp.route('/<int:recipient_id>', methods=['DELETE'])
    def delete_recipient(recipient_id):
        try:
            recipient = Recipient.query.get(recipient_id)
            if not recipient:
                return jsonify({
                    'success': False,
                    'error': 'Recipient not found'
                }), 404
            
            db.session.delete(recipient)
            db.session.commit()
            
            logger.info(f"✅ 수신자 ID {recipient_id} 삭제 성공")
            return jsonify({
                'success': True,
                'message': f'Recipient ID {recipient_id} deleted successfully'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 수신자 ID {recipient_id} 삭제 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    return recipients_bp