from flask import Blueprint, jsonify, request
from datetime import datetime
import logging

# Triggers 라우트 블루프린트 생성
triggers_bp = Blueprint('triggers', __name__, url_prefix='/api/triggers')

# 로거 설정
logger = logging.getLogger(__name__)

def init_triggers_routes(db, Trigger):
    """Triggers 라우트를 초기화하고 모델을 주입"""
    
    # 1. GET /api/triggers - 모든 트리거 조회
    @triggers_bp.route('', methods=['GET'])
    def get_all_triggers():
        try:
            triggers = Trigger.query.all()
            triggers_list = [trigger.to_dict() for trigger in triggers]
            logger.info(f"✅ 모든 트리거 조회 성공: {len(triggers_list)}개")
            return jsonify({
                'success': True,
                'data': triggers_list,
                'count': len(triggers_list)
            }), 200
        except Exception as e:
            logger.error(f"❌ 트리거 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 2. GET /api/triggers/user/<user_id> - 특정 사용자의 트리거들 조회
    @triggers_bp.route('/user/<user_id>', methods=['GET'])
    def get_triggers_by_user(user_id):
        try:
            triggers = Trigger.query.filter_by(user_id=user_id).order_by(Trigger.trigger_date.desc()).all()
            triggers_list = [trigger.to_dict() for trigger in triggers]
            logger.info(f"✅ 사용자 ID {user_id}의 트리거 조회 성공: {len(triggers_list)}개")
            return jsonify({
                'success': True,
                'data': triggers_list,
                'count': len(triggers_list)
            }), 200
        except Exception as e:
            logger.error(f"❌ 사용자 ID {user_id} 트리거 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 2-1. GET /api/triggers/user/<user_id>/pending - 특정 사용자의 대기중인 트리거 조회
    @triggers_bp.route('/user/<user_id>/pending', methods=['GET'])
    def get_pending_trigger_by_user(user_id):
        try:
            # 대기중인 트리거만 조회 (하나만 허용)
            pending_trigger = Trigger.query.filter_by(user_id=user_id, status='pending').first()
            
            if pending_trigger:
                logger.info(f"✅ 사용자 ID {user_id}의 대기중인 트리거 조회 성공")
                return jsonify({
                    'success': True,
                    'data': pending_trigger.to_dict()
                }), 200
            else:
                logger.info(f"ℹ️ 사용자 ID {user_id}의 대기중인 트리거 없음")
                return jsonify({
                    'success': True,
                    'data': None
                }), 200
        except Exception as e:
            logger.error(f"❌ 사용자 ID {user_id} 대기중인 트리거 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 3. GET /api/triggers/<id> - 특정 트리거 조회
    @triggers_bp.route('/<int:trigger_id>', methods=['GET'])
    def get_trigger(trigger_id):
        try:
            trigger = Trigger.query.get(trigger_id)
            if not trigger:
                logger.warning(f"⚠️ 트리거 ID {trigger_id} 찾을 수 없음")
                return jsonify({
                    'success': False,
                    'error': 'Trigger not found'
                }), 404
            
            logger.info(f"✅ 트리거 ID {trigger_id} 조회 성공")
            return jsonify({
                'success': True,
                'data': trigger.to_dict()
            }), 200
        except Exception as e:
            logger.error(f"❌ 트리거 ID {trigger_id} 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 4. POST /api/triggers - 신규 트리거 생성
    @triggers_bp.route('', methods=['POST'])
    def create_trigger():
        try:
            data = request.get_json()
            
            # 디버깅: 받은 데이터 로그
            logger.info(f"🔍 DEBUG: 받은 트리거 생성 데이터: {data}")
            logger.info(f"🔍 DEBUG: 데이터 타입: {type(data)}")
            if data:
                for key, value in data.items():
                    logger.info(f"🔍 DEBUG: {key} = {value} (type: {type(value)})")
            
            # 필수 데이터 검증
            if not data:
                logger.error("❌ No data provided")
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            if not data.get('user_id') or not data.get('trigger_type'):
                return jsonify({
                    'success': False,
                    'error': 'user_id and trigger_type are required'
                }), 400
            
            # trigger_type 유효성 검증
            valid_types = ['inactivity', 'date', 'manual']
            if data.get('trigger_type') not in valid_types:
                return jsonify({
                    'success': False,
                    'error': f'trigger_type must be one of: {", ".join(valid_types)}'
                }), 400
            
            # last_checked 처리
            last_checked = None
            if data.get('last_checked'):
                try:
                    last_checked = datetime.fromisoformat(data['last_checked'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({
                        'success': False,
                        'error': 'Invalid last_checked format. Use ISO format'
                    }), 400
            
            # trigger_date 처리
            trigger_date = None
            if data.get('trigger_date'):
                try:
                    trigger_date = datetime.strptime(data['trigger_date'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({
                        'success': False,
                        'error': 'Invalid trigger_date format. Use YYYY-MM-DD'
                    }), 400

            # 기존 pending 트리거가 있는지 확인 (하나만 허용)
            existing_pending = Trigger.query.filter_by(user_id=data.get('user_id'), status='pending').first()
            if existing_pending:
                return jsonify({
                    'success': False,
                    'error': 'User already has a pending trigger. Only one pending trigger allowed per user.'
                }), 400

            # 새 트리거 생성
            new_trigger = Trigger(
                user_id=data.get('user_id'),
                trigger_type=data.get('trigger_type'),
                trigger_date=trigger_date,
                trigger_value=data.get('trigger_value'),
                description=data.get('description'),
                last_checked=last_checked,
                is_triggered=data.get('is_triggered', False),
                status=data.get('status', 'pending')
            )
            
            db.session.add(new_trigger)
            db.session.commit()
            
            logger.info(f"✅ 신규 트리거 생성 성공: ID {new_trigger.id}")
            return jsonify({
                'success': True,
                'data': new_trigger.to_dict(),
                'message': 'Trigger created successfully'
            }), 201
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 트리거 생성 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 5. PUT /api/triggers/<id> - 트리거 정보 수정
    @triggers_bp.route('/<int:trigger_id>', methods=['PUT'])
    def update_trigger(trigger_id):
        try:
            trigger = Trigger.query.get(trigger_id)
            if not trigger:
                return jsonify({
                    'success': False,
                    'error': 'Trigger not found'
                }), 404
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            # 데이터 업데이트
            if 'user_id' in data:
                trigger.user_id = data['user_id']
            if 'trigger_type' in data:
                valid_types = ['inactivity', 'date', 'manual']
                if data['trigger_type'] not in valid_types:
                    return jsonify({
                        'success': False,
                        'error': f'trigger_type must be one of: {", ".join(valid_types)}'
                    }), 400
                trigger.trigger_type = data['trigger_type']
            if 'trigger_value' in data:
                trigger.trigger_value = data['trigger_value']
            if 'last_checked' in data:
                if data['last_checked']:
                    try:
                        trigger.last_checked = datetime.fromisoformat(data['last_checked'].replace('Z', '+00:00'))
                    except ValueError:
                        return jsonify({
                            'success': False,
                            'error': 'Invalid last_checked format. Use ISO format'
                        }), 400
                else:
                    trigger.last_checked = None
            if 'is_triggered' in data:
                trigger.is_triggered = data['is_triggered']
            
            db.session.commit()
            
            logger.info(f"✅ 트리거 ID {trigger_id} 업데이트 성공")
            return jsonify({
                'success': True,
                'data': trigger.to_dict(),
                'message': 'Trigger updated successfully'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 트리거 ID {trigger_id} 업데이트 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 6. DELETE /api/triggers/<id> - 트리거 삭제
    @triggers_bp.route('/<int:trigger_id>', methods=['DELETE'])
    def delete_trigger(trigger_id):
        try:
            trigger = Trigger.query.get(trigger_id)
            if not trigger:
                return jsonify({
                    'success': False,
                    'error': 'Trigger not found'
                }), 404
            
            db.session.delete(trigger)
            db.session.commit()
            
            logger.info(f"✅ 트리거 ID {trigger_id} 삭제 성공")
            return jsonify({
                'success': True,
                'message': f'Trigger ID {trigger_id} deleted successfully'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 트리거 ID {trigger_id} 삭제 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    return triggers_bp