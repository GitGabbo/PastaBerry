import RPi.GPIO as GPIO
from time import sleep
import os
import time
import glob
import signal
import sys

### TEMPERATURE INFO
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
def read_temperature_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
def read_temp():
    lines = read_temperature_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000
        return temp_c


### MOTORS
step_sequence = [[1,0,0,1],
                 [1,0,0,0],
                 [1,1,0,0],
                 [0,1,0,0],
                 [0,1,1,0],
                 [0,0,1,0],
                 [0,0,1,1],
                 [0,0,0,1]]
motor1_in1 = 12
motor1_in2 = 16
motor1_in3 = 20
motor1_in4 = 21
motor2_in1 = 18
motor2_in2 = 23
motor2_in3 = 24
motor2_in4 = 25
step_sleep = 0.002
step_count = 2048

motor1_pins = [motor1_in1,motor1_in2,motor1_in3,motor1_in4]
motor2_pins = [motor2_in1,motor2_in2,motor2_in3,motor2_in4]
motor1_step_counter = 0
motor2_step_counter = 0

### RELAY
RELE_OUT = 26



def init_pins():
	# choose BCM or BOARD
	GPIO.setmode(GPIO.BCM)  
	# setting up
	GPIO.setup(RELE_OUT, GPIO.OUT)
	GPIO.setup(motor1_in1, GPIO.OUT)
	GPIO.setup(motor1_in2, GPIO.OUT)
	GPIO.setup(motor1_in3, GPIO.OUT)
	GPIO.setup(motor1_in4, GPIO.OUT)
	GPIO.setup(motor2_in1, GPIO.OUT)
	GPIO.setup(motor2_in2, GPIO.OUT)
	GPIO.setup(motor2_in3, GPIO.OUT)
	GPIO.setup(motor2_in4, GPIO.OUT)
	# initializing
	clean_up()

def clean_up():
	GPIO.output(RELE_OUT, GPIO.LOW)
	GPIO.output(motor1_in1, GPIO.LOW)
	GPIO.output(motor1_in2, GPIO.LOW)
	GPIO.output(motor1_in3, GPIO.LOW)
	GPIO.output(motor1_in4, GPIO.LOW)
	GPIO.output(motor2_in1, GPIO.LOW)
	GPIO.output(motor2_in2, GPIO.LOW)
	GPIO.output(motor2_in3, GPIO.LOW)
	GPIO.output(motor2_in4, GPIO.LOW)

# rotate motors
def rotate_motors(clockwise):
	global motor1_step_counter
	global motor2_step_counter

	for i in range(step_count):
		for pin in range(len(motor1_pins)):
			GPIO.output(motor1_pins[pin], step_sequence[motor1_step_counter][pin])
			GPIO.output(motor2_pins[pin], step_sequence[motor2_step_counter][pin])
		if clockwise:
			motor1_step_counter = (motor1_step_counter - 1) % 8
			motor2_step_counter = (motor2_step_counter + 1) % 8
		else:
			motor1_step_counter = (motor1_step_counter + 1) % 8
			motor2_step_counter = (motor2_step_counter - 1) % 8
		time.sleep(step_sleep)

async def cook_script(pasta_timer, context, chat_id):
	BOILING_WATER_TEMPERATURE = 90
	pasta_timer = int(pasta_timer)
	init_pins()
	try:
		GPIO.output(RELE_OUT, GPIO.HIGH)
		msg = "Burner turned on"
		print(f"\n\n{msg}\n\n")
		await context.bot.send_message(chat_id=chat_id, text=msg)
		boiling_water = False
		temperature = 0
		while not boiling_water:
			# get water temperature from sensor
			sleep(1)
			temperature = read_temp()
			print(f"Temperature: {temperature}°C")
			if temperature >= BOILING_WATER_TEMPERATURE:
				boiling_water = True

		msg = "Water is boiling"
		print(f"\n\n{msg}\n\n")
		await context.bot.send_message(chat_id=chat_id, text=msg)

		# rotate motors
		rotate_motors(clockwise=True)
		sleep(3)
		# rotate motors
		rotate_motors(clockwise=False)

		msg = f"Your pasta is now cooking. Waiting {pasta_timer*60} seconds ({pasta_timer} minutes)"
		print(f"\n\n{msg}\n\n")
		await context.bot.send_message(chat_id=chat_id, text=msg)

		# wait for pasta to be ready
		sleep(pasta_timer*60)
		
		# done
		msg = f"Your pasta is ready"
		print(f"\n\n{msg}\n\n")
		await context.bot.send_message(chat_id=chat_id, text=msg)
		
		# shutdown relay
		GPIO.output(RELE_OUT, 0)				# set port/pin value to 1/GPIO.High/True
		msg = "Burner turned off"
		print(f"\n\n{msg}\n\n")
		await context.bot.send_message(chat_id=chat_id, text=msg)
	except KeyboardInterrupt:
		print("KeyboardInterrupt captured")
	except:
		# trap a CTRL+C keyboard interrupt
		print("An error has occurred")
	finally:
		GPIO.cleanup()
		print("Relay stopped. Everything is ok!")

async def shutdown(context, chat_id):
	GPIO.cleanup()
	msg = f"Your pins have been cleaned"
	print(f"\n\n{msg}\n\n")
	await context.bot.send_message(chat_id=chat_id, text=msg)

def handler(signum, frame):
	GPIO.cleanup()
	print('Ctrl+Z pressed, pins cleared')

signal.signal(signal.SIGTSTP, handler)