from flask import Flask, render_template, request
import RPi.GPIO as GPIO
import time
import cv2
import os
from datetime import datetime
import threading

# Initialize the Flask application
app = Flask(__name__)

# GPIO pin assignments for Motor Driver A (forward and backward)
DIR_PIN_A = 17  # GPIO17 for direction (forward/backward)
PWM_PIN_A = 18  # GPIO18 for speed (PWM)

# GPIO pin assignments for Motor Driver C (left and right)
DIR_PIN_C = 22  # GPIO22 for direction (left/right)
PWM_PIN_C = 23  # GPIO23 for speed (PWM)

# Ultrasonic sensor pins
TRIG = 24  # GPIO24 for trigger
ECHO = 25  # GPIO25 for echo

# Maximum duty cycle for the motors
MAX_DUTY_CYCLE = 50  # Adjust this for motor A (main movement)
STEERING_DUTY_CYCLE = 100  # Lower duty cycle for steering to slow it down

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
pwm_a = GPIO.PWM(PWM_PIN_A, 5000)  # PWM for Motor A at 5kHz
pwm_c = GPIO.PWM(PWM_PIN_C, 40000)  # PWM for Motor C at 5kHz
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
    camera = cv2.VideoCapture('/dev/video0')  # Use the correct device path
    if not camera.isOpened():
        print("Failed to open camera")
        return

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("recordings", exist_ok=True)
    output_file = f"recordings/recording_{now}.avi"

    # Set up video writer
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
    distance = measure_distance()

    if direction == "forward":
        if distance < 150:
            return "Obstacle too close! Cannot move forward.", 400
        set_motor_a_speed(50)
    elif direction == "backward":
        if distance < 150:
            return "Obstacle too close! Cannot move backward.", 400
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
        return "Recording started", 200
    elif action == 'stop' and recording:
        recording = False
        return "Recording stopped", 200
    else:
        return "Invalid action", 400

@app.route('/stop', methods=['POST'])
def stop():
    set_motor_a_speed(0)
    set_motor_c_direction(0)
    print("Emergency Stop activated")
    return "Emergency Stop activated!", 200

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        pass
    finally:
        pwm_a.stop()
        pwm_c.stop()
        GPIO.cleanup()
