from flask import Flask, render_template, request
import RPi.GPIO as GPIO
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

# Maximum duty cycle (adjust as necessary for your motor)
MAX_DUTY_CYCLE = 50

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

# Global variables for video recording
recording = False
video_writer = None
camera = None

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
def set_motor_c_direction(steering):
    steering = max(min(steering, MAX_DUTY_CYCLE), -MAX_DUTY_CYCLE)  # Clamp value to duty cycle limits
    if steering > 0:
        GPIO.output(DIR_PIN_C, GPIO.HIGH)  # Turn right
        pwm_c.ChangeDutyCycle(steering)
    elif steering < 0:
        GPIO.output(DIR_PIN_C, GPIO.LOW)  # Turn left
        pwm_c.ChangeDutyCycle(abs(steering))
    else:
        pwm_c.ChangeDutyCycle(0)  # Center steering (no turning)

# Function to handle video recording
def record_video():
    global recording, video_writer, camera
    camera = cv2.VideoCapture('/dev/video1')  # Use the correct device path
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camera.set(cv2.CAP_PROP_FPS, 20)

    if not camera.isOpened():
        print("Failed to open camera")
        return

    while recording:
        ret, frame = camera.read()
        if ret:
            video_writer.write(frame)
        else:
            print("Failed to capture frame")
            break

    camera.release()
    video_writer.release()


# Flask routes to render the webpage and handle motor control
@app.route('/')
def index():
    return render_template('control.html')

@app.route('/move', methods=['POST'])
def move():
    direction = request.form.get('direction')
    speed = int(request.form.get('speed', 50))  # Default speed is 50
    steering = int(request.form.get('steering', 0))  # Default steering is 0 (center)

    if direction == "forward":
        set_motor_a_speed(speed)  # Move forward at the specified speed
    elif direction == "backward":
        set_motor_a_speed(-speed)  # Move backward at the specified speed
    elif direction == "stop":
        set_motor_a_speed(0)  # Stop Motor A
        set_motor_c_direction(0)  # Center the steering (stop turning)
    else:
        # Apply steering for left/right tuning
        set_motor_c_direction(steering)

    return "OK", 200

@app.route('/record', methods=['POST'])
def record():
    global recording, video_writer
    action = request.form.get('action')
    
    if action == 'start' and not recording:
        recording = True
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"recordings/recording_{now}.avi"
        os.makedirs("recordings", exist_ok=True)

        # VideoWriter for saving the video
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video_writer = cv2.VideoWriter(output_file, fourcc, 20.0, (640, 480))
        
        threading.Thread(target=record_video).start()
        return "Recording started", 200
    elif action == 'stop' and recording:
        recording = False
        return "Recording stopped", 200
    else:
        return "Invalid action or recording already in progress", 400

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        pass
    finally:
        pwm_a.stop()  # Stop PWM for Motor A
        pwm_c.stop()  # Stop PWM for Motor C
        GPIO.cleanup()  # Clean up GPIO on exit
