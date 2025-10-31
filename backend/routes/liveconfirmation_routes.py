
# 기존 라우트 패턴에 맞게 Blueprint factory 함수로 변경
from flask import Blueprint
from datetime import datetime

def init_liveconfirmation_routes(db, DispatchLog):
    liveconfirmation_routes = Blueprint('liveconfirmation', __name__)

    @liveconfirmation_routes.route('/auth/liveconfirmation/<int:dispatch_log_id>/', methods=['GET'])
    def live_confirmation(dispatch_log_id):
        dispatch_log = db.session.query(DispatchLog).filter_by(id=dispatch_log_id).first()
        if dispatch_log:
            dispatch_log.read_at = datetime.utcnow()
            dispatch_log.status = 'read'
            db.session.commit()
            return "인증이 완료되었습니다."
        else:
            return "잘못된 링크입니다.", 404

    return liveconfirmation_routes