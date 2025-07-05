# Add the project root directory to sys.path
import sys, os
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import celebrities
import openAI_module as cosmetic_surgent
from database import init_db, save_user_to_db

from telegram import (Update, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, KeyboardButton)
from telegram.ext import (ApplicationBuilder, CommandHandler,
                          MessageHandler, filters,
                          ConversationHandler, ContextTypes)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PICTURES_DIR = os.path.join(BASE_DIR, 'static', 'pictures')

# Telegram Bot Token
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN_2")

# States
GENDER, PHOTO, CELEB_CHOICE, FIRSTNAME, LASTNAME, PHONE, CITY = range(7)

# Registration Status
NOT_REGISTERED = "کاربر ربات را شروع کرده است، اما هنوز فرم ثبت‌نام را کامل نکرده است!"
REGISTERED = "کاربر ربات را شروع کرده و فرم ثبت‌نام را به طور کامل پر کرده است."

# Bot's Identification Number (To discern data in the database)
BOT_ID = "@CosSur"

def handle_data_and_database(context: ContextTypes.DEFAULT_TYPE, column, data, registration_status):
   context.user_data['bot_id'] = BOT_ID
   context.user_data['registration_status'] = registration_status
   context.user_data[column] = data
   save_user_to_db(context.user_data)

def translate_gender(context):
    if context.user_data['gender'] == "خانم":
        gender_english_format = "female"
    else:
        gender_english_format = "male"
    return gender_english_format

