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

# Load environment
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a photo, then reply to it with /rme to get derpified 🤓")

async def rme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    replied = update.message.reply_to_message
    if not replied or not replied.photo:
        await update.message.reply_text("Please reply to an image with /rme.")
        return

    await update.message.reply_text("Drawing your dumbass cartoon... 🧠💥")

    try:
        # Save the image
        file = await context.bot.get_file(replied.photo[-1].file_id)
        image_data = requests.get(file.file_path).content
        with open("input.jpg", "wb") as f:
            f.write(image_data)

        # Upload image to an image host so Replicate can use it (Replicate requires a URL)
        response = requests.post("https://api.imgbb.com/1/upload", params={
            "key": "YOUR_IMGBB_API_KEY"  # optional if you want to self-host
        }, files={"image": image_data})
        image_url = response.json()['data']['url']

        # Send to Replicate
        output = replicate_client.run(
            "stability-ai/sdxl",
            input={
                "prompt": "A badly drawn cartoon version of the input photo, meme style, distorted and sketchy, with far-apart eyes, silly expression, rough art",
                "image": image_url,
                "strength": 0.6,
                "guidance": 7
            }
        )

        await update.message.reply_photo(photo=output[0], caption="here you go 🤡")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Run the bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("rme", rme))
print("🤖 Bot is live!")
app.run_polling()
