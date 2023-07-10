import dotenv
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import cook

# pip install python-telegram-bot --upgrade

dotenv.load_dotenv()
TOKEN = os.environ["TOKEN"]

logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	level=logging.INFO
)

# seconds for pasta to be ready
PASTA_TIMER = int(os.environ["PASTATIMER"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm PastaBerryBot, the bot that helps you cook pasta!")

async def set_pasta_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
	PASTA_TIMER = int(context.args[0])*60
	response = f"Default timer set to {PASTA_TIMER}s ({int(PASTA_TIMER/60)}min)!"
	print(f"\n{response}\n")
	dotenv.set_key(".env", "PASTATIMER", str(PASTA_TIMER))
	await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

async def start_cooking(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if len(context.args) > 0:
		PASTA_TIMER = int(context.args[0])*60
	response = f"\nStarting cooking. The pasta timer is set to {PASTA_TIMER}s ({int(PASTA_TIMER/60)}min).\n"
	print(f"\n{response}\n")
	
	await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

	# do raspberry things
	await cook.cook_script(PASTA_TIMER/60, context, update.effective_chat.id)

if __name__ == '__main__':
	application = ApplicationBuilder().token(TOKEN).build()
	
	start_handler = CommandHandler('start', start)
	application.add_handler(start_handler)

	pasta_timer_handler = CommandHandler('set_pasta_timer', set_pasta_timer)
	application.add_handler(pasta_timer_handler)

	start_cooking_handler = CommandHandler('start_cooking', start_cooking)
	application.add_handler(start_cooking_handler)
	
	application.run_polling()