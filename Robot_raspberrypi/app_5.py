from flask import Flask, render_template, request
import RPi.GPIO as GPIO

# Initialize the Flask application
app = Flask(__name__)

# GPIO pin assignments for Motor Driver A (forward and backward)
DIR_PIN_A = 17  # GPIO17 for direction (forward/backward)
PWM_PIN_A = 18  # GPIO18 for speed (PWM)

# GPIO pin assignments for Motor Driver C (left and right)
DIR_PIN_C = 22  # GPIO22 for direction (left/right)
PWM_PIN_C = 23  # GPIO23 for speed (PWM)

# Maximum duty cycle (adjust as necessary for your motor)
MAX_DUTY_CYCLE = 100

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN_A, GPIO.OUT)
GPIO.setup(PWM_PIN_A, GPIO.OUT)
GPIO.setup(DIR_PIN_C, GPIO.OUT)
GPIO.setup(PWM_PIN_C, GPIO.OUT)

# Initialize PWM for both motor drivers
pwm_a = GPIO.PWM(PWM_PIN_A, 2500)  # PWM for Motor A at 5kHz
pwm_c = GPIO.PWM(PWM_PIN_C, 2500)  # PWM for Motor C at 5kHz
pwm_a.start(0)  # Start with 0% duty cycle
pwm_c.start(0)  # Start with 0% duty cycle

# Function to control Motor A (forward and backward)
def set_motor_a_speed(speed):
    speed = max(min(speed, MAX_DUTY_CYCLE), -MAX_DUTY_CYCLE)  # Limit speed to 100%
    if speed > 0:
        GPIO.output(DIR_PIN_A, GPIO.LOW)  # Forward direction
        pwm_a.ChangeDutyCycle(speed)
    elif speed < 0:
        GPIO.output(DIR_PIN_A, GPIO.HIGH)  # Reverse direction
        pwm_a.ChangeDutyCycle(abs(speed))
    else:
        pwm_a.ChangeDutyCycle(0)  # Stop motor A

# Function to control Motor C (left and right) with variable speed
def set_motor_c_direction(direction, speed):
    speed = max(min(speed, MAX_DUTY_CYCLE), 0)  # Limit speed to 0-100%
    if direction == "right":
        GPIO.output(DIR_PIN_C, GPIO.HIGH)  # Turn right
        pwm_c.ChangeDutyCycle(speed)
    elif direction == "left":
        GPIO.output(DIR_PIN_C, GPIO.LOW)  # Turn left
        pwm_c.ChangeDutyCycle(speed)
    else:
        pwm_c.ChangeDutyCycle(0)  # Stop Motor C (no steering)

# Flask routes to render the webpage and handle motor control
@app.route('/')
def index():
    return render_template('control.html')

@app.route('/move', methods=['POST'])
def move():
    direction = request.form.get('direction')
    speed = int(request.form.get('speed', 0))  # Get speed if available, default to 0
    
    if direction == "forward":
        set_motor_a_speed(100)  # Move forward at full speed
    elif direction == "backward":
        set_motor_a_speed(-100)  # Move backward at full speed
    elif direction in ["left", "right"]:
        set_motor_c_direction(direction, speed)  # Control steering with speed
    elif direction == "stop":
        set_motor_a_speed(0)  # Stop Motor A
        set_motor_c_direction("stop", 0)  # Stop Motor C (no steering)
    
    return "OK", 200

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        pass
    finally:
        pwm_a.stop()  # Stop PWM for Motor A
        pwm_c.stop()  # Stop PWM for Motor C
        GPIO.cleanup()  # Clean up GPIO on exit
