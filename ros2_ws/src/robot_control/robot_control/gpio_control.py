import RPi.GPIO as GPIO
import time

def main():
    # GPIO pin assignments
    DIR_PIN_A = 17  # Motor A Direction
    PWM_PIN_A = 18  # Motor A Speed (PWM)
    DIR_PIN_C = 22  # Motor C Direction
    PWM_PIN_C = 23  # Motor C Speed (PWM)
    MAX_DUTY_CYCLE = 50

    # GPIO setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DIR_PIN_A, GPIO.OUT)
    GPIO.setup(PWM_PIN_A, GPIO.OUT)
    GPIO.setup(DIR_PIN_C, GPIO.OUT)
    GPIO.setup(PWM_PIN_C, GPIO.OUT)

    pwm_a = GPIO.PWM(PWM_PIN_A, 5000)
    pwm_c = GPIO.PWM(PWM_PIN_C, 5000)
    pwm_a.start(0)
    pwm_c.start(0)

    try:
        while True:
            print("Running GPIO control...")
            time.sleep(1)  # Simulate GPIO operations
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        pwm_a.stop()
        pwm_c.stop()
        GPIO.cleanup()
