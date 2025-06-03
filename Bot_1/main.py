# Add the project root directory to sys.path
import sys, os
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importing needed modules
import celebrities
import openAI_module as cosmetic_surgent
from database import init_db, save_user_to_db

from telegram import (Update, ReplyKeyboardMarkup, 
                      ReplyKeyboardRemove, KeyboardButton)
from telegram.ext import (ApplicationBuilder, CommandHandler, 
                          MessageHandler, filters, 
                          ConversationHandler, ContextTypes)

# Telegram Bot Token
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# States
GENDER, PHOTO, FIRSTNAME, LASTNAME, PHONE, CITY = range(6)

# Registration Status
NOT_REGISTERED = "کاربر ربات را شروع کرده است، اما هنوز فرم ثبت‌نام را کامل نکرده است!"
REGISTERED = "کاربر ربات را شروع کرده و فرم ثبت‌نام را به طور کامل پر کرده است."

# Bot's Identification Number (To discern data in the database)
BOT_ID = 1

def handle_data_and_database(context: ContextTypes.DEFAULT_TYPE, column, data, registration_status):
   context.user_data['bot_id'] = BOT_ID
   context.user_data['registration_status'] = registration_status  
   context.user_data[column] = data
   save_user_to_db(context.user_data)

# --- The Start Bot Handler --- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Add User To the users.db using their unique telegram_id
    telegram_id = update.effective_user.id
    handle_data_and_database(context, 'telegram_id', telegram_id, NOT_REGISTERED)
    
    # Keyboard Buttons To Specify User's Gender
    keyboard = [
        [KeyboardButton("خانم")],
        [KeyboardButton("آقا")]
    ]
    
    await update.message.reply_text("سلام! من ربات هوش مصنوعی جراحی زیبایی شما هستم. آماده‌ام کمکتان کنم شبیه سلبریتی مورد علاقه‌تان شوید! 🎯")
    await update.message.reply_text(
                                    "\n\nلطفاً جنسیت خود را برای ما مشخص کنید.",
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

# --- Handle Uploaded Picture & Call Upon AI Logic --- #
async def handle_picture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle Provided Photo
    file_id = update.message.photo[-1].file_id
    handle_data_and_database(context, 'user_photo', file_id, NOT_REGISTERED)
     
    await update.message.reply_text("عکس شما دریافت شد، در حال پردازش هستم. لطفاً صبور باشید! ✅")

    #return CELEB_CHOICE
    user_file_id = context.user_data['user_photo']
    picture_file = await context.bot.get_file(user_file_id)
    user_image_path = f"../static/pictures/{user_file_id}_{BOT_ID}.jpg"
    await picture_file.download_to_drive(user_image_path)

    # Translating gender to english for searchinng inside celebrities.celebrities dictionary
    if context.user_data['gender'] == "خانم":
        gender_english_format = "female"
    else:
        gender_english_format = "male"

    # Calling For AI Surgent
    result = cosmetic_surgent.analyze_faces_find_similarities(user_image_path, celebrities.celebrities[gender_english_format])
    result = cosmetic_surgent.analyze_faces_find_similarities(user_image_path, celebrities.celebrities[gender_english_format])

    if result is None or not isinstance(result, dict):
        await update.message.reply_text("متأسفم، مشکلی در حین پردازش عکس پیش آمد. لطفاً بعداً دوباره تلاش کنید.")
        return ConversationHandler.END
    
    #print("DEBUG RESULT:", result)
    #context.user_data['celeb_name'] = result.get("celebrity_name", "Unknown")
    #context.user_data['surgery_suggestions'] = result.get("suggestions", "No suggestions available.") 
    celeb_name = result.get("celebrity_name", "Unknown")
    surgery_suggestions = result.get("suggestions", "No suggestions available.")
    handle_data_and_database(context, 'celeb_name', celeb_name, NOT_REGISTERED)
    handle_data_and_database(context, 'surgery_suggestions', surgery_suggestions, NOT_REGISTERED)
    

    # Send the Matching Celeb Image Back:
    if result.get("celebrity_image"):
        try:
            with open(result["celebrity_image"], "rb") as photo:
                await update.message.reply_photo(photo=photo, caption=f"سلبریتی مشابه: {context.user_data['celeb_name']}")
        except Exception as e:
            await update.message.reply_text("Error displaying celebrity image.")

    await update.message.reply_text(
        f" این پیشنهاد من برای شبیه شدن به {context.user_data['celeb_name']}:\n\n{context.user_data['surgery_suggestions']}")

    await update.message.reply_text("خب، حالا بریم سراغ جزئیات شما. اسم کوچیکتون چیه؟")
    
    return FIRSTNAME

# --- Function To Get The User's First Name --- #
async def get_firstname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first_name = update.message.text
    handle_data_and_database(context, 'first_name', first_name, NOT_REGISTERED)
    
    await update.message.reply_text("فامیلیتون چیه؟")
    return LASTNAME

# --- Function To Get The User's Last Name --- #
async def get_lastname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last_name = update.message.text
    handle_data_and_database(context, 'last_name', last_name, NOT_REGISTERED)

    await update.message.reply_text("شماره تلفنتون چیه؟")
    return PHONE

# --- Function To Get The User's Phone Number --- #
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    handle_data_and_database(context, 'phone', phone, NOT_REGISTERED)

    await update.message.reply_text("شهر محل اقامت شما کجاست؟")
    return CITY

# --- Function To Get City Where The User Is Resident, Then Saving All The User Data Gathered Thus Far To Our users.db Database --- #
async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text
    handle_data_and_database(context, 'city', city, REGISTERED)
    
    # Save to database
    #save_user_to_db(context.user_data)
    
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



