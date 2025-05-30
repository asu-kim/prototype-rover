import RPi.GPIO as GPIO
import time

# GPIO pin setup
TRIG = 23
ECHO = 24

# GPIO Mode (BCM or BOARD)
GPIO.setmode(GPIO.BCM)

# Setup pins
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

try:
    while True:
        print("Distance measurement in progress...")
        GPIO.output(TRIG, False)
        print("Waiting for sensor to settle...")
        time.sleep(2)

        # Trigger the sensor
        GPIO.output(TRIG, True)
        time.sleep(0.00001)  # 10µs pulse
        GPIO.output(TRIG, False)

        # Measure the time of the echo pulse
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()

        # Calculate distance
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150  # Speed of sound is 343 m/s (17150 cm/s)
        distance = round(distance, 2)

        print(f"Distance: {distance} cm")
        
except KeyboardInterrupt:
    print("\nMeasurement stopped by user")

finally:
    # Cleanup GPIO settings
    GPIO.cleanup()
