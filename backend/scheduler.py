from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import models
from database import SessionLocal
from email_service import send_email
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def check_switches():
    """Check all active switches and trigger if needed"""
    db = SessionLocal()
    try:
        switches = db.query(models.Switch).filter(
            models.Switch.is_active == True,
            models.Switch.is_triggered == False
        ).all()
        
        for switch in switches:
            # Calculate deadline
            deadline = switch.last_check_in + timedelta(days=switch.check_in_interval_days)
            
            if datetime.utcnow() > deadline:
                logger.info(f"Triggering switch {switch.id} for user {switch.user_id}")
                
                # Trigger the switch
                switch.is_triggered = True
                switch.triggered_at = datetime.utcnow()
                
                # Send all messages
                for message in switch.messages:
                    if not message.is_sent:
                        success = await send_email(
                            message.recipient_email,
                            message.subject,
                            message.body
                        )
                        if success:
                            message.is_sent = True
                            message.sent_at = datetime.utcnow()
                
                db.commit()
                logger.info(f"Switch {switch.id} triggered successfully")
    except Exception as e:
        logger.error(f"Error in check_switches: {str(e)}")
    finally:
        db.close()


def start_scheduler():
    """Start the scheduler to check switches every hour"""
    scheduler.add_job(check_switches, 'interval', hours=1, id='check_switches')
    scheduler.start()
    logger.info("Scheduler started")


def shutdown_scheduler():
    """Shutdown the scheduler"""
    scheduler.shutdown()
    logger.info("Scheduler shutdown")
