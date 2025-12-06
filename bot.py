"""
Main entry point for Meeting Tracker Telegram Bot
"""
import logging
from telegram.ext import Application, CommandHandler

from config import BOT_TOKEN
from handlers.log_meeting import log_meeting_handler
from handlers.report import generate_report, export_csv
from handlers.commands import start_command, help_command, mystats_command
from handlers.reminder import setup_reminders

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Start the bot"""
    logger.info("Starting Meeting Tracker Bot...")

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers

    # Basic commands
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('mystats', mystats_command))

    # Log meeting conversation handler
    application.add_handler(log_meeting_handler)

    # Report commands (admin only)
    application.add_handler(CommandHandler('report', generate_report))
    application.add_handler(CommandHandler('export', export_csv))

    # Setup daily reminders
    setup_reminders(application)

    # Start the bot
    logger.info("Bot is running. Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=True)


if __name__ == '__main__':
    main()
