# Import Needed Modules 
import json
import sys, os
import requests
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from telegram import (Update, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, KeyboardButton)

from telegram.ext import (ApplicationBuilder, CommandHandler,
                          MessageHandler, filters,
                          ConversationHandler, ContextTypes)

from database_integrated import init_db, save_user_to_db

# Importing OpenAI Modules 
from verify_user_image import verify_user_image
from find_similar_celebrities import find_similar_celebrities
from search_for_image import search_valid_celebrity_image
from search_for_image import get_celebrity_image_url
from surgery_suggestions import surgery_suggestions 
# ===============================

# Load TELEGRAM_BOT_TOKEN from .env file
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# ===============================

# Bot Phases
# TODO: Define bot phases here as needed
HANDLE_GENDER, HANDLE_PICTURE, HANDLE_CHOSEN_PERSON,
HANDLE_USER_SENT_TARGET_IMAGE, HANDLE_WISH_TO_CONTINUE, 
HANDLE_LAST_YES_OR_NO, 
HANDLE_FIRSTNAME, HANDLE_LASTNAME, HANDLE_PHONE, HANDLE_CITY, HANDLE_SHARE_THIS_BOT = range(11)
# ===============================

# Telegram Bot's ID
TELEGRAM_BOT_ID = "@CosmeticSurgent_Bot"
# ===============================

# Error Cheking Variables
BAD_IMAGE_ERROR_COUNT = 0
NOT_FOUND_CELEBRITY_ERROR_COUNT = 0
# =============================== 

# User Registration Status
NOT_REGISTERED = "کاربر ربات را شروع کرده است، اما هنوز فرم ثبت‌نام را کامل نکرده است!"
REGISTERED = "کاربر ربات را شروع کرده و فرم ثبت‌نام را به طور کامل پر کرده است."
# ===============================

# Directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PICTURES_DIR = os.path.join(BASE_DIR, 'static', 'pictures')
TARGET_PERSON_PICTURES_DIR = os.path.join(BASE_DIR, 'static', 'target_person_pictures')
# ================================

# --- Function: Handles and Stores Data --- #
def handle_data_and_database(context: ContextTypes.DEFAULT_TYPE,
                             column, data, registration_status):
   context.user_data['bot_id'] = TELEGRAM_BOT_ID
   context.user_data['registration_status'] = registration_status    
   context.user_data[column] = data    
   save_user_to_db(context.user_data)
# ===============================

# --- Bot Functions: Start Handler --- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Stage 1: Take user telegram id and insert it into the database
    user_telegram_id = update.message.from_user.id
    handle_data_and_database(context, 'telegram_id', user_telegram_id, NOT_REGISTERED)
    # ----------------------------
    
    # Stage 2: Call the function responsible for greeting the user
    return await greet(update, context)
    # ----------------------------
# ===============================
   
# --- Bot Function: Greet User --- # 
async def greet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Stage 1: Greet The User
    await update.message.reply_text("سلام عزیزم من هوش مصنوعی کلینیک زیبایی ماهتا هستم میخوام کمکت کنم بفهمی شبیه کدوم سلبریتی هستی.")
    # ----------------------------
    
    # Stage 2: Get User's Gender
    return await get_user_gender(update, context)
    # ----------------------------
# =============================== 

# --- Bot Function: Get User Gender --- #
async def get_user_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    # Stage 1: Take gender and insert it into the database
    gender = update.message.text
    handle_data_and_database(context, 'gender', gender, NOT_REGISTERED)
    # ----------------------------
    
    # Stage 2: Get User Picture
    return await get_user_picture(update, context)
    # ----------------------------
# ===============================

# --- Bot Function: Get User's Picture --- #
async def get_user_picture(update:Update, context: ContextTypes.DEFAULT_TYPE):
    # Stage 1: Ask user to send a picture of themselves
    await update.message.reply_text("خب! حالا یه عکس واضح از صورتت بهم بده. لطفا یه عکس واضح از رو به رو بدون آرایش غلیظ و عینک باشه. نور کافی هم داشته باشه!",
                                    reply_markup=ReplyKeyboardRemove())
    # ----------------------------
    
    # Stage 2: Send an example image
    # ----------------------------
    
    # Stage 3: Conversation Handler Will Call handle_picture 
    return HANDLE_PICTURE
    # ----------------------------
