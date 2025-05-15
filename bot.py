import os
from io import BytesIO
import requests
import openai
from dotenv import load_dotenv
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a photo, then reply to it with /rme to cartoonify it 🤡")

async def rme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ensure the user is replying to a photo
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text("Please reply to a photo with /rme.")
        return

    # Get highest resolution photo from replied message
    file_id = update.message.reply_to_message.photo[-1].file_id
    file = await context.bot.get_file(file_id)
    image_data = requests.get(file.file_path).content
    image_stream = BytesIO(image_data)

    await update.message.reply_text("Drawing your goofy cartoon... hang tight 🤪")

    try:
        # For now, just use prompt-only image generation
        response = openai.images.generate(
            model="dall-e-3",
            prompt="A dumb, distorted cartoon version of the person in this photo. Big far-apart eyes, a weird mouth, silly expression, and funny colors. Drawn in sketchy meme style.",
            n=1,
            size="1024x1024"
        )
        img_url = response.data[0].url
        cartoon = requests.get(img_url).content

        await update.message.reply_photo(photo=BytesIO(cartoon), caption="here you go 🤡")

    except Exception as e:
        await update.message.reply_text(f"Error generating image: {e}")

# Initialize bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("rme", rme))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))  # fallback

print("🤖 Bot is running...")
app.run_polling()
