from flask import Blueprint, jsonify, request
from datetime import datetime
import logging

# DispatchLog 라우트 블루프린트 생성
dispatchlog_bp = Blueprint('dispatchlog', __name__, url_prefix='/api/dispatch-logs')

# 로거 설정
logger = logging.getLogger(__name__)

def init_dispatchlog_routes(db, DispatchLog, Recipient=None):
    """DispatchLog 라우트를 초기화하고 모델을 주입"""
    
    # 1. GET /api/dispatch-logs - 모든 발송 로그 조회
    @dispatchlog_bp.route('', methods=['GET'])
    def get_all_dispatch_logs():
        try:
            logs = DispatchLog.query.all()
            logs_list = [log.to_dict() for log in logs]
            logger.info(f"✅ 모든 발송 로그 조회 성공: {len(logs_list)}개")
            return jsonify({
                'success': True,
                'data': logs_list,
                'count': len(logs_list)
            }), 200
        except Exception as e:
            logger.error(f"❌ 발송 로그 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 2. GET /api/dispatch-logs/will/<will_id> - 특정 유언장의 발송 로그들 조회 (수신자 정보 포함)
    @dispatchlog_bp.route('/will/<int:will_id>', methods=['GET'])
    def get_logs_by_will(will_id):
        try:
            if Recipient:
                # OUTER JOIN으로 recipient_id가 없는 로그도 포함
                logs_with_recipients = db.session.query(DispatchLog, Recipient)\
                    .outerjoin(Recipient, DispatchLog.recipient_id == Recipient.id)\
                    .filter(DispatchLog.will_id == will_id)\
                    .all()

                logs_list = []
                for log, recipient in logs_with_recipients:
                    log_dict = log.to_dict()
                    if recipient:
                        log_dict['recipient_name'] = recipient.recipient_name
                        log_dict['recipient_email'] = recipient.recipient_email
                    else:
                        log_dict['recipient_name'] = None
                        log_dict['recipient_email'] = None
                    log_dict['created_at'] = log.sent_at.isoformat() if log.sent_at else None
                    logs_list.append(log_dict)
            else:
                # Recipient 모델이 없는 경우 기본 조회
                logs = DispatchLog.query.filter_by(will_id=will_id).all()
                logs_list = [log.to_dict() for log in logs]
            
            logger.info(f"✅ 유언장 ID {will_id}의 발송 로그 조회 성공: {len(logs_list)}개")
            return jsonify({
                'success': True,
                'data': logs_list,
                'count': len(logs_list)
            }), 200
        except Exception as e:
            logger.error(f"❌ 유언장 ID {will_id} 발송 로그 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 3. GET /api/dispatch-logs/recipient/<recipient_id> - 특정 수신자의 발송 로그들 조회
    @dispatchlog_bp.route('/recipient/<int:recipient_id>', methods=['GET'])
    def get_logs_by_recipient(recipient_id):
        try:
            logs = DispatchLog.query.filter_by(recipient_id=recipient_id).all()
            logs_list = [log.to_dict() for log in logs]
            logger.info(f"✅ 수신자 ID {recipient_id}의 발송 로그 조회 성공: {len(logs_list)}개")
            return jsonify({
                'success': True,
                'data': logs_list,
                'count': len(logs_list)
            }), 200
        except Exception as e:
            logger.error(f"❌ 수신자 ID {recipient_id} 발송 로그 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 4. GET /api/dispatch-logs/<id> - 특정 발송 로그 조회
    @dispatchlog_bp.route('/<int:log_id>', methods=['GET'])
    def get_dispatch_log(log_id):
        try:
            log = DispatchLog.query.get(log_id)
            if not log:
                logger.warning(f"⚠️ 발송 로그 ID {log_id} 찾을 수 없음")
                return jsonify({
                    'success': False,
                    'error': 'Dispatch log not found'
                }), 404
            
            logger.info(f"✅ 발송 로그 ID {log_id} 조회 성공")
            return jsonify({
                'success': True,
                'data': log.to_dict()
            }), 200
        except Exception as e:
            logger.error(f"❌ 발송 로그 ID {log_id} 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 5. POST /api/dispatch-logs - 신규 발송 로그 생성
    @dispatchlog_bp.route('', methods=['POST'])
    def create_dispatch_log():
        try:
            data = request.get_json()
            
            # 필수 데이터 검증
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            if not data.get('will_id') or not data.get('recipient_id'):
                return jsonify({
                    'success': False,
                    'error': 'will_id and recipient_id are required'
                }), 400
            
            # status 유효성 검증
            valid_statuses = ['pending', 'sent', 'failed']
            status = data.get('status', 'pending')
            if status not in valid_statuses:
                return jsonify({
                    'success': False,
                    'error': f'status must be one of: {", ".join(valid_statuses)}'
                }), 400
            
            # sent_at 처리
            sent_at = None
            if data.get('sent_at'):
                try:
                    sent_at = datetime.fromisoformat(data['sent_at'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({
                        'success': False,
                        'error': 'Invalid sent_at format. Use ISO format'
                    }), 400
            
            # 새 발송 로그 생성
            new_log = DispatchLog(
                will_id=data.get('will_id'),
                recipient_id=data.get('recipient_id'),
                sent_at=sent_at,
                status=status
            )
            
            db.session.add(new_log)
            db.session.commit()
            
            logger.info(f"✅ 신규 발송 로그 생성 성공: ID {new_log.id}")
            return jsonify({
                'success': True,
                'data': new_log.to_dict(),
                'message': 'Dispatch log created successfully'
            }), 201
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 발송 로그 생성 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 6. PUT /api/dispatch-logs/<id> - 발송 로그 정보 수정
    @dispatchlog_bp.route('/<int:log_id>', methods=['PUT'])
    def update_dispatch_log(log_id):
        try:
            log = DispatchLog.query.get(log_id)
            if not log:
                return jsonify({
                    'success': False,
                    'error': 'Dispatch log not found'
                }), 404
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            # 데이터 업데이트
            if 'will_id' in data:
                log.will_id = data['will_id']
            if 'recipient_id' in data:
                log.recipient_id = data['recipient_id']
            if 'sent_at' in data:
                if data['sent_at']:
                    try:
                        log.sent_at = datetime.fromisoformat(data['sent_at'].replace('Z', '+00:00'))
                    except ValueError:
                        return jsonify({
                            'success': False,
                            'error': 'Invalid sent_at format. Use ISO format'
                        }), 400
                else:
                    log.sent_at = None
            if 'status' in data:
                valid_statuses = ['pending', 'sent', 'failed']
                if data['status'] not in valid_statuses:
                    return jsonify({
                        'success': False,
                        'error': f'status must be one of: {", ".join(valid_statuses)}'
                    }), 400
                log.status = data['status']
            
            db.session.commit()
            
            logger.info(f"✅ 발송 로그 ID {log_id} 업데이트 성공")
            return jsonify({
                'success': True,
                'data': log.to_dict(),
                'message': 'Dispatch log updated successfully'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 발송 로그 ID {log_id} 업데이트 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # 7. DELETE /api/dispatch-logs/<id> - 발송 로그 삭제
    @dispatchlog_bp.route('/<int:log_id>', methods=['DELETE'])
    def delete_dispatch_log(log_id):
        try:
            log = DispatchLog.query.get(log_id)
            if not log:
                return jsonify({
                    'success': False,
                    'error': 'Dispatch log not found'
                }), 404
            
            db.session.delete(log)
            db.session.commit()
            
            logger.info(f"✅ 발송 로그 ID {log_id} 삭제 성공")
            return jsonify({
                'success': True,
                'message': f'Dispatch log ID {log_id} deleted successfully'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 발송 로그 ID {log_id} 삭제 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    return dispatchlog_bp