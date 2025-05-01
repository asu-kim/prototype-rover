from flask import Flask, render_template, request, jsonify
import os
import sys
import RPi.GPIO as GPIO
import time
import threading
import cv2
from datetime import datetime

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

# Video recording variables
recording = False
camera = None
video_writer = None
record_lock = threading.Lock()
last_record_stop_time = 0

# Global emergency stop flag
emergency_stop_active = False
latest_distance = 1000

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

# Function to measure distance
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

# Function to update distance in a thread
def ultrasonic_distance_updater():
    global latest_distance
    while True:
        try:
            distance = measure_distance()
            latest_distance = distance
            time.sleep(0.1)  # Update every 100 ms
        except Exception as e:
            print(f"Ultrasonic sensor error: {e}")
            latest_distance = 1000  # Safe default
            time.sleep(0.5)

def obstacle_monitor():
    global latest_distance, emergency_stop_active
    while True:
        if not emergency_stop_active:
            if 0 <= latest_distance < 50:
                print(f"Obstacle detected during motion: {latest_distance:.1f} cm! Stopping motors.")
                set_motor_a_speed(0)
                set_motor_c_direction(0)
                # Optional: you can even activate emergency stop here
                # emergency_stop_active = True
        time.sleep(0.1)  # Check every 100 ms

# Video recording function
def record_video():
    global recording, camera, video_writer

    with record_lock:
        print("Trying to open camera...")

        try:
            camera = cv2.VideoCapture('/dev/video0') 
            if not camera.isOpened():
                print("Failed to open camera")
                recording = False
                return

            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs("recordings", exist_ok=True)
            output_file = f"recordings/recording_{now}.avi"

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            video_writer = cv2.VideoWriter(output_file, fourcc, 20.0, (640, 480))

            print(f"Recording to {output_file}")

            while recording:
                ret, frame = camera.read()
                if not ret:
                    print("Failed to capture frame")
                    recording = False
                    break
                video_writer.write(frame)

        except Exception as e:
            print(f"Exception during recording: {e}")
            recording = False

        finally:
            if camera:
                camera.release()
                camera = None 
            if video_writer:
                video_writer.release()
                video_writer = None

            print("Camera and writer released.")
            time.sleep(1)  # Ensure OS finishes releasing resources

# Flask API Routes
# Flask routes
@app.route('/')
def index():
    return render_template('Controls.html')

@app.route('/move', methods=['POST'])
def move():
    global emergency_stop_active, latest_distance
    if emergency_stop_active:
        return jsonify(message="Emergency stop is active!"), 400

    direction = request.form.get('direction')
    print("MOVE API CALLED with direction:", direction)
    if not direction:
        return jsonify(message="Missing direction parameter."), 400

    if direction == "forward" and 0 <= latest_distance < 100:
        return jsonify(message=f"Obstacle detected {latest_distance:.1f}cm! Cannot move forward."), 400

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
    global recording
    action = request.form.get('action')

    if action == 'start' and not recording:
        recording = True
        threading.Thread(target=record_video).start()
        return "Recording started", 200
    elif action == 'stop' and recording:
        recording = False
        return "Recording stopped", 200
    else:
        return "Invalid action", 400

if __name__ == '__main__':
    try:
        # Start ultrasonic sensor updater thread
        ultrasonic_thread = threading.Thread(target=ultrasonic_distance_updater, daemon=True)
        ultrasonic_thread.start()

        # Start obstacle monitor thread
        obstacle_thread = threading.Thread(target=obstacle_monitor, daemon=True)
        obstacle_thread.start()

        app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
    except KeyboardInterrupt:
        pass
    finally:
        pwm_a.stop()
        pwm_c.stop()
        GPIO.cleanup()
