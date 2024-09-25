from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

# Flask routes to render the webpage and handle actions
@app.route('/')
def index():
    return render_template('control.html')

@app.route('/move', methods=['POST'])
def move():
    direction = request.form.get('direction')
    
    # Handle the direction command (up, down, left, right, stop)
    if direction == "up":
        print("Moving up")
        # Add the code here to move in the "up" direction
    elif direction == "down":
        print("Moving down")
        # Add the code here to move in the "down" direction
    elif direction == "left":
        print("Moving left")
        # Add the code here to move in the "left" direction
    elif direction == "right":
        print("Moving right")
        # Add the code here to move in the "right" direction
    elif direction == "stop":
        print("Stopping")
        # Add the code to stop here
    
    return "OK", 200

if __name__ == '__main__':
    # Run the Flask web server on all interfaces so it's accessible
    app.run(host='0.0.0.0', port=5000)
