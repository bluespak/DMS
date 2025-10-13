import unittest
import sys
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 프로젝트 루트 경로를 Python path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestConfig:
    """테스트용 설정"""
    TESTING = True
    # 테스트 전용 MySQL 데이터베이스 사용 (운영 DB와 분리)
    # 실제 운영 환경과 동일한 MySQL 엔진으로 정확한 테스트 가능
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://dmsTestUser:dmstest2025!@localhost/dmsdb_test'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'

def _ensure_latest_schema(db):
    """최신 스키마로 테이블 재생성"""
    try:
        from sqlalchemy import inspect, text
        
        # 테이블 스키마 확인
        inspector = inspect(db.engine)
        
        # dispatch_log 테이블이 존재하고 구버전인지 확인
        if inspector.has_table('dispatch_log'):
            columns = [col['name'] for col in inspector.get_columns('dispatch_log')]
            
            # delivered_at, read_at 컬럼이 없으면 구버전
            if 'delivered_at' not in columns or 'read_at' not in columns:
                print("⚠️ 구버전 dispatch_log 테이블 발견, 재생성 중...")
                
                # 기존 테이블 삭제 후 재생성
                with db.engine.connect() as conn:
                    conn.execute(text('DROP TABLE IF EXISTS dispatch_log'))
                    conn.commit()
                
                # 최신 스키마로 테이블 재생성
                db.create_all()
                print("✅ dispatch_log 테이블이 최신 스키마로 재생성됨")
        
    except Exception as e:
        print(f"⚠️ 스키마 확인 실패: {e}")
        pass

