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

# Load .env secrets
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")

replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a photo, then reply with /rme to get turned into a derpy meme 🤡")

async def rme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    replied = update.message.reply_to_message
    if not replied or not replied.photo:
        await update.message.reply_text("Please reply to a photo with /rme.")
        return

    await update.message.reply_text("Generating your goofy cartoon... 🧠💥")

    try:
        # Step 1: Download the Telegram image
        file = await context.bot.get_file(replied.photo[-1].file_id)
        image_data = requests.get(file.file_path).content

        # Step 2: Upload image to ImgBB
        imgbb_response = requests.post(
            "https://api.imgbb.com/1/upload",
            params={"key": IMGBB_API_KEY},
            files={"image": image_data}
        )
        image_url = imgbb_response.json()["data"]["url"]

        # Step 3: Use Replicate (img2img, correct model version)
        output = replicate_client.run(
            "stability-ai/stable-diffusion-img2img:15a3689ee13bd0216e988208eca3144c3abcd36672df0afec5b0feb1bd6087d",
            input={
                "image": image_url,
                "prompt": "A poorly drawn cartoon meme version of this person. Far-apart eyes, weird crooked smile, silly distorted proportions, sketchy and colorful.",
                "strength": 0.7,
                "guidance": 8
            }
        )

        await update.message.reply_photo(photo=output[0], caption="Here you go 🤡")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Launch the bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("rme", rme))
print("🤖 Bot is live!")
app.run_polling()
