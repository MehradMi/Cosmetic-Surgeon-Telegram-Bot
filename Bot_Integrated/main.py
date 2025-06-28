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

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# ===============================

# Bot Phases
# TODO: Define bot phases here as needed
GREETINGS, GENDER = range(2)
# ===============================

# Telegram Bot's ID
TELEGRAM_BOT_ID = "@CosmeticSurgent_Bot"
# ===============================

# User Registration Status
NOT_REGISTERED = "کاربر ربات را شروع کرده است، اما هنوز فرم ثبت‌نام را کامل نکرده است!"
REGISTERED = "کاربر ربات را شروع کرده و فرم ثبت‌نام را به طور کامل پر کرده است."
# ===============================

# Function to handle data
def handle_data_and_database(context: ContextTypes.DEFAULT_TYPE,
                             column, data, registration_status):
   context.user_data['bot_id'] = BOT_ID
   context.user_data['registrations_status'] = registrations_status    
   context.user_data[column] = data    
   save_user_to_db(context.user_data)
# ===============================

# --- Bot Functions: Start Handler --- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Add user telegram id to the database
    user_telegram_id = update.message.from_user.id
    handle_data_and_database(context, 'telegram_id', user_telegra_id, NOT_REGISTERED)
# ===============================
   
# --- Bot Function: Greetings Handler --- # 
async def greet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Greet User
    await update.message.reply_text("سلام عزیزم من هوش مصنوعی کلینیک زیبایی ماهتا هستم میخوام کمکت کنم بفهمی شبیه کدوم سلبریتی هستی.")
# =============================== 

# --- Bot Function: Gender Handler --- #
async def gender(update: Update, context: Context.DEFAULT_TYPE):
    


app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        
    },
    fallbacks=[],
) 

app.add_handler(conv_handler) 

init_db()
app.run_polling()
    