"""
Handler for logging meetings - Step-by-step conversation
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from database import db
from config import MEETING_TYPES, TIME_OF_DAY_OPTIONS

# Conversation states
TITLE, DURATION, PARTICIPANTS, TIME, TYPE, TEAM, LEAD, SATISFACTION = range(8)


async def start_log_meeting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the meeting logging process"""
    await update.message.reply_text(
        "بیا یک جلسه جدید ثبت کنیم! 📝\n\n"
        "عنوان یا موضوع جلسه چی بود؟\n"
        "(برای لغو از /cancel استفاده کن)"
    )
    return TITLE


async def get_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get meeting title"""
    context.user_data['title'] = update.message.text

    await update.message.reply_text(
        f"عالی! موضوع: {update.message.text}\n\n"
        "این جلسه چند دقیقه طول کشید؟ (فقط عدد بنویس)"
    )
    return DURATION


async def get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get meeting duration"""
    try:
        duration = int(update.message.text)
        if duration <= 0:
            raise ValueError()

        context.user_data['duration'] = duration

        await update.message.reply_text(
            f"جلسه {duration} دقیقه‌ای ✓\n\n"
            "چند نفر توی این جلسه بودن؟ (فقط عدد)"
        )
        return PARTICIPANTS

    except ValueError:
        await update.message.reply_text(
            "لطفاً یک عدد معتبر وارد کن (مثلاً 30، 60، 90)"
        )
        return DURATION


async def get_participants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get number of participants"""
    try:
        participants = int(update.message.text)
        if participants <= 0:
            raise ValueError()

        context.user_data['participants'] = participants

        # Create inline keyboard for time of day
        keyboard = [
            [InlineKeyboardButton("🌅 صبح", callback_data="time_صبح")],
            [InlineKeyboardButton("🌆 عصر", callback_data="time_عصر")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"{participants} نفر شرکت کردن ✓\n\n"
            "این جلسه کِی برگزار شد؟",
            reply_markup=reply_markup
        )
        return TIME

    except ValueError:
        await update.message.reply_text(
            "لطفاً یک عدد معتبر وارد کن (مثلاً 2، 5، 10)"
        )
        return PARTICIPANTS


async def get_time_of_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get time of day via callback"""
    query = update.callback_query
    await query.answer()

    time_choice = query.data.replace("time_", "")
    context.user_data['time_of_day'] = time_choice

    # Create inline keyboard for meeting types
    keyboard = [
        [InlineKeyboardButton(meeting_type, callback_data=f"type_{meeting_type}")]
        for meeting_type in MEETING_TYPES
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"زمان: {time_choice} ✓\n\n"
        "نوع جلسه چی بود؟",
        reply_markup=reply_markup
    )
    return TYPE


async def get_meeting_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get meeting type via callback"""
    query = update.callback_query
    await query.answer()

    meeting_type = query.data.replace("type_", "")
    context.user_data['meeting_type'] = meeting_type

    await query.edit_message_text(
        f"نوع جلسه: {meeting_type} ✓\n\n"
        "تیم شما چه نامی داره؟ (مثلاً Backend Team، Frontend Team)"
    )
    return TEAM


async def get_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get team name"""
    context.user_data['team'] = update.message.text

    # Create inline keyboard for team lead question
    keyboard = [
        [InlineKeyboardButton("✅ بله", callback_data="lead_yes")],
        [InlineKeyboardButton("❌ خیر", callback_data="lead_no")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"تیم: {update.message.text} ✓\n\n"
        "آیا شما lead این تیم هستید؟",
        reply_markup=reply_markup
    )
    return LEAD


async def get_team_lead(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get team lead status via callback"""
    query = update.callback_query
    await query.answer()

    is_lead = query.data == "lead_yes"
    context.user_data['is_lead'] = is_lead

    # Create inline keyboard for satisfaction rating
    keyboard = [
        [
            InlineKeyboardButton("⭐", callback_data="rating_1"),
            InlineKeyboardButton("⭐⭐", callback_data="rating_2"),
            InlineKeyboardButton("⭐⭐⭐", callback_data="rating_3"),
        ],
        [
            InlineKeyboardButton("⭐⭐⭐⭐", callback_data="rating_4"),
            InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data="rating_5"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    lead_text = "بله" if is_lead else "خیر"
    await query.edit_message_text(
        f"Team Lead: {lead_text} ✓\n\n"
        "چقدر از این جلسه راضی بودی؟\n"
        "(این جلسه چقدر کمک کرد کارت پیش بره؟)",
        reply_markup=reply_markup
    )
    return SATISFACTION


async def get_satisfaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get satisfaction rating and save to database"""
    query = update.callback_query
    await query.answer()

    rating = int(query.data.replace("rating_", ""))
    context.user_data['satisfaction'] = rating

    # Save to database
    user = update.effective_user
    data = context.user_data

    meeting_id = db.add_meeting(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        title=data['title'],
        duration_minutes=data['duration'],
        participants_count=data['participants'],
        time_of_day=data['time_of_day'],
        meeting_type=data['meeting_type'],
        team_name=data['team'],
        is_team_lead=data['is_lead'],
        satisfaction_rating=rating
    )

    # Format summary
    stars = "⭐" * rating
    summary = (
        f"✅ جلسه با موفقیت ثبت شد!\n\n"
        f"📋 خلاصه:\n"
        f"• موضوع: {data['title']}\n"
        f"• مدت: {data['duration']} دقیقه\n"
        f"• تعداد شرکت‌کنندگان: {data['participants']} نفر\n"
        f"• زمان: {data['time_of_day']}\n"
        f"• نوع: {data['meeting_type']}\n"
        f"• تیم: {data['team']}\n"
        f"• رضایت: {stars}\n\n"
        f"برای ثبت جلسه بعدی از /log استفاده کن."
    )

    await query.edit_message_text(summary)

    # Clear user data
    context.user_data.clear()

    return ConversationHandler.END


async def cancel_log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the logging process"""
    await update.message.reply_text(
        "ثبت جلسه لغو شد! ❌\n"
        "وقتی خواستی دوباره /log رو بزن."
    )
    context.user_data.clear()
    return ConversationHandler.END


# Create conversation handler
log_meeting_handler = ConversationHandler(
    entry_points=[CommandHandler('log', start_log_meeting)],
    states={
        TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_title)],
        DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_duration)],
        PARTICIPANTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_participants)],
        TIME: [CallbackQueryHandler(get_time_of_day, pattern='^time_')],
        TYPE: [CallbackQueryHandler(get_meeting_type, pattern='^type_')],
        TEAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_team)],
        LEAD: [CallbackQueryHandler(get_team_lead, pattern='^lead_')],
        SATISFACTION: [CallbackQueryHandler(get_satisfaction, pattern='^rating_')],
    },
    fallbacks=[CommandHandler('cancel', cancel_log)],
)
