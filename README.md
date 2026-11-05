# 📸 Instagram Media Downloader Telegram Bot

An ad-free, lightweight Telegram bot that automatically downloads high-resolution photos, videos, reels, and carousel posts directly from Instagram links.

---

## ✨ Features

- 🖼️ **Single & Carousel Photos:** Downloads full-resolution images.
- 🎥 **Reels & Videos:** Downloads high-quality video files directly.
- 🎠 **Carousel Posts:** Automatically extracts and sends all items (photos and videos) from multi-slide posts.
- ⚡ **Ad-Free & Private:** Run your own personal instance without third-party popups or trackers.
- 🤖 **Telegram Commands:** Includes built-in support for `/start` and `/help`.
- ☁️ **Cloud Ready:** Formatted for easy 24/7 deployment on Render or Heroku.

---

## 📁 Project Structure

```text
ig-telegram-bot/
├── bot.py             # Main application logic & handlers
├── requirements.txt   # Python dependencies
├── Procfile           # Process file for Render/Heroku background worker
├── .gitignore         # Prevents committing secrets & cache files
└── README.md          # Documentation
