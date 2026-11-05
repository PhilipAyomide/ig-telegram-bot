import os
import re
import instaloader
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Initialize Instaloader with video support enabled
loader = instaloader.Instaloader(
    download_videos=True,
    download_video_thumbnails=False,
    download_comments=False,
    save_metadata=False
)

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    # Extract shortcode for posts, reels, or carousels
    match = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', text)
    
    if not match:
        await update.message.reply_text("Please send a valid Instagram post or reel link.")
        return

    msg = await update.message.reply_text("Fetching media...")
    shortcode = match.group(1)
    
    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        
        # 1. Carousel posts (multiple images/videos)
        if post.typename == 'GraphSidecar':
            for node in post.get_sidecar_nodes():
                if node.is_video:
                    await update.message.reply_video(video=node.video_url)
                else:
                    await update.message.reply_photo(photo=node.display_url)
        # 2. Single Video or Reel
        elif post.is_video:
            await update.message.reply_video(video=post.video_url)
        # 3. Single Photo
        else:
            await update.message.reply_photo(photo=post.url)
            
        await msg.delete()
    except Exception as e:
        await update.message.reply_text(f"Error downloading media: {e}")

if __name__ == '__main__':
    # Make sure to put your actual BotFather token here for local testing
    TOKEN = os.getenv("BOT_TOKEN", "9204076637:AAG3hHEe3eJ3swNM-N97-tRQA9GOgCypvLE")
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_link))
    print("Bot is starting locally...")
    app.run_polling()