import RPi.GPIO as GPIO
import time

TRIG = 24
ECHO = 25

GPIO.setmode(GPIO.BCM)

while True:
    print("Distance measurement in progress")

    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    
    GPIO.output(TRIG, False)
    print("Waiting for sensor to settle")
    time.sleep(0.2)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    print(f"Distance: {distance} cm")
    time.sleep(2)