# ===============================

# --- Bot Function: Throw an error and Get User's Picture Again --- #
async def picture_error(update:Update, context: ContextTypes.DEFAULT_TYPE, user_bad_image_path):
           await update.message.reply_text("عزیزم مگه نمیخوای کمکت کنم؟ لطفا عکست رو با مشخصاتی که گفتم دقیق برام بفرست.")
           os.remove(user_bad_image_path)
           
           return HANDLE_PICTURE
# ===============================  

# --- Bot Function: Picture Handler --- #
async def handle_picture(update: Update, context: ContextTypes.DEFAULT_TYPE):
   # Handle provided picture
   global BAD_IMAGE_ERROR_COUNT
   if BAD_IMAGE_ERROR_COUNT == 0:
       await update.message.reply_text("به به چه عکس قشنگی! یکم بهم فرصت بده تا چهره تو درست آنالیز کنم!")
    
   file_id = update.message.photo[-1].file_id
   user_image_path = f"{PICTURES_DIR}/{file_id}_{TELEGRAM_BOT_ID}.jpg"
   picture_file = await context.bot.get_file(file_id)
   await picture_file.download_to_drive(user_image_path)
   # ----------------------------

   # Call verify_user_image function (OpenAI Module)
   verification = verify_user_image(user_image_path)
   # ----------------------------
   
   if BAD_IMAGE_ERROR_COUNT == 0 and verification != "OK":
       BAD_IMAGE_ERROR_COUNT += 1
       return await picture_error(update, context, user_image_path)
   else:
       handle_data_and_database(context, 'user_photo', file_id, NOT_REGISTERED)
       return await find_similar_celebs(update, context)
    
# --- Bot Function: Finds Similar Looking Celebrities --- #
async def find_similar_celebs(update: Update, context: ContextTypes.DEFAULT_TYPE):
   file_id = context.user_data['user_photo'] 
   user_image_path = f"{PICTURES_DIR}/{file_id}_{TELEGRAM_BOT_ID}.jpg" 
   user_gender_en = None
   if context.user_data['gender'] == "آقا":
       user_gender_en = "Male"
   else:
       user_gender_en = "Female"

   #  
   similar_celebrities = find_similar_celebrities(user_image_path, user_gender_en)

   global NOT_FOUND_CELEBRITY_ERROR_COUNT  
   if NOT_FOUND_CELEBRITY_ERROR_COUNT == 4:
       return stop(update, context)
   elif similar_celebrities == "NOT FOUND" and NOT_FOUND_CELEBRITY_ERROR_COUNT < 5:
       await update.message.reply_text("متاسفم نتونستم سلبریتی های مناسبی پیدا کنم. الان دوباره تلاش میکنم لطفا یکم دیگه صبر کن!")
       NOT_FOUND_CELEBRITY_ERROR_COUNT += 1
       return await find_similar_celebs(update, context) 
   
   handle_data_and_database(context, 'similar_celebrities', f"{similar_celebrities}".replace("\\u200c", " "), NOT_REGISTERED)
   
   await update.message.reply_text(
       json.dumps(similar_celebrities, ensure_ascii=False)
       ) 
   
   return await search_celebrity_image(update, context, similar_celebrities)
# ================================
       
# --- Bot Function: Search For Celebrity Image --- #
async def search_celebrity_image(update: Update, context: ContextTypes.DEFAULT_TYPE, similar_celebrities):
    file_id = context.user_data['user_photo']
    user_image_path = f"{PICTURES_DIR}/{file_id}_{TELEGRAM_BOT_ID}.jpg" 

    celebrity_image_url_dict = {}
    for celebrity in similar_celebrities:
        try:
            lang="en"
            if is_persian_name(celebrity["name"]):
                lang="fa"
            celebrity_image_url = get_celebrity_image_url(celebrity["name"], lang)
            celebrity_image_url_dict[celebrity["name"]] = celebrity_image_url
            await send_images_side_by_side(update, context, user_image_path, celebrity_image_url)
        except Exception as e:
            pass
    
    context.user_data['celebrity_image_urls'] = celebrity_image_url_dict
    return await select_person_to_look_like(update, context, similar_celebrities)
