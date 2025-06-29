# Import Needed Modules 
import sys, os
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from telegram import (Update, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, KeyboardButton)

from telegram.ext import (ApplicationBuilder, CommandHandler,
                          MessageHandler, filters,
                          ConversationHandler, ContextTypes)

from database import init_db, save_user_to_db
from verify_user_image import verify_user_image

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# ===============================

# Bot Phases
# TODO: Define bot phases here as needed
HANDLE_GENDER, HANDLE_PICTURE  = range(2)
# ===============================

# Telegram Bot's ID
TELEGRAM_BOT_ID = "@CosmeticSurgent_Bot"
# ===============================

# User Registration Status
NOT_REGISTERED = "کاربر ربات را شروع کرده است، اما هنوز فرم ثبت‌نام را کامل نکرده است!"
REGISTERED = "کاربر ربات را شروع کرده و فرم ثبت‌نام را به طور کامل پر کرده است."
# ===============================

# Directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PICTURES_DIR = os.path.join(BASE_DIR, 'static', 'pictures')
# ================================

# Function to handle data
def handle_data_and_database(context: ContextTypes.DEFAULT_TYPE,
                             column, data, registration_status):
   context.user_data['bot_id'] = TELEGRAM_BOT_ID
   context.user_data['registrations_status'] = registration_status    
   context.user_data[column] = data    
   save_user_to_db(context.user_data)
# ===============================

# --- Bot Functions: Start Handler --- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Add user telegram id to the database
    user_telegram_id = update.message.from_user.id
    handle_data_and_database(context, 'telegram_id', user_telegram_id, NOT_REGISTERED)
    
    return await greet(update, context)
# ===============================
   
# --- Bot Function: Greet User --- # 
async def greet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Greet The User
    await update.message.reply_text("سلام عزیزم من هوش مصنوعی کلینیک زیبایی ماهتا هستم میخوام کمکت کنم بفهمی شبیه کدوم سلبریتی هستی.")
    
    return await gender(update, context)
# =============================== 

# --- Bot Function: Get User Gender --- #
async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Keyboard Buttons To Get Users's Gender
    keyboard = [
        [KeyboardButton("آقا")],
        [KeyboardButton("خانم")]
    ]
    # Ask For Users Gender
    await update.message.reply_text("بگو آقایی یا خانم؟",
                                    reply_markup=ReplyKeyboardMarkup(keyboard,
                                                                     one_time_keyboard=True,
                                                                     resize_keyboard=True))
    return HANDLE_GENDER
# ===============================

# --- Bot Function: Gender Handler --- #
async def handle_gender(update:Update, context: ContextTypes.DEFAULT_TYPE):
    gender = update.message.text
    handle_data_and_database(context, 'gender', gender, NOT_REGISTERED)
    
    return await picture(update, context)
# ===============================

# --- Bot Function: Get User's Picture --- #
async def picture(update:Update, context: ContextTypes.DEFAULT_TYPE):
    # Ask user to send a picture of themselves
    await update.message.reply_text("خب! حالا یه عکس واضح از صورتت بهم بده. لطفا یه عکس واضح از رو به رو بدون آرایش غلیظ و عینک باشه. نور کافی هم داشته باشه!",
                                    reply_markup=ReplyKeyboardRemove())
    
    return HANDLE_PICTURE

# --- Bot Function: Picture Handler --- #
async def handle_picture(update: Update, context: ContextTypes.DEFAULT_TYPE):
   # Handle provided picture
   await update.message.reply_text("به به چه عکس قشنگی! یکم بهم فرصت بده تا چهره تو درست آنالیز کنم!")
    
   file_id = update.message.photo[-1].file_id
   user_image_path = f"{PICTURES_DIR}/{file_id}_{TELEGRAM_BOT_ID}.jpg"
   picture_file = await context.bot.get_file(file_id)
   await picture_file.download_to_drive(user_image_path)
   
   verify_user_image(user_image_path)
   

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        HANDLE_GENDER : [MessageHandler(filters.TEXT, handle_gender)],
        HANDLE_PICTURE : [MessageHandler(filters.PHOTO & ~filters.COMMAND, handle_picture)]
    },
    fallbacks=[],
) 

app.add_handler(conv_handler) 

init_db()
app.run_polling()
    