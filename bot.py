import os
import requests
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

# Load .env
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")

replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a photo, then reply to it with /rme to get memeified 🤓")

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

        # Upload image to ImgBB
        imgbb_response = requests.post(
            "https://api.imgbb.com/1/upload",
            params={"key": IMGBB_API_KEY},
            files={"image": image_data}
        )
        image_url = imgbb_response.json()["data"]["url"]

        # Run image-to-image model on Replicate
        output = replicate_client.run(
            "stability-ai/stable-diffusion-img2img",
            input={
                "prompt": "A distorted meme-style cartoon version of this person, with far-apart eyes, a weird mouth, sketchy art, dumb expression. Colorful and derpy.",
                "image": image_url,
                "strength": 0.6,
                "guidance": 8
            }
        )

        await update.message.reply_photo(photo=output[0], caption="Here you go 🤡")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Launch bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("rme", rme))
print("🤖 Bot is live!")
app.run_polling()
