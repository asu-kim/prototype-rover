from flask import Flask, render_template, request, jsonify
import os
import sys
import RPi.GPIO as GPIO
import time
import threading

# Initialize the Flask application
app = Flask(__name__)

# GPIO pin assignments
DIR_PIN_A = 17
PWM_PIN_A = 18
DIR_PIN_C = 22
PWM_PIN_C = 23
TRIG = 24
ECHO = 25

# Maximum duty cycle for the motors
MAX_DUTY_CYCLE = 50
STEERING_DUTY_CYCLE = 100

# Global variables
emergency_stop_active = False

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN_A, GPIO.OUT)
GPIO.setup(PWM_PIN_A, GPIO.OUT)
GPIO.setup(DIR_PIN_C, GPIO.OUT)
GPIO.setup(PWM_PIN_C, GPIO.OUT)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Initialize PWM
pwm_a = GPIO.PWM(PWM_PIN_A, 5000)
pwm_c = GPIO.PWM(PWM_PIN_C, 40000)
pwm_a.start(0)
pwm_c.start(0)

# Functions for motor control
def set_motor_a_speed(speed):
    if speed > 0:
        GPIO.output(DIR_PIN_A, GPIO.LOW)
        pwm_a.ChangeDutyCycle(speed)
    elif speed < 0:
        GPIO.output(DIR_PIN_A, GPIO.HIGH)
        pwm_a.ChangeDutyCycle(abs(speed))
    else:
        pwm_a.ChangeDutyCycle(0)

def set_motor_c_direction(speed):
    if speed > 0:
        GPIO.output(DIR_PIN_C, GPIO.HIGH)
        pwm_c.ChangeDutyCycle(speed)
    elif speed < 0:
        GPIO.output(DIR_PIN_C, GPIO.LOW)
        pwm_c.ChangeDutyCycle(abs(speed))
    else:
        pwm_c.ChangeDutyCycle(0)

def measure_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(ECHO) == 0:
        start_time = time.time()

    while GPIO.input(ECHO) == 1:
        stop_time = time.time()

    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2
    return distance

# Flask routes
@app.route('/')
def index():
    return render_template('Controls.html')

@app.route('/move', methods=['POST'])
def move():
    global emergency_stop_active
    if emergency_stop_active:
        set_motor_a_speed(0)
        set_motor_c_direction(0)
        func = request.environ.get('Werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError("Not running with the Werkzeug Server")
        func()
        os.execv(sys.executable, ['python3'] + sys.argv)

    direction = request.form.get('direction')
    distance = measure_distance()

    if direction == "forward":
        if distance >= 0 and distance < 150:
            return jsonify(message="Obstacle detected in front! Cannot move forward."), 400
        set_motor_a_speed(10)
    elif direction == "backward":
        set_motor_a_speed(-10)
    elif direction == "left":
        set_motor_c_direction(-25)
    elif direction == "right":
        set_motor_c_direction(25)
    elif direction == "stop":
        set_motor_a_speed(0)
        set_motor_c_direction(0)
    else:
        return jsonify(message="Invalid direction."), 400

    return jsonify(message=f"Robot is moving {direction}."), 200

@app.route('/emergency_stop', methods=['POST'])
def emergency_stop():
    global emergency_stop_active
    emergency_stop_active = True
    set_motor_a_speed(0)
    set_motor_c_direction(0)

    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()
    os.execv(sys.executable, ['python3'] + sys.argv)

@app.route('/soft_stop', methods=['POST'])
def soft_stop():
    set_motor_a_speed(0)
    set_motor_c_direction(0)
    return jsonify(message="Soft Stop activated! Rover stopped but further commands allowed."), 200

@app.route('/release_emergency', methods=['POST'])
def release_emergency():
    global emergency_stop_active
    emergency_stop_active = False
    return jsonify(message="Emergency stop released. Commands are now accepted."), 200

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        pass
    finally:
        pwm_a.stop()
        pwm_c.stop()
        GPIO.cleanup()
