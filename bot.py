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

# Load secrets
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")

replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a photo, then reply to it with /rme to get DERPIFIED 🤪")

async def rme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    replied = update.message.reply_to_message
    if not replied or not replied.photo:
        await update.message.reply_text("Please reply to a photo with /rme.")
        return

    await update.message.reply_text("Drawing your derpy masterpiece... 🎨🧠")

    try:
        # Step 1: Download photo from Telegram
        file = await context.bot.get_file(replied.photo[-1].file_id)
        image_data = requests.get(file.file_path).content

        # Step 2: Upload image to ImgBB to get public URL
        imgbb_response = requests.post(
            "https://api.imgbb.com/1/upload",
            params={"key": IMGBB_API_KEY},
            files={"image": image_data}
        )
        image_url = imgbb_response.json()["data"]["url"]

        # Step 3: Send image to Replicate img2img model with derpy prompt
        output = replicate_client.run(
            "stability-ai/stable-diffusion-img2img",
            input={
                "prompt": "A distorted cartoon meme version of this person. Weird face, far-apart eyes, dumb expression, glitchy or sketchy art. Derpy and hilarious.",
                "image": image_url,
                "strength": 0.7,
                "guidance": 7
            }
        )

        await update.message.reply_photo(photo=output[0], caption="Here you go, derp god 🤡")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Run the bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("rme", rme))
print("🤖 Bot is live!")
app.run_polling()
