# import RPi.GPIO as GPIO           		# import RPi.GPIO module  
from time import sleep

async def cook_script(pasta_timer, context, chat_id):
	BOILING_WATER_TEMPERATURE = 90

	# GPIO.setmode(GPIO.BCM)				# choose BCM or BOARD  
	RELE_OUT = 24
	TEMP_IN = 26
	# GPIO.setup(RELE_OUT, GPIO.OUT)		# set a port/pin as an output   
	# GPIO.setup(TEMP_IN, GPIO.IN)			# set a port/pin as an output   

	# GPIO.output(RELE_OUT, 1)				# set port/pin value to 0/GPIO.LOW/False
	msg = "Burner turned on"
	print(msg)
	await context.bot.send_message(chat_id=chat_id, text=msg)
	

	try:
		boiling_water = False
		temperature = 0
		while not boiling_water:
			# get water temperature from sensor
			temperature += 1
			sleep(0.5)
			if temperature >= BOILING_WATER_TEMPERATURE:
				boiling_water = True

		msg = "Water is boiling"
		print(msg)
		await context.bot.send_message(chat_id=chat_id, text=msg)

		# rotate motors
		sleep(3)
		# rotate motors

		msg = f"Your pasta is now cooking. Waiting {pasta_timer*60} min"
		print(msg)
		await context.bot.send_message(chat_id=chat_id, text=msg)

		# wait for pasta to be ready
		sleep(pasta_timer)

		msg = f"Your pasta is ready"
		print(msg)
		await context.bot.send_message(chat_id=chat_id, text=msg)
		
		# GPIO.output(RELE_OUT, 0)				# set port/pin value to 1/GPIO.High/True
		msg = "Burner turned off"
		print(msg)
		await context.bot.send_message(chat_id=chat_id, text=msg)
	except KeyboardInterrupt:					# trap a CTRL+C keyboard interrupt
		# GPIO.cleanup()						# resets all GPIO ports used by this program
		# GPIO.output(RELE_OUT, 0)				# set port/pin value to 1/GPIO.High/True
		print("OK")