# ================================

# --- Bot Function: Send Back User & Celebrity Images --- #
async def send_images_side_by_side(update: Update, context: ContextTypes.DEFAULT_TYPE, user_image_path, celebrity_image_url):
    try:
        # Step 1: Load user photo from file
        user_image = Image.open(user_image_path).convert("RGB")
        # ----------------------------

        # Step 2: Download celebrity image
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; TelegramBot/1.0; +https://yourdomain.com/)"
        }
        response = requests.get(celebrity_image_url, headers=headers)
        response.raise_for_status()
        celeb_image = Image.open(BytesIO(response.content)).convert("RGB")
        # ----------------------------

        # Step 3: Resize both to same height
        target_height = 512
        user_image = user_image.resize((int(user_image.width * target_height / user_image.height), target_height))
        celeb_image = celeb_image.resize((int(celeb_image.width * target_height / celeb_image.height), target_height))
        # ----------------------------

        # Step 4: Create side-by-side image
        total_width = user_image.width + celeb_image.width
        combined = Image.new("RGB", (total_width, target_height))
        combined.paste(user_image, (0, 0))
        combined.paste(celeb_image, (user_image.width, 0))
        # ----------------------------

        # Step 5: Save and send
        combined_path = "comparison.jpg"
        combined.save(combined_path)

        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(combined_path, "rb"),
            #caption=f"👥 {caption}"
            caption="👥 Your Face vs Celebrity Match"
        )
        # ----------------------------

    except Exception as e:
        await update.message.reply_text(f"⚠️ Could not create comparison: {e}")  
# ================================

# --- Bot Function: Select Desired Celebrity --- #
async def select_person_to_look_like(update: Update, context: ContextTypes.DEFAULT_TYPE, similar_celebrities):
    keyboard = [
        [KeyboardButton(similar_celebrities[0]["name"])],
        [KeyboardButton(similar_celebrities[1]["name"])],
        [KeyboardButton(similar_celebrities[2]["name"])],
        [KeyboardButton(similar_celebrities[3]["name"])],
        [KeyboardButton("خودم عکسش رو اضافه می‌کنم.")]
    ]
    await update.message.reply_text("اگه بخوای یکی رو انتخاب کنی که شبیهش بشی کدوم رو انتخاب میکنی؟",
                                    reply_markup=ReplyKeyboardMarkup(keyboard,
                                                                     one_time_keyboard=True,
                                                                     resize_keyboard=True))
    return HANDLE_CHOSEN_PERSON
# ================================

# --- Bot Function: Chosen Person Handler --- #
async def handle_chosen_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    celeb_name=""
    if update.message.text == "خورم عکسش رو اضافه می‌کنم.":
        await update.message.reply_text("خیلی هم عالی. عکس مورد نظرت رو برام بفرست پس!",
                                        reply_markup=ReplyKeyboardRemove())
        return HANDLE_USER_SENT_TARGET_IMAGE 
    else:  
        celeb_name = update.message.text
        handle_data_and_data_base(context, 'celeb_name', celeb_name, NOT_REGISTERED)
        await update.message.reply_text(f"ای باهوش! اتفاقا خیلی انتخاب خوبی کردی. میخوای بهت بگم با چه تغییراتی میتونی به {celeb_name} شبیه بشی؟",
                                        reply_markup=ReplyKeyboardMarkup(keyboard,
                                                                         one_time_keyboard=True,
                                                                         resize_keyboard=True))
        return HANDLE_WISH_TO_CONTINUE    
# ================================

# --- Bot Function: Handle User Sent Target Image --- #
async def handle_user_sent_target_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle user-provided target image
    file_id = update.message.photo[-1].file_id
    target_image_path = f"{TARGET_PERSON_PICTURES_DIR}/{file_id}_{TELEGRAM_BOT_ID}.jpg"
    picture_file = await context.bot.get_file(file_id)
    await picture_file.download_to_drive(target_image_path)
    
    # Store the target image info
    handle_data_and_database(context, 'user_target_photo', file_id, NOT_REGISTERED)
    
    keyboard = [
        [KeyboardButton("بله")],
        [KeyboardButton("خیر")]
    ]
    
    await update.message.reply_text("عکس رو گرفتم! میخوای بهت بگم با چه تغییراتی میتونی به این شخص شبیه بشی؟",
                                    reply_markup=ReplyKeyboardMarkup(keyboard,
                                                                     one_time_keyboard=True,
                                                                     resize_keyboard=True))
    return HANDLE_WISH_TO_CONTINUE
