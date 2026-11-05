import os
import re
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import instaloader
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# 1. DUMMY WEB SERVER TO KEEP RENDER'S FREE WEB SERVICE HAPPY
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

    def log_message(self, format, *args):
        return  # Silences HTTP log noise in terminal

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# Runs the web server in a background thread
threading.Thread(target=run_health_check_server, daemon=True).start()


# 2. INSTALOADER & BOT LOGIC
loader = instaloader.Instaloader(
    download_videos=True,
    download_video_thumbnails=False,
    download_comments=False,
    save_metadata=False,
)

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
        "3. Wait a few seconds for the media file to arrive."
    )

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

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_link))

    print("Bot is running...")
    app.run_polling()