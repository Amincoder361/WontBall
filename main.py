
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ChatMemberStatus

# تنظیمات ربات
BOT_TOKEN = "8444027589:AAG1H48viBP6dFajmiKY1ZrhRmubLl-e684"  # توکن ربات خود را اینجا قرار دهید
ADMIN_ID = 6651180345
CHANNEL_ID = "-1002546069051"  # ID عددی کانال
CHANNEL_LINK = "https://t.me/+Nt-iXiZiddc2NmU0"
BOT_LINK = "https://t.me/TheTopRange_bot"

# وضعیت‌های مختلف ربات
USER_STATES = {}
POSTS_DATA = {}  # ذخیره اطلاعات پست‌ها
POST_COUNTER = 0  # شمارنده پست‌ها

# فعال‌سازی لاگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

class BotStates:
    IDLE = "idle"
    WAITING_MEDIA = "waiting_media"
    WAITING_MUSIC = "waiting_music"
    WAITING_LINK = "waiting_link"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # بررسی اینکه آیا کاربر ادمین است یا خیر
    if user_id == ADMIN_ID:
        USER_STATES[user_id] = BotStates.WAITING_MEDIA
        await update.message.reply_text("سلام لطفا برای شروع پست را ارسال کنید :")
    else:
        # بررسی عضویت در کانال برای کاربران عادی
        try:
            member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
            if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                # کاربر عضو کانال است - ارسال موزیک
                if str(user_id) in POSTS_DATA:
                    post_data = POSTS_DATA[str(user_id)]
                    if 'music' in post_data:
                        await context.bot.send_audio(
                            chat_id=user_id,
                            audio=post_data['music']
                        )
                    else:
                        await update.message.reply_text("متاسفانه موزیک این پست در دسترس نیست.")
                else:
                    await update.message.reply_text("لطفا ابتدا روی دکمه Download Music🎵 کلیک کنید.")
            else:
                # کاربر عضو کانال نیست
                keyboard = [[InlineKeyboardButton("TheTopRange", url=CHANNEL_LINK)]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    "لطفا در کانال های زیر عضو شید و هروقت عضو شدید دوباره ربات را استارت کنید و دانلود موزیک را بزنید.",
                    reply_markup=reply_markup
                )
        except Exception as e:
            print(f"خطا در بررسی عضویت: {e}")
            keyboard = [[InlineKeyboardButton("TheTopRange", url=CHANNEL_LINK)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "لطفا در کانال های زیر عضو شید و هروقت عضو شدید دوباره ربات را استارت کنید و دانلود موزیک را بزنید.",
                reply_markup=reply_markup
            )

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # فقط ادمین می‌تواند مدیا ارسال کند
    if user_id != ADMIN_ID:
        return
    
    if USER_STATES.get(user_id) == BotStates.WAITING_MEDIA:
        if update.message.photo or update.message.video:
            # ذخیره مدیا
            if str(user_id) not in POSTS_DATA:
                POSTS_DATA[str(user_id)] = {}
            
            if update.message.photo:
                POSTS_DATA[str(user_id)]['media'] = update.message.photo[-1].file_id
                POSTS_DATA[str(user_id)]['media_type'] = 'photo'
            else:
                POSTS_DATA[str(user_id)]['media'] = update.message.video.file_id
                POSTS_DATA[str(user_id)]['media_type'] = 'video'
            
            USER_STATES[user_id] = BotStates.WAITING_MUSIC
            await update.message.reply_text("لطفا آهنگ پست را ارسال کنید :")
        else:
            await update.message.reply_text("لطفا فقط عکس یا ویدیو ارسال کنید.")

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # فقط ادمین می‌تواند آهنگ ارسال کند
    if user_id != ADMIN_ID:
        return
    
    if USER_STATES.get(user_id) == BotStates.WAITING_MUSIC:
        if update.message.audio or update.message.voice:
            # ذخیره آهنگ
            if update.message.audio:
                POSTS_DATA[str(user_id)]['music'] = update.message.audio.file_id
            else:
                POSTS_DATA[str(user_id)]['music'] = update.message.voice.file_id
            
            USER_STATES[user_id] = BotStates.WAITING_LINK
            await update.message.reply_text("لطفا لینک پست را ارسال کنید :")
        else:
            await update.message.reply_text("لطفا فقط آهنگ ارسال کنید.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global POST_COUNTER
    user_id = update.effective_user.id
    
    # فقط ادمین می‌تواند لینک ارسال کند
    if user_id != ADMIN_ID:
        return
    
    if USER_STATES.get(user_id) == BotStates.WAITING_LINK:
        # ذخیره لینک
        POSTS_DATA[str(user_id)]['link'] = update.message.text
        
        # افزایش شمارنده پست‌ها
        POST_COUNTER += 1
        
        # ارسال پست به کانال
        try:
            post_data = POSTS_DATA[str(user_id)]
            
            # متن پست با لینک
            caption = f"""New Post!🧡🤝

[Click to view post]({post_data['link']})

`Code : {POST_COUNTER}`

@TheTopRange"""
            
            # دکمه دانلود موزیک
            keyboard = [[InlineKeyboardButton("Download Music🎵", callback_data=f"download_{user_id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # ارسال به کانال
            if post_data['media_type'] == 'photo':
                await context.bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=post_data['media'],
                    caption=caption,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            else:
                await context.bot.send_video(
                    chat_id=CHANNEL_ID,
                    video=post_data['media'],
                    caption=caption,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            
            # بازنشانی وضعیت
            USER_STATES[user_id] = BotStates.IDLE
            await update.message.reply_text(f"ارسال شد✅️\nکد پست: {POST_COUNTER}")
            
        except Exception as e:
            print(f"خطا در ارسال پست: {e}")
            await update.message.reply_text("خطا در ارسال پست. لطفا دوباره تلاش کنید.")

async def handle_download_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(url=BOT_LINK)
    
    user_id = query.from_user.id
    callback_data = query.data
    
    if callback_data.startswith("download_"):
        admin_id = callback_data.split("_")[1]
        
        # بررسی عضویت در کانال
        try:
            member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
            if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                # کاربر عضو کانال است - ارسال موزیک
                if admin_id in POSTS_DATA and 'music' in POSTS_DATA[admin_id]:
                    # ارسال موزیک به صورت خصوصی
                    await context.bot.send_audio(
                        chat_id=user_id,
                        audio=POSTS_DATA[admin_id]['music']
                    )
                else:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="متاسفانه موزیک این پست در دسترس نیست."
                    )
            else:
                # کاربر عضو کانال نیست
                keyboard = [[InlineKeyboardButton("TheTopRange", url=CHANNEL_LINK)]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await context.bot.send_message(
                    chat_id=user_id,
                    text="لطفا در کانال های زیر عضو شید و هروقت عضو شدید دوباره ربات را استارت کنید و دانلود موزیک را بزنید.",
                    reply_markup=reply_markup
                )
        except Exception as e:
            print(f"خطا در بررسی عضویت: {e}")
            keyboard = [[InlineKeyboardButton("TheTopRange", url=CHANNEL_LINK)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=user_id,
                text="لطفا در کانال های زیر عضو شید و هروقت عضو شدید دوباره ربات را استارت کنید و دانلود موزیک را بزنید.",
                reply_markup=reply_markup
            )

async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # اگر کاربر ادمین نیست، هیچ پاسخی نده
    if user_id != ADMIN_ID:
        return
    
    # اگر ادمین چیز غلطی فرستاده
    if USER_STATES.get(user_id) == BotStates.WAITING_MEDIA:
        await update.message.reply_text("لطفا فقط عکس یا ویدیو ارسال کنید.")
    elif USER_STATES.get(user_id) == BotStates.WAITING_MUSIC:
        await update.message.reply_text("لطفا فقط آهنگ ارسال کنید.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    application.add_handler(MessageHandler(filters.AUDIO | filters.VOICE, handle_audio))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CallbackQueryHandler(handle_download_callback))
    application.add_handler(MessageHandler(filters.ALL, handle_other_messages))
    
    print("ربات شروع به کار کرد...")
    application.run_polling()

if __name__ == '__main__':
    main()
