from multiprocessing import context
import time
import ssl
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os
from dotenv import load_dotenv

# Flask app과 db를 import
import sys
from pathlib import Path

import logging
sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.app import app, db

# .env 환경변수 로드
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))


from backend.triggers.email_templates import live_confirmation_subject, live_confirmation_body

# 로거 설정
logger = logging.getLogger("live_confirmation_scheduler")
logging.basicConfig(level=logging.INFO)

# 이메일 발송 함수 (간단 예시)
def send_email(to_email, subject, body):
    smtp_host = os.environ.get('SMTP_HOST')
    smtp_port = int(os.environ.get('SMTP_PORT'))
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')
    logger.info(f"[SMTP_HOST]  {smtp_host}")
    logger.info(f"[SMTP_PORT]  {smtp_port}")
    logger.info(f"[SMTP_USER]  {smtp_user}")
    logger.info(f"[SMTP_PASS]  {smtp_pass}")    

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = to_email
    logger.info(f"[subject]  {subject}")
    logger.info(f"[From]  {smtp_user}")
    logger.info(f"[to_email]  {to_email}")


    try:

#        context = ssl.SSLContext(ssl.PROTOCOL_TLS)  # TLS 1.0~1.2 허용
#        context = ssl._create_unverified_context()
        context = ssl.create_default_context()

        with smtplib.SMTP(smtp_host, smtp_port) as server:
        #    server.starttls(context=context)
        #    server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [to_email], msg.as_string())
            logger.info(f"after sendmail")
    except Exception as e:
        logger.error(f"[SMTP ERROR] {type(e).__name__}: {e}")
        raise


# 트리거 조회 및 이메일 발송

def process_email_triggers():
    logger.info(f"Trigger email processing started at {datetime.now()}")

    query = """
        SELECT t.id, t.user_id, t.trigger_date, u.email, w.id as will_id, u.id as clientid
        FROM triggers t
        JOIN UserInfo u ON t.user_id = u.user_id
        JOIN wills w ON t.user_id = w.user_id
        where status = 'pending'
        and trigger_date < CURDATE()
    """


    with app.app_context():
        with db.engine.connect() as connection:
            result = connection.execute(db.text(query))
            rows = result.fetchall()
            for row in rows:
                trigger_id, user_id, trigger_date, email, will_id, userid = row
                try:
                    # live confirmation email 발송 (실제 발송은 주석 처리)
                    # 동적 URL/WillID 치환
                    base_url = os.environ.get('BASE_URL', 'localhost:5000')
                    body = live_confirmation_body.replace('$url$', base_url).replace('$willid$', str(will_id))
                    logger.info(f"[before] Would send live confirmation email to {email} for trigger {trigger_id}")
                    send_email(email, live_confirmation_subject, body)
                    logger.info(f"[After] Would send live confirmation email to {email} for trigger {trigger_id}")
                    connection.execute(db.text("UPDATE triggers SET status='completed', updated_at=NOW() WHERE id=:id"), {"id": trigger_id})

                    # dispatch_log 기록 추가
                    connection.execute(
                        db.text("""
                            INSERT INTO dispatch_log (will_id, recipient_id, sent_at, status, type)
                            VALUES (:will_id, 0, NOW(), 'sent', 1)
                        """),
                        {"will_id": row[4]}
                    )
                    connection.commit()  # 트랜잭션 커밋
                except Exception as e:
                    logger.error(f"Failed to process trigger {trigger_id}: {e}")
                    try:
                        connection.rollback()
                    except Exception as rollback_err:
                        logger.error(f"[ROLLBACK ERROR] {type(rollback_err).__name__}: {rollback_err}")

if __name__ == "__main__":
    while True:
        process_email_triggers()
        time.sleep(60)  # 1분마다 실행 (원하는 주기로 조정)