# ================================

# --- Bot Function: Wish To Continue Handler --- #
async def handle_wish_to_continue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("بله")],
        [KeyboardButton("خیر")]
    ]
    if update.message.text == "خیر":
        await update.message.reply_text("میخوای برات یه وقت مشاوره رایگان برای نغییرات زیبایی بگیرم؟",
                                        reply_markup=ReplyKeyboardMarkup(keyboard,
                                                                         one_time_keyboard=True,
                                                                         resize_keyboard=True))
        return HANDLE_LAST_YES_OR_NO
    elif update.message.text == "بله":
        return # TODO: take user's info
# ================================

# --- Bot Function: Last Yes Or No Handler --- #
async def handle_last_yes_or_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "خیر":
        # If "NO": Go to the bot's last state and end conversation
        return HANDLE_SHARE_THIS_BOT 
    elif update.message.text == "بله":
        # If "Yes": Take user information
        return HANDLE_FIRSTNAME
# ================================

# --- Bot Function: Share This Bot Please Handler --- #
async def handle_share_this_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("این هوش مصنوعی رو برای دوستات بفرست و به چالش شبیه کدوم سلبریتی هستی دعوتشون کن.")
    return ConversationHandler.END
# ================================

# --- Bot Function: Take User Information Handler --- #
async def take_user_information(update: Update, context: ContextTypes.DEFAULT_TYPE): 
# ================================

# --- Bot Function: Surgery Suggestions Handler --- #
#async def give_surgery_suggestions(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Retrieve user_image_path And celebrity_image_url, Then Call surgery_suggestions functions (OpenAI Module) We fetch and store the suggestions but we don't just hand it to user yet :)
        file_id = context.user_data['user_photo']
        user_image_path = f"{PICTURES_DIR}/{file_id}_{TELEGRAM_BOT_ID}.jpg" 
        celebrity_image_url = context.user_data['celebrity_image_urls'].get(celeb_name)
        suggestions = surgery_suggestions(user_image_path, celebrity_image_url)
        # ----------------------------
    
    # Save suggestions to database
    handle_data_and_data_base(context, 'surgery_suggestions', suggestions, NOT_REGISTERED)
    # ----------------------------
    
# ================================

# --- Bot Function: Stop The Bot From Progressing Any Furthur --- #
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ربات متوقف شد." \
    "\nلطفاً برای شروع مجدد ربات، روی دکمه «start» از منو کلیک کنید.")

    # Reset the *_ERROR_COUNT variables to 0
    global BAD_IMAGE_ERROR_COUNT, NOT_FOUND_CELEBRITY_ERROR_COUNT
    BAD_IMAGE_ERROR_COUNT = 0
    NOT_FOUND_CELEBRITY_ERROR_COUNT = 0
   # ----------------------------

    return ConversationHandler.END
# ================================

# --- Function: Detects Whether The Name Is Persian --- #
def is_persian_name(name):
    return any('\u0600' <= c <= '\u06FF' for c in name)
# ================================

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        HANDLE_GENDER : [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gender)],
        HANDLE_PICTURE : [MessageHandler(filters.PHOTO & ~filters.COMMAND, handle_picture)],
        HANDLE_CHOSEN_PERSON: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_chosen_person)],
        HANDLE_USER_SENT_TARGET_IMAGE: [MessageHandler(filters.PHOTO & ~filters.COMMAND, handle_user_sent_targer_image)],
        HANDLE_WISH_TO_CONTINUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wish_to_continue)],
        HANDLE_LAST_YES_OR_NO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_last_yes_or_no)],
        HANDLE_SHARE_THIS_BOT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_share_this_bot)]
    },
    fallbacks=[
        CommandHandler("start", start),
        CommandHandler("stop", stop)
    ]
) 

app.add_handler(conv_handler) 

init_db()
app.run_polling()
    