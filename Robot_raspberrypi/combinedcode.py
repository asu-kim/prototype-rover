from flask import Flask, render_template, request
import RPi.GPIO as GPIO
import time
import cv2
import os
from datetime import datetime
import threading
import atexit

# Initialize the Flask application
app = Flask(__name__)

# GPIO pin assignments
# Motor Driver A (forward and backward)
DIR_PIN_A = 17  # GPIO17 for direction (forward/backward)
PWM_PIN_A = 18  # GPIO18 for speed (PWM)

# Motor Driver C (left and right)
DIR_PIN_C = 22  # GPIO22 for direction (left/right)
PWM_PIN_C = 23  # GPIO23 for speed (PWM)

# Ultrasonic sensor
TRIG = 24  # GPIO24 for trigger
ECHO = 25  # GPIO25 for echo

# Maximum duty cycles
MAX_DUTY_CYCLE = 50  # Adjust for Motor A
STEERING_DUTY_CYCLE = 100  # Adjust for Motor C

# Video recording variables
recording = False
camera = None
video_writer = None

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN_A, GPIO.OUT)
GPIO.setup(PWM_PIN_A, GPIO.OUT)
GPIO.setup(DIR_PIN_C, GPIO.OUT)
GPIO.setup(PWM_PIN_C, GPIO.OUT)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Initialize PWM for both motor drivers
pwm_a = GPIO.PWM(PWM_PIN_A, 5000)  # Motor A PWM at 5kHz
pwm_c = GPIO.PWM(PWM_PIN_C, 5000)  # Motor C PWM at 5kHz
pwm_a.start(0)  # Start with 0% duty cycle
pwm_c.start(0)  # Start with 0% duty cycle

# Register cleanup for GPIO pins
atexit.register(GPIO.cleanup)

# Function to control Motor A (forward and backward)
def set_motor_a_speed(speed):
    speed = max(min(speed, MAX_DUTY_CYCLE), -MAX_DUTY_CYCLE)
    if speed > 0:
        GPIO.output(DIR_PIN_A, GPIO.LOW)  # Forward
        pwm_a.ChangeDutyCycle(speed)
    elif speed < 0:
        GPIO.output(DIR_PIN_A, GPIO.HIGH)  # Reverse
        pwm_a.ChangeDutyCycle(abs(speed))
    else:
        pwm_a.ChangeDutyCycle(0)  # Stop

# Function to control Motor C (left and right)
def set_motor_c_direction(speed):
    speed = max(min(speed, STEERING_DUTY_CYCLE), -STEERING_DUTY_CYCLE)
    if speed > 0:
        GPIO.output(DIR_PIN_C, GPIO.HIGH)  # Right
        pwm_c.ChangeDutyCycle(speed)
        time.sleep(0.2)
    elif speed < 0:
        GPIO.output(DIR_PIN_C, GPIO.LOW)  # Left
        pwm_c.ChangeDutyCycle(abs(speed))
        time.sleep(0.2)
    pwm_c.ChangeDutyCycle(0)  # Stop steering after turning

# Function to measure distance with the ultrasonic sensor
def measure_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.2)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)

# Video recording function
def record_video():
    global recording, camera, video_writer
    camera = cv2.VideoCapture('/dev/video0')
    if not camera.isOpened():
        print("Failed to open camera")
        return

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("recordings", exist_ok=True)
    output_file = f"recordings/recording_{now}.avi"

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_writer = cv2.VideoWriter(output_file, fourcc, 20.0, (640, 480))

    while recording:
        ret, frame = camera.read()
        if ret:
            video_writer.write(frame)
        else:
            print("Failed to capture frame")
            break

    camera.release()
    video_writer.release()

# Flask routes
@app.route('/')
def index():
    distance = measure_distance()
    return render_template('control.html', distance=distance)

@app.route('/move', methods=['POST'])
def move():
    direction = request.form.get('direction')

    if direction == "forward":
        set_motor_a_speed(50)
    elif direction == "backward":
        set_motor_a_speed(-50)
    elif direction == "left":
        set_motor_c_direction(-10)
    elif direction == "right":
        set_motor_c_direction(10)
    elif direction == "stop":
        set_motor_a_speed(0)
        set_motor_c_direction(0)

    return "OK", 200

@app.route('/record', methods=['POST'])
def record():
    global recording
    action = request.form.get('action')

    if action == 'start' and not recording:
        recording = True
        threading.Thread(target=record_video).start()
    elif action == 'stop' and recording:
        recording = False

    return "OK", 200

# Optional route to trigger GPIO cleanup manually
@app.route('/cleanup', methods=['POST'])
def cleanup():
    GPIO.cleanup()
    return "GPIO cleanup completed", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
