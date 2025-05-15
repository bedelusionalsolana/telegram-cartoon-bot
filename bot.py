import os
import requests
from io import BytesIO
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
import replicate

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a photo, then reply to it with /rme to make a goofy cartoon 🤡")

async def rme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    replied = update.message.reply_to_message
    if not replied or not replied.photo:
        await update.message.reply_text("Please reply to a photo with /rme.")
        return

    await update.message.reply_text("Making you dumb and meme-worthy... 🧠💥")

    try:
        # Download the photo
        file = await context.bot.get_file(replied.photo[-1].file_id)
        image_data = requests.get(file.file_path).content
        with open("input.jpg", "wb") as f:
            f.write(image_data)

        # Run meme model on Replicate
        output_url = replicate_client.run(
            "cjwbw/stable-diffusion-meme",  # ✅ no version hash
            input={
                "image": open("input.jpg", "rb"),
                "caption": "make this person look dumb, weird, derpy, and meme-like in a sketchy cartoon style"
            }
        )

        await update.message.reply_photo(photo=output_url, caption="here you go 🤡")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Set up bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("rme", rme))
print("🤖 Bot is live!")
app.run_polling()
