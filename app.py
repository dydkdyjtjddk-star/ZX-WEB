import os
import random
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "8926793236:AAEL4D0k9mhNMtYo7z71PwURS2bKN8W0CXU"

# Predefined popular video keys — yt-dlp এগুলো থেকে র‍্যান্ডম নেবে
VIDEO_KEYS = [
    "ph5ef5c3e3c4f8a",
    "ph5ef5c3e3c4f8b",
    "ph60c3e3c4f8a12",
    "ph61b2a3c4d5e6f",
    "ph62a1b2c3d4e5f",
]

def get_random_video_url():
    """yt-dlp দিয়ে pornhub সার্চ পেজ থেকে র‍্যান্ডম ভিডিও নাও"""
    
    search_queries = [
        "ytsearch3:site:pornhub.com hot",
        "ytsearch3:site:pornhub.com trending",
        "ytsearch3:site:pornhub.com best",
    ]
    
    # pornhub playlist/category URL
    category_urls = [
        "https://www.pornhub.com/video?o=mv&t=w",  # most viewed this week
        "https://www.pornhub.com/video?o=tr&t=w",  # top rated this week  
        "https://www.pornhub.com/video?o=ht",       # hot
    ]
    
    return random.choice(category_urls)


def download_random_video(user_id: int):
    """yt-dlp দিয়ে র‍্যান্ডম ভিডিও ডাউনলোড"""
    os.makedirs("downloads", exist_ok=True)
    
    category_urls = [
        "https://www.pornhub.com/video?o=mv&t=w",
        "https://www.pornhub.com/video?o=tr&t=w",
        "https://www.pornhub.com/video?o=ht",
    ]
    
    url = random.choice(category_urls)
    output_path = f"downloads/{user_id}_%(title)s.%(ext)s"
    
    ydl_opts = {
        "outtmpl": output_path,
        "format": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]/best",
        "merge_output_format": "mp4",
        "quiet": False,
        "playliststart": random.randint(1, 15),  # র‍্যান্ডম পজিশন
        "playlistend": random.randint(16, 20),
        "max_downloads": 1,                       # শুধু ১টা
        "ignoreerrors": True,
        "socket_timeout": 30,
        "retries": 3,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.pornhub.com/",
        },
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        
        # playlist হলে প্রথম ভিডিও নাও
        if "entries" in info:
            for entry in info["entries"]:
                if entry:
                    info = entry
                    break
        
        title = info.get("title", "Hot Video")
        filename = ydl.prepare_filename(info)
        if not filename.endswith(".mp4"):
            filename = filename.rsplit(".", 1)[0] + ".mp4"
        
        return filename, title


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔥 Video Hot", callback_data="video_hot")]]
    await update.message.reply_text(
        "👋 স্বাগতম!\n🔥 বাটন চাপো — অটো ভিডিও পাবে!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# বাটন
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("🔥 লোড হচ্ছে...")

    msg = await query.message.reply_text("⬇️ ভিডিও আনা হচ্ছে...")

    try:
        user_id = query.from_user.id
        filename, title = download_random_video(user_id)

        await msg.edit_text("📤 পাঠানো হচ্ছে...")

        keyboard = [[InlineKeyboardButton("🔥 আরেকটা Video Hot", callback_data="video_hot")]]

        with open(filename, "rb") as vf:
            await query.message.reply_video(
                video=vf,
                caption=f"🔥 {title}",
                supports_streaming=True,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        os.remove(filename)
        await msg.delete()

    except Exception as e:
        keyboard = [[InlineKeyboardButton("🔄 আবার চেষ্টা", callback_data="video_hot")]]
        await msg.edit_text(
            f"❌ এরর হয়েছে। আবার চেষ্টা করো।",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        print(f"এরর: {e}")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="video_hot"))
    print("🔥 বট চালু...")
    app.run_polling()


if __name__ == "__main__":
    main()