import RPi.GPIO as GPIO
import time

# Pin definitions (BCM mode)
PIN_A = 17  # GPIO 17 (Physical Pin 15)
PIN_B = 18  # GPIO 18 (Physical Pin 16)

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)  # Use BCM numbering
GPIO.setup(PIN_A, GPIO.OUT)  # Set GPIO 22 as an output
GPIO.setup(PIN_B, GPIO.OUT)  # Set GPIO 23 as an output

try:
    while True:
        # Set GPIO 22 HIGH, GPIO 23 LOW
        print("Setting GPIO 22 HIGH, GPIO 23 LOW")
        GPIO.output(PIN_A, GPIO.HIGH)  # Set GPIO 22 to HIGH
        GPIO.output(PIN_B, GPIO.LOW)   # Set GPIO 23 to LOW
        time.sleep(3)  # Wait 3 seconds

        # Set GPIO 22 LOW, GPIO 23 HIGH
        print("Setting GPIO 22 LOW, GPIO 23 HIGH")
        GPIO.output(PIN_A, GPIO.LOW)   # Set GPIO 22 to LOW
        GPIO.output(PIN_B, GPIO.HIGH)  # Set GPIO 23 to HIGH
        time.sleep(3)  # Wait 3 seconds

        # Set both GPIOs to LOW
        print("Setting both GPIO 22 and GPIO 23 LOW")
        GPIO.output(PIN_A, GPIO.LOW)
        GPIO.output(PIN_B, GPIO.LOW)
        time.sleep(3)  # Wait 3 seconds

except KeyboardInterrupt:
    print("Exiting program")

finally:
    # Clean up GPIO
    GPIO.cleanup()  # Reset GPIO settings
    print("GPIO cleanup completed")
