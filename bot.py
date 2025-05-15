import os
from io import BytesIO
import requests
import openai
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
)

# Load .env
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Yo 👋 Send /drawme and I'll cartoonify your profile pic in meme style 🤡")

async def drawme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photos = await context.bot.get_user_profile_photos(user.id, limit=1)

    if photos.total_count == 0:
        await update.message.reply_text("You don’t have a profile photo I can use 😞")
        return

    file = await context.bot.get_file(photos.photos[0][-1].file_id)
    response = requests.get(file.file_path)
    profile_img = BytesIO(response.content)

    # Generate cartoon meme image
    await update.message.reply_text("Drawing you as a goofy cartoon... please wait 🤓")
    try:
        result = openai.images.generate(
            model="dall-e-3",
            prompt="Turn this into a funny cartoon meme with a dumb expression, far-apart eyes, weird mouth, and saturated colors.",
            image=profile_img,
            n=1,
            size="1024x1024"
        )
        img_url = result.data[0].url
        img_data = requests.get(img_url).content
        await update.message.reply_photo(photo=BytesIO(img_data), caption="here you go 🤡")
    except Exception as e:
        await update.message.reply_text(f"Error generating image: {e}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("drawme", drawme))

print("🤖 Bot is running...")
app.run_polling()
