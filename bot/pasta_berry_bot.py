import dotenv
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import cook


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

async def start_cooking(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if len(context.args) > 0:
		PASTA_TIMER = int(context.args[0])*60
	response = f"\nStarting cooking. The pasta timer is set to {PASTA_TIMER}s ({int(PASTA_TIMER/60)}min).\n"
	print(f"\n{response}\n")
	
	await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

	# do raspberry things
	await cook.cook_script(PASTA_TIMER/60, context, update.effective_chat.id)

async def clean_pins(update: Update, context: ContextTypes.DEFAULT_TYPE):
	# do raspberry things
	await cook.shutdown(context, update.effective_chat.id)


if __name__ == '__main__':

	application = ApplicationBuilder().token(TOKEN).build()
	
	start_handler = CommandHandler('start', start)
	application.add_handler(start_handler)

	start_cooking_handler = CommandHandler('start_cooking', start_cooking)
	application.add_handler(start_cooking_handler)

	clean_pins_handler = CommandHandler('clean_pins', clean_pins)
	application.add_handler(clean_pins_handler)
	
	application.run_polling()
