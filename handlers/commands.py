"""
Basic commands for the bot (/start, /help, /mystats)
"""
from telegram import Update
from telegram.ext import ContextTypes
from database import db


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    welcome_message = (
        f"سلام {user.first_name}! 👋\n\n"
        "به ربات Meeting Tracker خوش اومدی! 📊\n\n"
        "این ربات برای ثبت و آنالیز جلسات تیمه.\n\n"
        "دستورات موجود:\n"
        "• /log - ثبت جلسه جدید\n"
        "• /mystats - آمار شخصی من\n"
        "• /help - راهنمای کامل\n"
        "• /cancel - لغو فرآیند ثبت\n\n"
        "برای شروع، از /log استفاده کن! 🚀"
    )
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_message = (
        "📖 راهنمای استفاده از Meeting Tracker Bot\n\n"
        "═" * 30 + "\n\n"
        "🎯 هدف:\n"
        "این ربات برای جمع‌آوری داده درباره جلسات تیم و کمک به بهینه‌سازی "
        "تعداد و کیفیت جلسات ساخته شده.\n\n"
        "📝 ثبت جلسه:\n"
        "با دستور /log می‌تونی یک جلسه جدید ثبت کنی.\n"
        "ربات از تو چند سوال می‌پرسه:\n"
        "• موضوع جلسه\n"
        "• مدت زمان (به دقیقه)\n"
        "• تعداد شرکت‌کنندگان\n"
        "• زمان برگزاری (صبح/عصر)\n"
        "• نوع جلسه (Standup, Planning, Review, 1:1, etc.)\n"
        "• نام تیم\n"
        "• آیا lead تیم هستی\n"
        "• میزان رضایت (۱ تا ۵ ستاره)\n\n"
        "📊 آمار شخصی:\n"
        "با /mystats می‌تونی آمار جلسات خودت رو ببینی.\n\n"
        "❌ لغو:\n"
        "در هر مرحله از ثبت جلسه، می‌تونی با /cancel فرآیند رو لغو کنی.\n\n"
        "🔔 یادآوری:\n"
        "هر روز ساعت ۶ عصر، ربات یادآوری می‌فرسته که جلسات روزت رو ثبت کنی.\n\n"
        "═" * 30 + "\n\n"
        "سوالی داشتی، از /help استفاده کن! 💡"
    )
    await update.message.reply_text(help_message)


async def mystats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mystats command - show personal statistics"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    # Get user statistics
    stats = db.get_user_statistics(user_id)

    if not stats:
        await update.message.reply_text(
            f"سلام {user_name}! 👋\n\n"
            "هنوز هیچ جلسه‌ای ثبت نکردی!\n"
            "برای شروع از /log استفاده کن."
        )
        return

    # Get user's meetings
    meetings = db.get_user_meetings(user_id)

    # Build stats message
    message = f"📊 آمار شخصی {user_name}\n"
    message += "═" * 30 + "\n\n"

    message += "📈 خلاصه آمار:\n"
    message += f"• تعداد کل جلسات: {stats['total_meetings']}\n"
    message += f"• مجموع ساعات: {stats['total_hours']} ساعت\n"
    message += f"• میانگین مدت هر جلسه: {stats['avg_duration']} دقیقه\n"
    message += f"• میانگین رضایت: {stats['avg_satisfaction']}/5 "
    message += "⭐" * int(stats['avg_satisfaction']) + "\n\n"

    # Latest meetings
    if meetings:
        message += "📝 آخرین جلسات:\n"
        for meeting in meetings[:5]:  # Show last 5
            stars = "⭐" * meeting['satisfaction_rating']
            message += (
                f"• {meeting['title']} "
                f"({meeting['duration_minutes']} دقیقه) - {stars}\n"
            )
        message += "\n"

    message += "═" * 30 + "\n"
    message += "برای ثبت جلسه جدید از /log استفاده کن!"

    await update.message.reply_text(message)
