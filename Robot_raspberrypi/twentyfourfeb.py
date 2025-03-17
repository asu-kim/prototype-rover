from flask import Flask, render_template, request, jsonify
import RPi.GPIO as GPIO
import time
import threading

app = Flask(__name__)

# GPIO pin assignments
DIR_PIN_A = 17
PWM_PIN_A = 18
DIR_PIN_C = 22
PWM_PIN_C = 23
TRIG = 24
ECHO = 25

# Constants
MAX_DISTANCE = 200  # Maximum distance to measure (in cm)
SAFE_DISTANCE = 100  # Safe distance threshold (in cm)
MAX_DUTY_CYCLE = 50
STEERING_DUTY_CYCLE = 100

# Global variables
emergency_stop_active = False
soft_stop_active = False
current_distance = MAX_DISTANCE

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN_A, GPIO.OUT)
GPIO.setup(PWM_PIN_A, GPIO.OUT)
GPIO.setup(DIR_PIN_C, GPIO.OUT)
GPIO.setup(PWM_PIN_C, GPIO.OUT)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Initialize PWM
pwm_a = GPIO.PWM(PWM_PIN_A, 1000)
pwm_c = GPIO.PWM(PWM_PIN_C, 1000)
pwm_a.start(0)
pwm_c.start(0)

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
    GPIO.output(TRIG, False)
    time.sleep(0.000002)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return min(distance, MAX_DISTANCE)

def continuous_distance_measurement():
    global current_distance
    while True:
        current_distance = measure_distance()
        time.sleep(0.1)

# Start the continuous distance measurement in a separate thread
distance_thread = threading.Thread(target=continuous_distance_measurement)
distance_thread.daemon = True
distance_thread.start()

@app.route('/')
def index():
    return render_template('Controls.html')

@app.route('/move', methods=['POST'])
def move():
    global soft_stop_active
    direction = request.form.get('direction')

    if soft_stop_active:
        return jsonify(message="Soft Stop is active. Robot cannot move."), 400

    if current_distance < SAFE_DISTANCE and direction in ['forward', 'backward']:
        return jsonify(message=f"Cannot move {direction}. Obstacle detected within {SAFE_DISTANCE} cm."), 400

    if direction == 'forward':
        set_motor_a_speed(MAX_DUTY_CYCLE)
    elif direction == 'backward':
        set_motor_a_speed(-MAX_DUTY_CYCLE)
    elif direction == 'left':
        set_motor_c_direction(-STEERING_DUTY_CYCLE)
    elif direction == 'right':
        set_motor_c_direction(STEERING_DUTY_CYCLE)
    elif direction == 'stop':
        set_motor_a_speed(0)
        set_motor_c_direction(0)
    else:
        return jsonify(message="Invalid direction."), 400

    return jsonify(message=f"Robot is moving {direction}."), 200

@app.route('/soft_stop', methods=['POST'])
def soft_stop():
    global soft_stop_active
    soft_stop_active = True
    set_motor_a_speed(0)
    set_motor_c_direction(0)
    return jsonify(message="Soft Stop activated! Rover stopped but further commands allowed."), 200

@app.route('/emergency_stop', methods=['POST'])
def emergency_stop():
    global emergency_stop_active
    emergency_stop_active = True
    set_motor_a_speed(0)
    set_motor_c_direction(0)
    return jsonify(message="Emergency Stop activated!"), 200

@app.route('/record', methods=['POST'])
def record():
    action = request.form.get('action')
    if action == 'start':
        # Implement start recording logic here
        return jsonify(message="Recording started."), 200
    elif action == 'stop':
        # Implement stop recording logic here
        return jsonify(message="Recording stopped."), 200
    else:
        return jsonify(message="Invalid recording action."), 400

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        pwm_a.stop()
        pwm_c.stop()
        GPIO.cleanup()
