import subprocess
from flask import Flask, render_template, request
import RPi.GPIO as GPIO

# Initialize the Flask application
app = Flask(__name__)

# Function to disconnect active connections
def disconnect_active_connections():
    try:
        # Get the list of active connections
        result = subprocess.run(["nmcli", "connection", "show", "--active"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode().strip()

        # If there's an active connection, extract the connection name and disconnect it
        if "wlan0" in output:
            lines = output.split("\n")
            for line in lines:
                if "wlan0" in line:
                    connection_name = line.split()[0]
                    print(f"Disconnecting from active connection: {connection_name}")
                    subprocess.run(["nmcli", "connection", "down", connection_name], check=True)
                    break
    except subprocess.CalledProcessError as e:
        print(f"Error while disconnecting active connections: {e}")

# Function to start a hotspot
def start_hotspot(ssid, password):
    try:
        # Disconnect any active connections on wlan0
        disconnect_active_connections()

        # Start the hotspot without turning off Wi-Fi
        subprocess.run([
            "nmcli", "dev", "wifi", "hotspot",
            "ifname", "wlan0",  # Adjust wlan0 if necessary
            "con-name", ssid,
            "ssid", ssid,
            "password", password
        ], check=True)

        print(f"Hotspot '{ssid}' started successfully with password '{password}'")
    except subprocess.CalledProcessError as e:
        print(f"Failed to start hotspot. Error: {e}")
        print(e.stdout.decode())
        print(e.stderr.decode())

# GPIO pin assignments for Motor Driver A (forward and backward)
DIR_PIN_A = 17  # GPIO17 for direction (forward/backward)
PWM_PIN_A = 18  # GPIO18 for speed (PWM)

# GPIO pin assignments for Motor Driver C (left and right)
DIR_PIN_C = 22  # GPIO22 for direction (left/right)
PWM_PIN_C = 23  # GPIO23 for speed (PWM)

# Maximum duty cycle (adjust as necessary for your motor)
MAX_DUTY_CYCLE = 100

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

# Function to control Motor A (forward and backward)
def set_motor_a_speed(speed):
    speed = max(min(speed, MAX_DUTY_CYCLE), -MAX_DUTY_CYCLE)  # Limit speed to 100%
    if speed > 0:
        GPIO.output(DIR_PIN_A, GPIO.HIGH)  # Forward direction
        pwm_a.ChangeDutyCycle(speed)
    elif speed < 0:
        GPIO.output(DIR_PIN_A, GPIO.LOW)  # Reverse direction
        pwm_a.ChangeDutyCycle(abs(speed))
    else:
        pwm_a.ChangeDutyCycle(0)  # Stop motor A

# Function to control Motor C (left and right)
def set_motor_c_direction(speed):
    speed = max(min(speed, MAX_DUTY_CYCLE), -MAX_DUTY_CYCLE)  # Limit speed to 100%
    if speed > 0:
        GPIO.output(DIR_PIN_C, GPIO.HIGH)  # Turn right
        pwm_c.ChangeDutyCycle(speed)
    elif speed < 0:
        GPIO.output(DIR_PIN_C, GPIO.LOW)  # Turn left
        pwm_c.ChangeDutyCycle(abs(speed))
    else:
        pwm_c.ChangeDutyCycle(0)  # Stop Motor C (no steering)

# Flask routes to render the webpage and handle motor control
@app.route('/')
def index():
    return render_template('control.html')

@app.route('/move', methods=['POST'])
def move():
    direction = request.form.get('direction')
    
    if direction == "forward":
        set_motor_a_speed(100)  # Move forward at full speed
    elif direction == "backward":
        set_motor_a_speed(-100)  # Move backward at full speed
    elif direction == "left":
        set_motor_c_direction(-100)  # Turn left at full speed
    elif direction == "right":
        set_motor_c_direction(100)  # Turn right at full speed
    elif direction == "stop":
        set_motor_a_speed(0)  # Stop Motor A
        set_motor_c_direction(0)  # Stop Motor C (no steering)
    
    return "OK", 200

if __name__ == '__main__':
    try:
        # Start the hotspot before starting the Flask app
        ssid = "Robot"
        password = "123456789"
        start_hotspot(ssid, password)

        # Start the Flask app
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        pass
    finally:
        pwm_a.stop()  # Stop PWM for Motor A
        pwm_c.stop()  # Stop PWM for Motor C
        GPIO.cleanup()  # Clean up GPIO on exit
