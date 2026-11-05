import os
import re
import instaloader
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

loader = instaloader.Instaloader(
    download_videos=True,
    download_video_thumbnails=False,
    download_comments=False,
    save_metadata=False,
)

# 1. Command Handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"Hi {user_name}! 👋\nSend me any Instagram post, reel, or carousel link, and I will download the high-res media for you."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 **How to use this bot:**\n"
        "1. Open Instagram and copy a post or Reel link.\n"
        "2. Paste the link directly into this chat.\n"
        "3. Wait a few seconds for the photo or video file to arrive."
    )

# 2. Link Handler
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    match = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', text)

    if not match:
        await update.message.reply_text("Please send a valid Instagram post or reel link.")
        return

    msg = await update.message.reply_text("Fetching media...")
    shortcode = match.group(1)

    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        if post.typename == 'GraphSidecar':
            for node in post.get_sidecar_nodes():
                if node.is_video:
                    await update.message.reply_video(video=node.video_url)
                else:
                    await update.message.reply_photo(photo=node.display_url)
        elif post.is_video:
            await update.message.reply_video(video=post.video_url)
        else:
            await update.message.reply_photo(photo=post.url)

        await msg.delete()
    except Exception as e:
        await update.message.reply_text(f"Error downloading media: {e}")

if __name__ == '__main__':
    TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

    app = ApplicationBuilder().token(TOKEN).build()

    # Register command handlers (e.g. /start, /help)
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    # Register general text handler for IG links (ignores commands via ~filters.COMMAND)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_link))

    print("Bot is running...")
    app.run_polling()