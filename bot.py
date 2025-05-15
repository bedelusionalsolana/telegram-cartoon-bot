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

# Load env variables
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")

replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a photo, then reply with /rme to get memeified 🤓")

async def rme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    replied = update.message.reply_to_message
    if not replied or not replied.photo:
        await update.message.reply_text("Please reply to a photo with /rme.")
        return

    await update.message.reply_text("Generating your goofy cartoon... 🧠💥")

    try:
        # Get photo from Telegram
        file = await context.bot.get_file(replied.photo[-1].file_id)
        image_data = requests.get(file.file_path).content

        # Upload to ImgBB
        imgbb_response = requests.post(
            "https://api.imgbb.com/1/upload",
            params={"key": IMGBB_API_KEY},
            files={"image": image_data}
        )

        image_url = imgbb_response.json()["data"]["url"]

        # Send to Replicate SDXL model
        output = replicate_client.run(
            "stability-ai/sdxl",
            input={
                "prompt": "A dumb-looking, meme-style cartoon portrait with far-apart eyes, a distorted mouth, and rough sketch lines. Funny, derpy, colorful.",
                "image": image_url,
                "strength": 0.6,
                "guidance": 8
            }
        )

        await update.message.reply_photo(photo=output[0], caption="Here you go 🤡")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Start the bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("rme", rme))
print("🤖 Bot is running...")
app.run_polling()
