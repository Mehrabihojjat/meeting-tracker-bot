"""
Configuration management for Meeting Tracker Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', 0))

# Database Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'meetings.db')

# Reminder Configuration
REMINDER_HOUR = int(os.getenv('REMINDER_HOUR', 18))
REMINDER_MINUTE = int(os.getenv('REMINDER_MINUTE', 0))

# Meeting Types
MEETING_TYPES = ['Standup', 'Planning', 'Review', '1:1', 'Other']

# Time of Day Options
TIME_OF_DAY_OPTIONS = ['صبح', 'عصر']

# Validation
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN must be set in .env file")

if not ADMIN_USER_ID:
    raise ValueError("ADMIN_USER_ID must be set in .env file")
