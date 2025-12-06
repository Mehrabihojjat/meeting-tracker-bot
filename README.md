# Meeting Tracker Telegram Bot 📊

یک ربات تلگرامی برای ثبت و آنالیز جلسات تیم، با هدف جمع‌آوری داده برای بهینه‌سازی تعداد و کیفیت جلسات.

## ویژگی‌ها

- ✅ ثبت جلسات با جزئیات کامل (موضوع، مدت، تعداد شرکت‌کنندگان، نوع، و...)
- 📊 گزارش‌گیری جامع با آمار کامل (فقط برای مدیر)
- 🔔 یادآوری روزانه برای ثبت جلسات
- 📈 آمار شخصی برای هر کاربر
- 💾 ذخیره‌سازی با SQLite (رایگان و ساده)
- 📥 امکان Export به CSV

## پیش‌نیازها

- Python 3.10 یا بالاتر
- یک اکانت تلگرام
- دسترسی به اینترنت

## نصب و راه‌اندازی

### 1. دریافت Bot Token

1. در تلگرام به [@BotFather](https://t.me/BotFather) پیام بده
2. دستور `/newbot` رو بزن
3. یک نام و username برای ربات انتخاب کن
4. Bot Token رو کپی کن (مثل: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. پیدا کردن User ID خودت

1. در تلگرام به [@userinfobot](https://t.me/userinfobot) پیام بده
2. ربات User ID تو رو نشون میده (یک عدد مثل: `123456789`)

### 3. نصب پروژه

```bash
# Clone کردن پروژه (یا دانلود ZIP)
git clone https://github.com/YOUR_USERNAME/meeting-tracker-bot.git
cd meeting-tracker-bot

# نصب dependencies
pip install -r requirements.txt
```

### 4. تنظیمات

فایل `.env` رو بساز و مقادیر زیر رو وارد کن:

```env
BOT_TOKEN=your_bot_token_here
ADMIN_USER_ID=your_telegram_user_id
DATABASE_PATH=meetings.db
REMINDER_HOUR=18
REMINDER_MINUTE=0
```

**توضیحات:**
- `BOT_TOKEN`: توکنی که از BotFather گرفتی
- `ADMIN_USER_ID`: User ID تلگرام خودت (فقط تو به /report دسترسی داری)
- `DATABASE_PATH`: مسیر فایل دیتابیس (پیش‌فرض: meetings.db)
- `REMINDER_HOUR`: ساعت یادآوری روزانه (24 ساعته، پیش‌فرض: 18)
- `REMINDER_MINUTE`: دقیقه یادآوری (پیش‌فرض: 0)

### 5. اجرا

```bash
python bot.py
```

ربات اجرا میشه و منتظر پیام‌ها می‌مونه! 🚀

## استفاده

### دستورات کاربران

- `/start` - شروع کار با ربات
- `/log` - ثبت جلسه جدید
- `/mystats` - مشاهده آمار شخصی
- `/help` - راهنمای کامل
- `/cancel` - لغو فرآیند ثبت جلسه

### دستورات مدیر (فقط ADMIN_USER_ID)

- `/report` - مشاهده گزارش جامع
- `/export` - دانلود داده‌ها به صورت CSV

## جریان ثبت جلسه

وقتی `/log` رو می‌زنی، ربات این سوالات رو می‌پرسه:

1. عنوان/موضوع جلسه چی بود؟
2. چند دقیقه طول کشید؟
3. چند نفر شرکت کردند؟
4. کِی بود؟ (صبح/عصر)
5. نوع جلسه؟ (Standup, Planning, Review, 1:1, Other)
6. تیم شما چه نامی داره؟
7. آیا شما lead تیم هستید؟
8. چقدر راضی بودی؟ (۱ تا ۵ ستاره)

## گزارش‌ها

گزارش `/report` شامل این موارد میشه:

- **آمار کلی:** تعداد جلسات، کاربران، میانگین رضایت
- **تفکیک زمانی:** مقایسه جلسات صبح و عصر
- **آمار ساعات:** مجموع و میانگین ساعات جلسه
- **Top 5 کاربران:** افرادی با بیشترین ساعت جلسه
- **آمار تیمی:** جلسات هر تیم با رضایت
- **نوع جلسات:** توزیع و رضایت انواع مختلف

## یادآوری روزانه

ربات هر روز ساعت تنظیم‌شده (پیش‌فرض: ۶ عصر) به کاربرانی که امروز جلسه ثبت نکرده‌ند یادآوری می‌فرسته.

## ساختار پروژه

```
meeting-tracker-bot/
├── bot.py                      # فایل اصلی
├── config.py                   # تنظیمات
├── database.py                 # مدیریت دیتابیس
├── handlers/
│   ├── __init__.py
│   ├── commands.py            # دستورات پایه
│   ├── log_meeting.py         # ثبت جلسه
│   ├── reminder.py            # یادآوری روزانه
│   └── report.py              # گزارش‌گیری
├── requirements.txt
├── .env                       # تنظیمات محیطی (ساخته نمیشه)
├── .env.example              # نمونه تنظیمات
├── .gitignore
└── README.md
```

## اجرا روی سرور (Deploy)

### گزینه ۱: اجرا در پس‌زمینه

```bash
# استفاده از nohup
nohup python bot.py > bot.log 2>&1 &
```

### گزینه ۲: استفاده از screen

```bash
screen -S meeting-bot
python bot.py
# برای خروج: Ctrl+A سپس D
# برای برگشت: screen -r meeting-bot
```

### گزینه ۳: systemd service

فایل `/etc/systemd/system/meeting-bot.service` رو بساز:

```ini
[Unit]
Description=Meeting Tracker Telegram Bot
After=network.target

[Service]
Type=simple
User=YOUR_USER
WorkingDirectory=/path/to/meeting-tracker-bot
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

سپس:

```bash
sudo systemctl enable meeting-bot
sudo systemctl start meeting-bot
sudo systemctl status meeting-bot
```

## امنیت

- 🔒 فایل `.env` رو هرگز commit نکن
- 🔒 Bot Token رو محرمانه نگه دار
- 🔒 فقط ADMIN_USER_ID به گزارش‌ها دسترسی داره
- 🔒 فایل دیتابیس رو backup بگیر

## مشارکت

هر گونه پیشنهاد و مشارکت خوش‌آمده است! لطفاً:

1. Fork کن
2. یک branch جدید بساز (`git checkout -b feature/AmazingFeature`)
3. تغییرات رو commit کن (`git commit -m 'Add some AmazingFeature'`)
4. Push کن (`git push origin feature/AmazingFeature`)
5. Pull Request باز کن

## لایسنس

MIT License - برای جزئیات فایل LICENSE رو ببین.

## پشتیبانی

اگه مشکلی داشتی یا سوالی بود، یک Issue باز کن.

---

**ساخته شده با ❤️ برای بهینه‌سازی جلسات تیمی**
