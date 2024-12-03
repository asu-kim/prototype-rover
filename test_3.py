from gpiozero import LED
from time import sleep

# Define GPIO pins
PIN_A = 22  # GPIO 22 (Physical Pin 15)
PIN_B = 23  # GPIO 23 (Physical Pin 16)

# Set up GPIO pins as outputs
pin_a = LED(PIN_A)  # GPIO 22
pin_b = LED(PIN_B)  # GPIO 23

try:
    while True:
        # Set GPIO 22 HIGH, GPIO 23 LOW
        print("Setting GPIO 22 HIGH, GPIO 23 LOW")
        pin_a.on()  # GPIO 22 HIGH
        pin_b.off()  # GPIO 23 LOW
        sleep(3)  # Wait 3 seconds

        # Set GPIO 22 LOW, GPIO 23 HIGH
        print("Setting GPIO 22 LOW, GPIO 23 HIGH")
        pin_a.off()  # GPIO 22 LOW
        pin_b.on()   # GPIO 23 HIGH
        sleep(3)  # Wait 3 seconds

        # Set both GPIOs to LOW
        print("Setting both GPIO 22 and GPIO 23 LOW")
        pin_a.off()  # GPIO 22 LOW
        pin_b.off()  # GPIO 23 LOW
        sleep(3)  # Wait 3 seconds

except KeyboardInterrupt:
    print("Exiting program")

finally:
    print("GPIO cleanup completed")
