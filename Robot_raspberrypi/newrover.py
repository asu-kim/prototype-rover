from flask import Flask, render_template, request, jsonify
import os
import sys
import RPi.GPIO as GPIO
import time
import threading

# Initialize Flask app
app = Flask(__name__)

# GPIO Pin Assignments
DIR_PIN_A = 17
PWM_PIN_A = 18
DIR_PIN_C = 22
PWM_PIN_C = 23
TRIG = 24
ECHO = 25

# Disable GPIO warnings
GPIO.setwarnings(False)

# Maximum duty cycle for the motors
MAX_DUTY_CYCLE = 50
STEERING_DUTY_CYCLE = 100

# Global emergency stop flag
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

# Function to control Motor A (forward and backward)
def set_motor_a_speed(speed):
    def run_motor():
        global emergency_stop_active
        if emergency_stop_active:
            pwm_a.ChangeDutyCycle(0)  # Stop the motor immediately
            return
        
        speed_limited = max(min(speed, MAX_DUTY_CYCLE), -MAX_DUTY_CYCLE)
        if speed_limited > 0:
            GPIO.output(DIR_PIN_A, GPIO.LOW)
        elif speed_limited < 0:
            GPIO.output(DIR_PIN_A, GPIO.HIGH)
        
        pwm_a.ChangeDutyCycle(abs(speed_limited))

    threading.Thread(target=run_motor, daemon=True).start()

# Function to control Motor C (steering left and right)
def set_motor_c_direction(speed):
    def run_motor():
        global emergency_stop_active
        if emergency_stop_active:
            pwm_c.ChangeDutyCycle(0)  # Stop steering immediately
            return

        speed_limited = max(min(speed, STEERING_DUTY_CYCLE), -STEERING_DUTY_CYCLE)
        if speed_limited > 0:
            GPIO.output(DIR_PIN_C, GPIO.HIGH)
            pwm_c.ChangeDutyCycle(speed_limited)
        elif speed_limited < 0:
            GPIO.output(DIR_PIN_C, GPIO.LOW)
            pwm_c.ChangeDutyCycle(abs(speed_limited))
        
        time.sleep(0.2)  # Delay for steering motion
        pwm_c.ChangeDutyCycle(0)  # Stop steering after movement

    threading.Thread(target=run_motor, daemon=True).start()

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

# Flask API Routes
# Flask routes
@app.route('/')
def index():
    return render_template('Controls.html')

@app.route('/move', methods=['POST'])
def move():
    global emergency_stop_active
    if emergency_stop_active:
        return jsonify(message="Emergency stop is active!"), 400

    direction = request.form.get('direction')
    if not direction:
        return jsonify(message="Missing direction parameter."), 400

    distance = measure_distance()
    if direction == "forward" and 0 <= distance < 150:
        return jsonify(message="Obstacle detected! Cannot move forward."), 400

    movement_map = {
        "forward": lambda: set_motor_a_speed(20),
        "backward": lambda: set_motor_a_speed(-20),
        "left": lambda: set_motor_c_direction(-100),
        "right": lambda: set_motor_c_direction(100),
        "stop": lambda: (set_motor_a_speed(0), set_motor_c_direction(0)),
    }

    if direction in movement_map:
        movement_map[direction]()
        return jsonify(message=f"Moving {direction}"), 200
    else:
        return jsonify(message="Invalid direction!"), 400

@app.route('/release_emergency', methods=['POST'])
def release_emergency():
    global emergency_stop_active
    emergency_stop_active = False  
    return jsonify(message="Emergency stop released. You can now control the rover."), 200

@app.route('/emergency_stop', methods=['POST'])
def emergency_stop():
    global emergency_stop_active
    emergency_stop_active = True
    
    def stop_motors():
        set_motor_a_speed(0)
        set_motor_c_direction(0)
    
    stop_thread = threading.Thread(target=stop_motors, daemon=True)
    stop_thread.start()

    return jsonify(message="Emergency stop activated! Use 'Release Emergency' to continue."), 200

@app.route('/soft_stop', methods=['POST'])
def soft_stop():
    def stop_motors():
        set_motor_a_speed(0)
        set_motor_c_direction(0)

    stop_thread = threading.Thread(target=stop_motors, daemon=True)
    stop_thread.start()

    return jsonify(message="Soft Stop activated!"), 200
@app.route('/record', methods=['POST'])
def record():
    action = request.form.get('action')
    if action == "start":
        os.system("ffmpeg -f v4l2 -i /dev/video0 -t 10 /home/pi/video.mp4 &")
        return jsonify(message="Recording started."), 200
    elif action == "stop":
        os.system("pkill -f ffmpeg")
        return jsonify(message="Recording stopped."), 200
    else:
        return jsonify(message="Invalid action! Use 'start' or 'stop'."), 400

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
    except KeyboardInterrupt:
        pass
    finally:
        pwm_a.stop()
        pwm_c.stop()
        GPIO.cleanup()
