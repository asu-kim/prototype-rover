from flask import Flask, render_template, request
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
MAX_DUTY_CYCLE = 50

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN_A, GPIO.OUT)
GPIO.setup(PWM_PIN_A, GPIO.OUT)
GPIO.setup(DIR_PIN_C, GPIO.OUT)
GPIO.setup(PWM_PIN_C, GPIO.OUT)

pwm_a = GPIO.PWM(PWM_PIN_A, 5000)  # PWM for Motor A
pwm_c = GPIO.PWM(PWM_PIN_C, 5000)  # PWM for Motor C
pwm_a.start(0)
pwm_c.start(0)

# Helper functions to control motors
def set_motor_a(speed):
    if speed > 0:
        GPIO.output(DIR_PIN_A, GPIO.LOW)
        pwm_a.ChangeDutyCycle(speed)
    elif speed < 0:
        GPIO.output(DIR_PIN_A, GPIO.HIGH)
        pwm_a.ChangeDutyCycle(abs(speed))
    else:
        pwm_a.ChangeDutyCycle(0)

def set_motor_c(speed):
    if speed > 0:
        GPIO.output(DIR_PIN_C, GPIO.HIGH)
        pwm_c.ChangeDutyCycle(speed)
    elif speed < 0:
        GPIO.output(DIR_PIN_C, GPIO.LOW)
        pwm_c.ChangeDutyCycle(abs(speed))
    else:
        pwm_c.ChangeDutyCycle(0)

@app.route('/')
def index():
    return render_template('control.html')

@app.route('/move', methods=['POST'])
def move():
    direction = request.form.get('direction')
    speed = int(request.form.get('speed', 0))

    if direction == "forward":
        set_motor_a(MAX_DUTY_CYCLE)
    elif direction == "backward":
        set_motor_a(-MAX_DUTY_CYCLE)
    elif direction == "left":
        set_motor_c(-5)
    elif direction == "right":
        set_motor_c(5)
    elif direction == "stop":
        set_motor_a(0)
        set_motor_c(0)

    return "OK", 200

def main():
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        pass
    finally:
        pwm_a.stop()
        pwm_c.stop()
        GPIO.cleanup()
