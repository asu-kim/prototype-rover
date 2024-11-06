from flask import Flask, render_template, request
import RPi.GPIO as GPIO
import time

# Initialize the Flask application
app = Flask(__name__)

# GPIO pin assignments for Motor Driver A (forward and backward)
DIR_PIN_A = 17  # GPIO17 for direction (forward/backward)
PWM_PIN_A = 18  # GPIO18 for speed (PWM)

# GPIO pin assignments for Motor Driver C (left and right)
DIR_PIN_C = 22  # GPIO22 for direction (left/right)
PWM_PIN_C = 23  # GPIO23 for speed (PWM)

# Maximum duty cycle for the motors
MAX_DUTY_CYCLE = 50  # Adjust this for motor A (main movement)
STEERING_DUTY_CYCLE = 15  # Lower duty cycle for steering to slow it down

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN_A, GPIO.OUT)
GPIO.setup(PWM_PIN_A, GPIO.OUT)
GPIO.setup(DIR_PIN_C, GPIO.OUT)
GPIO.setup(PWM_PIN_C, GPIO.OUT)

# Initialize PWM for both motor drivers
pwm_a = GPIO.PWM(PWM_PIN_A, 5000)  # PWM for Motor A at 5kHz
pwm_c = GPIO.PWM(PWM_PIN_C, 5000)  # PWM for Motor C at 5kHz
pwm_a.start(0)  # Start with 0% duty cycle
pwm_c.start(0)  # Start with 0% duty cycle

# Function to control Motor A (forward and backward)
def set_motor_a_speed(speed):
    speed = max(min(speed, MAX_DUTY_CYCLE), -MAX_DUTY_CYCLE)  # Limit speed to 50%
    if speed > 0:
        GPIO.output(DIR_PIN_A, GPIO.LOW)  # Forward direction
        pwm_a.ChangeDutyCycle(speed)
    elif speed < 0:
        GPIO.output(DIR_PIN_A, GPIO.HIGH)  # Reverse direction
        pwm_a.ChangeDutyCycle(abs(speed))
    else:
        pwm_a.ChangeDutyCycle(0)  # Stop motor A

# Function to control Motor C (left and right)
def set_motor_c_direction(speed):
    speed = max(min(speed, STEERING_DUTY_CYCLE), -STEERING_DUTY_CYCLE)  # Limit speed for smoother steering
    if speed > 0:
        GPIO.output(DIR_PIN_C, GPIO.HIGH)  # Turn right
        pwm_c.ChangeDutyCycle(speed)
        time.sleep(0.2)  # Run the motor briefly to make a small turn
    elif speed < 0:
        GPIO.output(DIR_PIN_C, GPIO.LOW)  # Turn left
        pwm_c.ChangeDutyCycle(abs(speed))
        time.sleep(0.2)  # Run the motor briefly to make a small turn
    pwm_c.ChangeDutyCycle(0)  # Stop the steering motor after turning

# Flask routes to render the webpage and handle motor control
@app.route('/')
def index():
    return render_template('control.html')

@app.route('/move', methods=['POST'])
def move():
    direction = request.form.get('direction')
    
    if direction == "forward":
        set_motor_a_speed(50)  # Move forward at full speed
    elif direction == "backward":
        set_motor_a_speed(-50)  # Move backward at full speed
    elif direction == "left":
        set_motor_c_direction(-10)  # Turn left with reduced speed
    elif direction == "right":
        set_motor_c_direction(10)  # Turn right with reduced speed
    elif direction == "stop":
        set_motor_a_speed(0)  # Stop Motor A
        set_motor_c_direction(0)  # Stop Motor C (no steering)
    
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
