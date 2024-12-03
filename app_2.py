from flask import Flask, render_template, request
import RPi.GPIO as GPIO

# Initialize the Flask application
app = Flask(__name__)

# GPIO pin assignments for Motor A (MD30C Motor Driver)
DIR_PIN_A = 17  # Pin controlling the direction of Motor A (GPIO17)
PWM_PIN_A = 18  # Pin controlling the speed of Motor A (GPIO18 - PWM capable)
MAX_DUTY_CYCLE = 25  # Limit the duty cycle to 25%

# GPIO pin assignments for Motor C
PIN_A = 22  # Pin A for Motor C direction control
PIN_B = 23  # Pin B for Motor C direction control

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN_A, GPIO.OUT)
GPIO.setup(PWM_PIN_A, GPIO.OUT)
GPIO.setup(PIN_A, GPIO.OUT)
GPIO.setup(PIN_B, GPIO.OUT)

# Initialize PWM for Motor A at 100Hz frequency
pwm_a = GPIO.PWM(PWM_PIN_A, 5000)  
pwm_a.start(0)  # Start PWM with 0% duty cycle (motor off)

# Function to control Motor A speed
def set_motor_a_speed(speed):
    speed = max(min(speed, MAX_DUTY_CYCLE), -MAX_DUTY_CYCLE)  # Limit speed to 25%
    if speed > 0:
        GPIO.output(DIR_PIN_A, GPIO.HIGH)  # Forward direction
        pwm_a.ChangeDutyCycle(speed)
    elif speed < 0:
        GPIO.output(DIR_PIN_A, GPIO.LOW)  # Reverse direction
        pwm_a.ChangeDutyCycle(abs(speed))
    else:
        pwm_a.ChangeDutyCycle(0)  # Stop motor A

# Function to control Motor C direction
def set_motor_c_direction(direction):
    if direction == "right":
        GPIO.output(PIN_A, GPIO.HIGH)
        GPIO.output(PIN_B, GPIO.LOW)
    elif direction == "left":
        GPIO.output(PIN_A, GPIO.LOW)
        GPIO.output(PIN_B, GPIO.HIGH)
    else:
        GPIO.output(PIN_A, GPIO.LOW)
        GPIO.output(PIN_B, GPIO.LOW)  # Stop motor C

# Flask routes to render the webpage and handle motor control
@app.route('/')
def index():
    return render_template('control.html')

@app.route('/move', methods=['POST'])
def move():
    direction = request.form.get('direction')
    
    if direction == "forward":
        set_motor_a_speed(100)  # Move forward at 25% speed
    elif direction == "backward":
        set_motor_a_speed(-100)  # Move backward at 25% speed
    elif direction == "left":
        set_motor_c_direction("left")  # Motor C turns left
    elif direction == "right":
        set_motor_c_direction("right")  # Motor C turns right
    elif direction == "stop":
        set_motor_a_speed(0)  # Stop Motor A
        set_motor_c_direction("stop")  # Stop Motor C
    
    return "OK", 200

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        pass
    finally:
        pwm_a.stop()  # Stop PWM
        GPIO.cleanup()  # Clean up GPIO on exit
