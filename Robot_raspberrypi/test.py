import gpiod
import time

# GPIO chip setup (usually 'gpiochip0' for the Raspberry Pi)
chip = gpiod.Chip('gpiochip0')

# Define GPIO pin numbers (using Broadcom numbering, not physical pin numbers)
PIN_A = 22  # GPIO 22 (Physical Pin 15)
PIN_B = 23  # GPIO 23 (Physical Pin 16)

# Request the GPIO lines (pins)
line_a = chip.get_line(PIN_A)
line_b = chip.get_line(PIN_B)

# Configure the lines as outputs
line_a.request(consumer='test_pin_a', type=gpiod.LINE_REQ_DIR_OUT)
line_b.request(consumer='test_pin_b', type=gpiod.LINE_REQ_DIR_OUT)

try:
    while True:
        # Set GPIO 22 to HIGH, GPIO 23 to LOW
        print("Setting GPIO 22 HIGH, GPIO 23 LOW")
        line_a.set_value(1)  # Set GPIO 22 to HIGH
        line_b.set_value(0)  # Set GPIO 23 to LOW
        time.sleep(3)        # Wait for 3 seconds

        # Set GPIO 22 to LOW, GPIO 23 to HIGH
        print("Setting GPIO 22 LOW, GPIO 23 HIGH")
        line_a.set_value(0)  # Set GPIO 22 to LOW
        line_b.set_value(1)  # Set GPIO 23 to HIGH
        time.sleep(3)        # Wait for 3 seconds

        # Set both GPIOs to LOW
        print("Setting both GPIO 22 and GPIO 23 LOW")
        line_a.set_value(0)
        line_b.set_value(0)
        time.sleep(3)        # Wait for 3 seconds

except KeyboardInterrupt:
    print("Exiting program")

finally:
    # Reset both GPIO pins to LOW before exiting
    line_a.set_value(0)
    line_b.set_value(0)
    print("GPIO cleanup completed")