# --- The Start Bot Handler --- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Add User To the users.db using their unique telegram_id
    telegram_id = update.effective_user.id
    handle_data_and_database(context, 'telegram_id', telegram_id, NOT_REGISTERED)

    # Define Keyboard Buttons
    keyboard = [
        [KeyboardButton("خانم")],
        [KeyboardButton("آقا")]
    ]

    # Ask user to determine their gender via the defined buttons
    await update.message.reply_text("سلام! من ربات هوش مصنوعی جراحی زیبایی شما هستم. آماده‌ام کمکتان کنم شبیه سلبریتی مورد علاقه‌تان شوید!"\
                                    "\n\nلطفاً جنسیت خود را برای ما مشخص کنید. 🎯",
                                    reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    return GENDER

# --- Handle User's Gender --- #
async def handle_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle Gender
    gender = update.message.text
    handle_data_and_database(context, 'gender', gender, NOT_REGISTERED)

    # Remove The Keyboard Options
    await update.message.reply_text("لطفاً عکسی از خودتان برایمان ارسال کنید.🎯" \
                                    "\n\nتوصیه می‌شود عکس ارسالی بدون آرایش غلیظ و عینک باشد و نور کافی داشته باشد.",
                                     reply_markup=ReplyKeyboardRemove())
    return PHOTO

# --- Handle Uploaded Picture --- #
async def handle_picture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عکس شما دریافت شد، در حال پردازش هستم. لطفاً صبور باشید! ✅")
    file_id = update.message.photo[-1].file_id
    handle_data_and_database(context, 'user_photo', file_id, NOT_REGISTERED)

    # Translating gender to english
    gender_english_format = translate_gender(context)

    keyboard = []
    if gender_english_format == "male":
        keyboard = [
            [KeyboardButton("Brad Pitt")],
            [KeyboardButton("Christian Bale")],
            [KeyboardButton("Jake Gyllenhaal")],
            [KeyboardButton("Leonardo DiCaprio")],
            [KeyboardButton("Matthew McConaughey")],
            [KeyboardButton("Ryan Gosling")]
        ]
    elif gender_english_format == "female":
        keyboard = [
            [KeyboardButton("Ana DE Armas")],
            [KeyboardButton("Angelina Jolie")],
            [KeyboardButton("Emma Mackey")],
            [KeyboardButton("Emma Stone")],
            [KeyboardButton("Emma Watson")],
            [KeyboardButton("Margot Robbie")],
            [KeyboardButton("Natalie Portman")],
            [KeyboardButton("Scarlett Johansson")],
            [KeyboardButton("Taylor Swift")]
        ]

    await update.message.reply_text(
        "عالیه! حالا یه سلبریتی رو انتخاب کن که دوست داری شبیه اون بشی:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )

    return CELEB_CHOICE

# --- Handle Celebrity Choice --- #
async def handle_celebrity_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    celeb_name = update.message.text
    handle_data_and_database(context, 'celeb_name', celeb_name, NOT_REGISTERED)

    await update.message.reply_text(f"متوجه شدم! شما می‌خواهید شبیه {celeb_name} شوید. در حال بررسی عکس‌ها هستم. لطفاً صبور باشید.")

    celeb_image_path = ""
    gender_english_format = translate_gender(context)
    if gender_english_format == "male":
        for celeb in celebrities.celebrities["male"]:
            if celeb['name'] == celeb_name:
                celeb_image_path = celeb['image_path']
                break

    elif gender_english_format == "female":
        for celeb in celebrities.celebrities["female"]:
            if celeb['name'] == celeb_name:
                celeb_image_path = celeb['image_path']
                break

    # Downloading User's Picture from Telegream
    user_file_id = context.user_data['user_photo']
    picture_file = await context.bot.get_file(user_file_id)
    user_image_path = f"{PICTURES_DIR}/{user_file_id}_{BOT_ID}.jpg"
    await picture_file.download_to_drive(user_image_path)

    # Calling For AI Surgent
    result = cosmetic_surgent.analyze_faces(user_image_path, celeb_image_path)
    #context.user_data['surgery_suggestions'] = result
    handle_data_and_database(context, 'surgery_suggestions', result, NOT_REGISTERED)

    await update.message.reply_text(
        f"این پیشنهاد من برای شبیه شدن به سلبریتی مورد نظرتان است {celeb_name}:\n\n{result}",
        reply_markup=ReplyKeyboardRemove()
    )
    await update.message.reply_text("خب، حالا بریم سراغ جزئیات شما. اسم کوچیکتون چیه؟")
    return FIRSTNAME


# --- Function To Get The User's First Name --- #
async def get_firstname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle User's First Name
    first_name = update.message.text
    handle_data_and_database(context, 'first_name', first_name, NOT_REGISTERED)

    # Ask for their Last Name
    await update.message.reply_text("فامیلیتون چیه؟")
    return LASTNAME

# --- Function To Get The User's Last Name --- #
async def get_lastname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle User's Last Name
    last_name = update.message.text
    handle_data_and_database(context, 'last_name', last_name, NOT_REGISTERED)

    # Ask for their Phone Number
    await update.message.reply_text("لطفاً شماره تلفن خود را به ما بدهید:")
    return PHONE

# --- Function To Get The User's Phone Number --- #
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle User's Phone Number
    phone = update.message.text
    handle_data_and_database(context, 'phone', phone, NOT_REGISTERED)

    # Ask where they live
    await update.message.reply_text("شهر محل اقامت شما کجاست؟")
    return CITY

# --- Function To Get City Where The User Is Resident, Then Saving All The User Data Gathered Thus Far To Our users.db Database --- #
async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle User's City
    city = update.message.text
    handle_data_and_database(context, 'city', city, REGISTERED)

    await update.message.reply_text("ممنون! اطلاعات شما ذخیره شد. به زودی با شما تماس می‌گیریم. 😊")

    await update.message.reply_text("ربات متوقف شد." \
    "\nلطفاً برای شروع مجدد ربات، روی دکمه «start» از منو کلیک کنید.")
    return ConversationHandler.END

# --- Function To Stop The Bot From Any Furthur Progerssing --- #
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ربات متوقف شد." \
    "\nلطفاً برای شروع مجدد ربات، روی دکمه «start» از منو کلیک کنید.")
    return ConversationHandler.END

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gender)],
        PHOTO: [MessageHandler(filters.PHOTO, handle_picture)],
        CELEB_CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_celebrity_choice)],
        FIRSTNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_firstname)],
        LASTNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_lastname)],
        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
    },
    fallbacks=[
        CommandHandler("stop", stop),
        CommandHandler("start", start)
    ]
)

app.add_handler(conv_handler)

init_db()
app.run_polling()