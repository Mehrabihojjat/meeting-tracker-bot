"""
Handler for generating reports (admin only)
"""
from telegram import Update
from telegram.ext import ContextTypes
from database import db
from config import ADMIN_USER_ID
import csv
import io


async def generate_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate comprehensive meeting report (admin only)"""
    user_id = update.effective_user.id

    # Check if user is admin
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text(
            "⛔ متأسفانه فقط مدیر سیستم می‌تونه گزارش ببینه."
        )
        return

    await update.message.reply_text("📊 در حال تهیه گزارش... لطفاً صبر کن")

    # Gather all statistics
    total_meetings = db.get_total_meetings_count()
    unique_users = db.get_unique_users_count()
    avg_satisfaction = db.get_average_satisfaction()

    # Time-based stats
    satisfaction_by_time = db.get_satisfaction_by_time()
    meetings_by_time = db.get_meetings_count_by_time()

    # Hours stats
    total_hours = db.get_total_hours()
    avg_hours_per_person = db.get_average_hours_per_person()
    top_users = db.get_top_users_by_hours(5)

    # Team stats
    team_stats = db.get_team_statistics()

    # Meeting type stats
    type_stats = db.get_meeting_type_statistics()

    # Build report message
    report = "📊 گزارش جامع جلسات\n"
    report += "═" * 30 + "\n\n"

    # Overall stats
    report += "📈 آمار کلی:\n"
    report += f"• تعداد کل جلسات: {total_meetings}\n"
    report += f"• تعداد کاربران: {unique_users}\n"
    report += f"• میانگین رضایت: {avg_satisfaction}/5 {'⭐' * int(avg_satisfaction)}\n\n"

    # Time-based stats
    report += "🕐 تفکیک زمانی:\n"
    morning_sat = satisfaction_by_time.get('صبح', 0)
    afternoon_sat = satisfaction_by_time.get('عصر', 0)
    morning_count = meetings_by_time.get('صبح', 0)
    afternoon_count = meetings_by_time.get('عصر', 0)

    report += f"• جلسات صبح: {morning_count} جلسه - میانگین رضایت: {morning_sat}/5\n"
    report += f"• جلسات عصر: {afternoon_count} جلسه - میانگین رضایت: {afternoon_sat}/5\n\n"

    # Hours stats
    report += "⏱ آمار ساعات:\n"
    report += f"• مجموع کل: {total_hours} ساعت\n"
    report += f"• میانگین به ازای هر نفر: {avg_hours_per_person} ساعت\n\n"

    if top_users:
        report += "🏆 Top 5 افراد با بیشترین ساعت جلسه:\n"
        for i, (name, hours) in enumerate(top_users, 1):
            report += f"  {i}. {name}: {hours} ساعت\n"
        report += "\n"

    # Team stats
    if team_stats:
        report += "👥 آمار تیم‌ها:\n"
        for team in team_stats:
            report += f"• {team['team']}\n"
            report += f"  - تعداد جلسات: {team['meetings']}\n"
            report += f"  - مجموع ساعات: {team['hours']} ساعت\n"
            report += f"  - میانگین رضایت: {team['satisfaction']}/5\n"
        report += "\n"

    # Meeting type stats
    if type_stats:
        report += "📋 آمار انواع جلسات:\n"
        for type_stat in type_stats:
            report += f"• {type_stat['type']}: {type_stat['count']} جلسه "
            report += f"(رضایت: {type_stat['satisfaction']}/5)\n"
        report += "\n"

    report += "═" * 30 + "\n"
    report += "برای دریافت فایل CSV از /export استفاده کن"

    await update.message.reply_text(report)


async def export_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export all meetings data to CSV (admin only)"""
    user_id = update.effective_user.id

    # Check if user is admin
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text(
            "⛔ متأسفانه فقط مدیر سیستم می‌تونه داده‌ها رو export کنه."
        )
        return

    await update.message.reply_text("📥 در حال آماده‌سازی فایل CSV...")

    # Get all meetings
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM meetings ORDER BY created_at DESC')
    meetings = cursor.fetchall()
    conn.close()

    if not meetings:
        await update.message.reply_text("هیچ داده‌ای برای export وجود نداره!")
        return

    # Create CSV in memory
    output = io.StringIO()
    csv_writer = csv.writer(output)

    # Write header
    csv_writer.writerow([
        'ID', 'User ID', 'Username', 'First Name', 'Last Name',
        'Title', 'Duration (min)', 'Participants', 'Time of Day',
        'Meeting Type', 'Team', 'Is Team Lead', 'Satisfaction', 'Created At'
    ])

    # Write data
    for meeting in meetings:
        csv_writer.writerow([
            meeting['id'], meeting['user_id'], meeting['username'],
            meeting['first_name'], meeting['last_name'], meeting['title'],
            meeting['duration_minutes'], meeting['participants_count'],
            meeting['time_of_day'], meeting['meeting_type'], meeting['team_name'],
            meeting['is_team_lead'], meeting['satisfaction_rating'],
            meeting['created_at']
        ])

    # Send CSV file
    output.seek(0)
    csv_bytes = output.getvalue().encode('utf-8-sig')  # UTF-8 with BOM for Excel
    await update.message.reply_document(
        document=csv_bytes,
        filename='meetings_export.csv',
        caption='📊 فایل CSV داده‌های جلسات'
    )

    output.close()