def create_test_app():
    """테스트용 Flask 앱 생성"""
    import uuid
    
    app = Flask(__name__ + str(uuid.uuid4()))
    app.config.from_object(TestConfig)
    
    db = SQLAlchemy(app)
    
    # 모델 임포트 (실제 프로젝트 모델 사용)
    from models.userinfo import create_userinfo_model
    from models.will import create_will_model
    from models.recipients import create_recipient_model
    from models.trigger import create_trigger_model
    from models.dispatchlog import create_dispatchlog_model
    
    # 모델 생성
    UserInfo = create_userinfo_model(db)
    Will = create_will_model(db)
    Recipient = create_recipient_model(db)
    Trigger = create_trigger_model(db)
    DispatchLog = create_dispatchlog_model(db)
    
    # 테스트용 라우트 직접 생성 (Blueprint 재등록 문제 해결)
    from flask import Blueprint, jsonify, request
    
    # UserInfo 라우트
    userinfo_bp = Blueprint('userinfo_test_' + str(uuid.uuid4())[:8], __name__)
    
    @userinfo_bp.route('', methods=['GET'])
    def get_all_users():
        users = UserInfo.query.all()
        return jsonify([user.to_dict() for user in users])
    
    @userinfo_bp.route('/<int:user_id>', methods=['GET'])
    def get_user(user_id):
        user = UserInfo.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user.to_dict())
    
    @userinfo_bp.route('', methods=['POST'])
    def create_user():
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        try:
            from datetime import datetime
            dob = None
            if data.get('DOB'):
                dob = datetime.strptime(data['DOB'], '%Y-%m-%d').date()
            
            new_user = UserInfo(
                LastName=data.get('LastName'),
                FirstName=data.get('FirstName'),
                Email=data.get('Email'),
                Grade=data.get('Grade'),
                DOB=dob
            )
            
            db.session.add(new_user)
            db.session.commit()
            return jsonify(new_user.to_dict()), 201
        except ValueError as e:
            return jsonify({'error': 'Invalid date format'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @userinfo_bp.route('/<int:user_id>', methods=['PUT'])
    def update_user(user_id):
        user = UserInfo.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        try:
            if data.get('LastName'):
                user.LastName = data['LastName']
            if data.get('FirstName'):
                user.FirstName = data['FirstName']
            if data.get('Email'):
                user.Email = data['Email']
            if data.get('Grade'):
                user.Grade = data['Grade']
            if data.get('DOB'):
                from datetime import datetime
                user.DOB = datetime.strptime(data['DOB'], '%Y-%m-%d').date()
            
            db.session.commit()
            return jsonify(user.to_dict())
        except ValueError as e:
            return jsonify({'error': 'Invalid date format'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @userinfo_bp.route('/<int:user_id>', methods=['DELETE'])
    def delete_user(user_id):
        user = UserInfo.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})
    
    # Will 라우트
    will_bp = Blueprint('will_test_' + str(uuid.uuid4())[:8], __name__)
    
    @will_bp.route('', methods=['GET'])
    def get_all_wills():
        try:
            wills = Will.query.all()
            wills_list = [will.to_dict() for will in wills]
            return jsonify({
                'success': True,
                'data': wills_list,
                'count': len(wills_list)
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @will_bp.route('/<int:will_id>', methods=['GET'])
    def get_will(will_id):
        try:
            will = Will.query.get(will_id)
            if not will:
                return jsonify({
                    'success': False,
                    'error': 'Will not found'
                }), 404
            return jsonify({
                'success': True,
                'data': will.to_dict()
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @will_bp.route('', methods=['POST'])
    def create_will():
        try:
            data = request.get_json()
        except:
            data = None
            
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # 필수 필드 검증
        required_fields = ['user_id', 'subject', 'body']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        try:
            from datetime import datetime
            
            new_will = Will(
                user_id=data['user_id'],
                subject=data['subject'],
                body=data['body'],
                created_at=datetime.utcnow()
            )
            
            db.session.add(new_will)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': new_will.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @will_bp.route('/<int:will_id>', methods=['PUT'])
    def update_will(will_id):
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
        
        try:
            from datetime import datetime
            
            # 업데이트 가능한 필드들
            if 'subject' in data:
                will.subject = data['subject']
            if 'body' in data:
                will.body = data['body']
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': will.to_dict()
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @will_bp.route('/<int:will_id>', methods=['DELETE'])
    def delete_will(will_id):
        will = Will.query.get(will_id)
        if not will:
            return jsonify({
                'success': False,
                'error': 'Will not found'
            }), 404
        
        try:
            db.session.delete(will)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Will deleted successfully'
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # Recipients 라우트
    recipients_bp = Blueprint('recipients_test_' + str(uuid.uuid4())[:8], __name__)
    
    @recipients_bp.route('', methods=['GET'])
    def get_all_recipients():
        try:
            recipients = Recipient.query.all()
            recipients_list = [recipient.to_dict() for recipient in recipients]
            return jsonify({
                'success': True,
                'data': recipients_list,
                'count': len(recipients_list)
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @recipients_bp.route('/<int:recipient_id>', methods=['GET'])
    def get_recipient(recipient_id):
        try:
            recipient = Recipient.query.get(recipient_id)
            if not recipient:
                return jsonify({
                    'success': False,
                    'error': 'Recipient not found'
                }), 404
            return jsonify({
                'success': True,
                'data': recipient.to_dict()
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @recipients_bp.route('', methods=['POST'])
    def create_recipient():
        try:
            data = request.get_json()
        except:
            data = None
            
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # 필수 필드 검증
        required_fields = ['will_id', 'recipient_email']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        try:
            new_recipient = Recipient(
                will_id=data['will_id'],
                recipient_email=data['recipient_email'],
                recipient_name=data.get('recipient_name'),
                relatedCode=data.get('relatedCode')
            )
            
            db.session.add(new_recipient)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': new_recipient.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @recipients_bp.route('/<int:recipient_id>', methods=['PUT'])
    def update_recipient(recipient_id):
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
        
        try:
            # 업데이트 가능한 필드들
            if 'recipient_email' in data:
                recipient.recipient_email = data['recipient_email']
            if 'recipient_name' in data:
                recipient.recipient_name = data['recipient_name']
            if 'relatedCode' in data:
                recipient.relatedCode = data['relatedCode']
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': recipient.to_dict()
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @recipients_bp.route('/<int:recipient_id>', methods=['DELETE'])
    def delete_recipient(recipient_id):
        recipient = Recipient.query.get(recipient_id)
        if not recipient:
            return jsonify({
                'success': False,
                'error': 'Recipient not found'
            }), 404
        
        try:
            db.session.delete(recipient)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Recipient deleted successfully'
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @recipients_bp.route('/will/<int:will_id>', methods=['GET'])
    def get_recipients_by_will_id(will_id):
        try:
            recipients = Recipient.query.filter_by(will_id=will_id).all()
            recipients_list = [recipient.to_dict() for recipient in recipients]
            return jsonify({
                'success': True,
                'data': recipients_list,
                'count': len(recipients_list)
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # Triggers 라우트
    triggers_bp = Blueprint('triggers_test_' + str(uuid.uuid4())[:8], __name__)
    
    @triggers_bp.route('', methods=['GET'])
    def get_all_triggers():
        try:
            triggers = Trigger.query.all()
            triggers_list = [trigger.to_dict() for trigger in triggers]
            return jsonify({
                'success': True,
                'data': triggers_list,
                'count': len(triggers_list)
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @triggers_bp.route('/<int:trigger_id>', methods=['GET'])
    def get_trigger(trigger_id):
        try:
            trigger = Trigger.query.get(trigger_id)
            if not trigger:
                return jsonify({
                    'success': False,
                    'error': 'Trigger not found'
                }), 404
            return jsonify({
                'success': True,
                'data': trigger.to_dict()
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @triggers_bp.route('', methods=['POST'])
    def create_trigger():
        try:
            data = request.get_json()
        except:
            data = None
            
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # 필수 필드 검증
        required_fields = ['user_id', 'trigger_type']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # trigger_type 검증
        valid_types = ['inactivity', 'date', 'manual']
        if data['trigger_type'] not in valid_types:
            return jsonify({
                'success': False,
                'error': f'Invalid trigger type. Must be one of: {", ".join(valid_types)}'
            }), 400
        
        try:
            from datetime import datetime
            
            new_trigger = Trigger(
                user_id=data['user_id'],
                trigger_type=data['trigger_type'],
                trigger_value=data.get('trigger_value'),
                last_checked=datetime.utcnow() if data.get('last_checked') else None,
                is_triggered=data.get('is_triggered', False)
            )
            
            db.session.add(new_trigger)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': new_trigger.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @triggers_bp.route('/<int:trigger_id>', methods=['PUT'])
    def update_trigger(trigger_id):
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
        
        try:
            from datetime import datetime
            
            # 업데이트 가능한 필드들
            if 'trigger_type' in data:
                valid_types = ['inactivity', 'date', 'manual']
                if data['trigger_type'] not in valid_types:
                    return jsonify({
                        'success': False,
                        'error': f'Invalid trigger type. Must be one of: {", ".join(valid_types)}'
                    }), 400
                trigger.trigger_type = data['trigger_type']
            
            if 'trigger_value' in data:
                trigger.trigger_value = data['trigger_value']
            if 'is_triggered' in data:
                trigger.is_triggered = data['is_triggered']
            if 'last_checked' in data:
                trigger.last_checked = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': trigger.to_dict()
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @triggers_bp.route('/<int:trigger_id>', methods=['DELETE'])
    def delete_trigger(trigger_id):
        trigger = Trigger.query.get(trigger_id)
        if not trigger:
            return jsonify({
                'success': False,
                'error': 'Trigger not found'
            }), 404
        
        try:
            db.session.delete(trigger)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Trigger deleted successfully'
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @triggers_bp.route('/user/<int:user_id>', methods=['GET'])
    def get_triggers_by_user_id(user_id):
        try:
            triggers = Trigger.query.filter_by(user_id=user_id).all()
            triggers_list = [trigger.to_dict() for trigger in triggers]
            return jsonify({
                'success': True,
                'data': triggers_list,
                'count': len(triggers_list)
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # DispatchLog 라우트
    dispatchlog_bp = Blueprint('dispatchlog_test_' + str(uuid.uuid4())[:8], __name__)
    
    @dispatchlog_bp.route('', methods=['GET'])
    def get_all_dispatch_logs():
        try:
            logs = DispatchLog.query.all()
            logs_list = [log.to_dict() for log in logs]
            return jsonify({
                'success': True,
                'data': logs_list,
                'count': len(logs_list)
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @dispatchlog_bp.route('/<int:log_id>', methods=['GET'])
    def get_dispatch_log(log_id):
        try:
            log = DispatchLog.query.get(log_id)
            if not log:
                return jsonify({
                    'success': False,
                    'error': 'Dispatch log not found'
                }), 404
            return jsonify({
                'success': True,
                'data': log.to_dict()
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @dispatchlog_bp.route('', methods=['POST'])
    def create_dispatch_log():
        try:
            data = request.get_json()
        except:
            data = None
            
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # 필수 필드 검증
        required_fields = ['will_id', 'recipient_id']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # status 검증
        if 'status' in data:
            valid_statuses = ['pending', 'sent', 'delivered', 'read', 'failed']
            if data['status'] not in valid_statuses:
                return jsonify({
                    'success': False,
                    'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
                }), 400
        
        try:
            from datetime import datetime
            
            new_log = DispatchLog(
                will_id=data['will_id'],
                recipient_id=data['recipient_id'],
                sent_at=datetime.utcnow() if data.get('sent_at') else None,
                delivered_at=datetime.utcnow() if data.get('delivered_at') else None,
                read_at=datetime.utcnow() if data.get('read_at') else None,
                status=data.get('status', 'pending')
            )
            
            db.session.add(new_log)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': new_log.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @dispatchlog_bp.route('/<int:log_id>', methods=['PUT'])
    def update_dispatch_log(log_id):
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
        
        try:
            from datetime import datetime
            
            # 업데이트 가능한 필드들
            if 'status' in data:
                valid_statuses = ['pending', 'sent', 'delivered', 'read', 'failed']
                if data['status'] not in valid_statuses:
                    return jsonify({
                        'success': False,
                        'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
                    }), 400
                log.status = data['status']
            
            if 'sent_at' in data:
                log.sent_at = datetime.utcnow()
            if 'delivered_at' in data:
                log.delivered_at = datetime.utcnow()
            if 'read_at' in data:
                log.read_at = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': log.to_dict()
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @dispatchlog_bp.route('/<int:log_id>', methods=['DELETE'])
    def delete_dispatch_log(log_id):
        log = DispatchLog.query.get(log_id)
        if not log:
            return jsonify({
                'success': False,
                'error': 'Dispatch log not found'
            }), 404
        
        try:
            db.session.delete(log)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Dispatch log deleted successfully'
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @dispatchlog_bp.route('/will/<int:will_id>', methods=['GET'])
    def get_logs_by_will_id(will_id):
        try:
            logs = DispatchLog.query.filter_by(will_id=will_id).all()
            logs_list = [log.to_dict() for log in logs]
            return jsonify({
                'success': True,
                'data': logs_list,
                'count': len(logs_list)
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @dispatchlog_bp.route('/recipient/<int:recipient_id>', methods=['GET'])
    def get_logs_by_recipient_id(recipient_id):
        try:
            logs = DispatchLog.query.filter_by(recipient_id=recipient_id).all()
            logs_list = [log.to_dict() for log in logs]
            return jsonify({
                'success': True,
                'data': logs_list,
                'count': len(logs_list)
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    app.register_blueprint(userinfo_bp, url_prefix='/api/userinfo')
    app.register_blueprint(will_bp, url_prefix='/api/wills')
    app.register_blueprint(recipients_bp, url_prefix='/api/recipients')
    app.register_blueprint(triggers_bp, url_prefix='/api/triggers')
    app.register_blueprint(dispatchlog_bp, url_prefix='/api/dispatch-logs')
    
    # 데이터베이스 테이블 생성 및 스키마 확인
    with app.app_context():
        # 최신 스키마 확인 및 필요시 재생성
        _ensure_latest_schema(db)
        
        # 모든 테이블 생성 (누락된 테이블만 생성됨)
        db.create_all()
    
    return app, db, {
        'UserInfo': UserInfo,
        'Will': Will,
        'Recipient': Recipient,
        'Trigger': Trigger,
        'DispatchLog': DispatchLog
    }

class BaseTestCase(unittest.TestCase):
    """모든 테스트의 기본 클래스"""
    
    def setUp(self):
        """각 테스트 실행 전 설정"""
        self.app, self.db, self.models = create_test_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 테스트용 데이터베이스 테이블 생성 (이미 create_test_app에서 최신 스키마로 처리됨)
        self.db.create_all()
        
    def tearDown(self):
        """각 테스트 실행 후 정리"""
        try:
            # 모든 테스트 데이터 삭제 (운영 데이터 보호)
            for table in reversed(self.db.metadata.sorted_tables):
                self.db.session.execute(table.delete())
            self.db.session.commit()
        except Exception as e:
            # 에러 발생 시 롤백
            self.db.session.rollback()
        finally:
            self.db.session.remove()
            self.app_context.pop()