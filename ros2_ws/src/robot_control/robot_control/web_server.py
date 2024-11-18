from flask import Flask, request, render_template
import RPi.GPIO as GPIO

# Flask setup
app = Flask(
    __name__,
    static_folder='/home/pk/Toy-car/ros2_ws/src/robot_control/static',
    template_folder='/home/pk/Toy-car/ros2_ws/src/robot_control/templates'
)


# GPIO pin assignments
DIR_PIN_A = 17  # Motor A Direction
PWM_PIN_A = 18  # Motor A Speed (PWM)
DIR_PIN_C = 22  # Motor C Direction
PWM_PIN_C = 23  # Motor C Speed (PWM)

# Initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN_A, GPIO.OUT)
GPIO.setup(PWM_PIN_A, GPIO.OUT)
GPIO.setup(DIR_PIN_C, GPIO.OUT)
GPIO.setup(PWM_PIN_C, GPIO.OUT)

pwm_a = GPIO.PWM(PWM_PIN_A, 5000)  # Speed control for Motor A
pwm_c = GPIO.PWM(PWM_PIN_C, 5000)  # Speed control for Motor C
pwm_a.start(0)
pwm_c.start(0)

# Helper functions
def set_speed(speed):
    if speed >= 0:
        GPIO.output(DIR_PIN_A, GPIO.LOW)
        pwm_a.ChangeDutyCycle(speed)
    else:
        GPIO.output(DIR_PIN_A, GPIO.HIGH)
        pwm_a.ChangeDutyCycle(abs(speed))

def set_turn(value):
    if value > 0:
        GPIO.output(DIR_PIN_C, GPIO.HIGH)
        pwm_c.ChangeDutyCycle(value)
    elif value < 0:
        GPIO.output(DIR_PIN_C, GPIO.LOW)
        pwm_c.ChangeDutyCycle(abs(value))
    else:
        pwm_c.ChangeDutyCycle(0)

@app.route('/')
def index():
    return render_template('control.html')

@app.route('/move', methods=['POST'])
def move():
    action = request.form.get('action')
    value = int(request.form.get('value', 0))

    if action == 'move':
        if value == 'forward':
            set_speed(50)
        elif value == 'backward':
            set_speed(-50)
        elif value == 'stop':
            set_speed(0)
            set_turn(0)
    elif action == 'speed':
        set_speed(value)
    elif action == 'turn':
        set_turn(value)

    return "OK", 200

def main():
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        pwm_a.stop()
        pwm_c.stop()
        GPIO.cleanup()
