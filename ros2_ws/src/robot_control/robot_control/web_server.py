from flask import Flask, render_template, request
import pyrealsense2 as rs
import RPi.GPIO as GPIO
import os
import threading
from datetime import datetime  # Import the missing module

# Flask setup
app = Flask(__name__, 
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
pwm_c = GPIO.PWM(PWM_PIN_C, 5000)  # Turn control for Motor C
pwm_a.start(0)
pwm_c.start(0)

# Global variables for recording
pipeline = None
recording = False
output_file = None

# Helper functions for GPIO
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

# Video recording functions
def start_recording():
    global pipeline, recording, output_file
    try:
        pipeline = rs.pipeline()
        config = rs.config()

        # Generate a filename based on date and time
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = os.path.join(os.getcwd(), f"recorded_video_{timestamp}.avi")
        config.enable_record_to_file(output_file)

        # Configure the stream
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

        # Start the pipeline
        pipeline.start(config)
        recording = True

        print(f"Recording started. Saving to {output_file}")

        # Test if frames are being captured
        for _ in range(10):  # Test for a few frames
            frames = pipeline.wait_for_frames(timeout_ms=5000)
            if frames and frames.get_color_frame():
                print("Color frame detected.")
                break
        else:
            raise RuntimeError("No frames detected. Camera stream is not working.")

    except Exception as e:
        print(f"Error starting recording: {e}")
        stop_recording()  # Stop pipeline if there's an error

def stop_recording():
    global pipeline, recording
    try:
        if pipeline:
            pipeline.stop()
        recording = False
        print(f"Recording stopped. File saved to {output_file}")
    except Exception as e:
        print(f"Error stopping recording: {e}")

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

@app.route('/record', methods=['POST'])
def record():
    action = request.form.get('action')
    if action == 'start':
        if not recording:
            threading.Thread(target=start_recording).start()
    elif action == 'stop':
        if recording:
            stop_recording()
    return "OK", 200

def main():
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        pwm_a.stop()
        pwm_c.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
