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

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
REPLICATE_TOKEN = os.getenv("REPLICATE_API_TOKEN")
replicate.Client(api_token=REPLICATE_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a photo, then reply to it with /rme to make a dumb cartoon 🤪")

async def rme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if reply to a photo
    replied = update.message.reply_to_message
    if not replied or not replied.photo:
        await update.message.reply_text("Please reply to an image with /rme.")
        return

    await update.message.reply_text("Making you dumb and meme-worthy... 🧠💥")

    # Download photo
    file = await context.bot.get_file(replied.photo[-1].file_id)
    photo_data = requests.get(file.file_path).content

    with open("temp_input.jpg", "wb") as f:
        f.write(photo_data)

    # Send to Replicate
    try:
        output = replicate.run(
            "cjwbw/stable-diffusion-meme:2609c6b0886cf07198db50d3a04efed4c00dba38c6c6f24e00d4d4c4a6f7a5f0",
            input={
                "image": open("temp_input.jpg", "rb"),
                "caption": "make this person look dumb, weird, and meme-like in a sketchy cartoon style"
            }
        )
        await update.message.reply_photo(photo=output, caption="here you go 🤡")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Run bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("rme", rme))
print("🤖 Bot is live!")
app.run_polling()
