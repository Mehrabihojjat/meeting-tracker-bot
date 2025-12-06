"""
Daily reminder system for users to log their meetings
"""
from telegram.ext import ContextTypes
from database import db
from config import REMINDER_HOUR, REMINDER_MINUTE
import logging

logger = logging.getLogger(__name__)


async def send_daily_reminders(context: ContextTypes.DEFAULT_TYPE):
    """
    Send daily reminders to all users who haven't logged meetings today
    This job runs daily at the configured time
    """
    logger.info("Starting daily reminder job...")

    # Get all users who have ever used the bot
    all_users = db.get_all_users()

    sent_count = 0
    skipped_count = 0

    for user_id in all_users:
        try:
            # Check if user already logged a meeting today
            if db.user_logged_today(user_id):
                skipped_count += 1
                logger.debug(f"User {user_id} already logged today, skipping")
                continue

            # Send reminder
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "سلام! 👋\n\n"
                    "آیا جلسات امروزت رو ثبت کردی؟ 📝\n\n"
                    "اگه هنوز نکردی، الان وقتشه!\n"
                    "برای ثبت جلسه از /log استفاده کن."
                )
            )
            sent_count += 1
            logger.info(f"Reminder sent to user {user_id}")

        except Exception as e:
            logger.error(f"Failed to send reminder to user {user_id}: {e}")
            continue

    logger.info(
        f"Daily reminder job completed. "
        f"Sent: {sent_count}, Skipped: {skipped_count}, "
        f"Total users: {len(all_users)}"
    )


def setup_reminders(application):
    """
    Setup daily reminder job
    Call this function when initializing the bot
    """
    from datetime import time

    # Schedule daily reminder
    application.job_queue.run_daily(
        send_daily_reminders,
        time=time(hour=REMINDER_HOUR, minute=REMINDER_MINUTE),
        name='daily_meeting_reminder'
    )

    logger.info(
        f"Daily reminder scheduled for {REMINDER_HOUR:02d}:{REMINDER_MINUTE:02d}"
    )
