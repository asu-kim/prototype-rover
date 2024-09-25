import RPi.GPIO as GPIO
import time

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define GPIO pins
output_pin = 17  # Pin to be tested as output
input_pin = 18   # Pin to be tested as input

# Set up GPIO pins
GPIO.setup(output_pin, GPIO.OUT)
GPIO.setup(input_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set input pin with a pull-down resistor

def check_pins():
    print("Testing GPIO pins 17 (output) and 18 (input)...")
    
    # Set the output pin HIGH
    GPIO.output(output_pin, GPIO.HIGH)
    time.sleep(1)  # Wait for the change to be reflected
    
    # Check the input pin state
    if GPIO.input(input_pin) == GPIO.HIGH:
        print("GPIO 18 detected HIGH (Output from GPIO 17 is working)")
    else:
        print("GPIO 18 failed to detect HIGH (Check wiring or GPIO 17)")
    
    # Set the output pin LOW
    GPIO.output(output_pin, GPIO.LOW)
    time.sleep(1)  # Wait for the change to be reflected

    # Check the input pin state again
    if GPIO.input(input_pin) == GPIO.LOW:
        print("GPIO 18 detected LOW (Output from GPIO 17 is working)")
    else:
        print("GPIO 18 failed to detect LOW (Check wiring or GPIO 17)")

try:
    check_pins()

except KeyboardInterrupt:
    print("Test interrupted")

finally:
    # Cleanup GPIO
    GPIO.cleanup()
    print("GPIO cleanup complete")
