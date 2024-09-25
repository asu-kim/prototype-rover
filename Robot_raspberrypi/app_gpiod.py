from flask import Flask, render_template, request
import gpiod

# Initialize Flask application
app = Flask(__name__)

# GPIO chip and line setup (replace 'gpiochip0' if needed)
chip = gpiod.Chip('gpiochip0')

# Set up lines (GPIO pin numbers, not physical pin numbers)
DIR_PIN_A = 17  # Direction pin for Motor A
PWM_PIN_A = 18  # PWM pin for Motor A (simulated)
PIN_A_C = 22    # Direction control pin A for Motor C
PIN_B_C = 23    # Direction control pin B for Motor C

# Request lines
line_dir_a = chip.get_line(DIR_PIN_A)
line_pwm_a = chip.get_line(PWM_PIN_A)
line_a_c = chip.get_line(PIN_A_C)
line_b_c = chip.get_line(PIN_B_C)

# Configure lines as outputs
line_dir_a.request(consumer='motor_a_dir', type=gpiod.LINE_REQ_DIR_OUT)
line_pwm_a.request(consumer='motor_a_pwm', type=gpiod.LINE_REQ_DIR_OUT)
line_a_c.request(consumer='motor_c_a', type=gpiod.LINE_REQ_DIR_OUT)
line_b_c.request(consumer='motor_c_b', type=gpiod.LINE_REQ_DIR_OUT)

# Function to control motor A speed (simulated PWM using sleep)
def set_motor_a_speed(speed):
    if speed > 0:
        line_dir_a.set_value(1)  # Set direction to forward
        line_pwm_a.set_value(1)  # Turn motor on (simulate PWM)
        print("Motor A: Forward at speed", speed)
    elif speed < 0:
        line_dir_a.set_value(0)  # Set direction to reverse
        line_pwm_a.set_value(1)  # Turn motor on (simulate PWM)
        print("Motor A: Backward at speed", abs(speed))
    else:
        line_pwm_a.set_value(0)  # Stop motor A
        print("Motor A: Stopped")

# Function to control Motor C direction
def set_motor_c_direction(direction):
    if direction == "right":
        line_a_c.set_value(1)
        line_b_c.set_value(0)
        print("Motor C: Turning right")
    elif direction == "left":
        line_a_c.set_value(0)
        line_b_c.set_value(1)
        print("Motor C: Turning left")
    else:
        line_a_c.set_value(0)
        line_b_c.set_value(0)  # Stop motor C
        print("Motor C: Stopped")

# Flask route to render the webpage
@app.route('/')
def index():
    return render_template('control.html')

# Flask route to handle movement requests
@app.route('/move', methods=['POST'])
def move():
    direction = request.form.get('direction')
    
    if direction == "forward":
        set_motor_a_speed(25)  # Move forward at speed 25
    elif direction == "backward":
        set_motor_a_speed(-25)  # Move backward at speed 25
    elif direction == "left":
        set_motor_c_direction("left")  # Turn motor C left
    elif direction == "right":
        set_motor_c_direction("right")  # Turn motor C right
    elif direction == "stop":
        set_motor_a_speed(0)  # Stop motor A
        set_motor_c_direction("stop")  # Stop motor C
    
    return "OK", 200

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        pass
    finally:
        # Cleanup GPIO on exit
        line_dir_a.set_value(0)
        line_pwm_a.set_value(0)
        line_a_c.set_value(0)
        line_b_c.set_value(0)
        print("GPIO cleanup completed")
