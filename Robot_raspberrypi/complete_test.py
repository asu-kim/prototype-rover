import cv2
import RPi.GPIO as GPIO
import time

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# GPIO pins for ultrasonic sensor
TRIG = 23
ECHO = 24

# GPIO pins for GPIO test
output_pin = 17
input_pin = 18

def camera_test():
    """Test the camera functionality."""
    print("\nStarting Camera Test...")
    camera = cv2.VideoCapture('/dev/video0')  # Replace with your correct device
    if camera.isOpened():
        ret, frame = camera.read()
        if ret:
            print("Camera works! Capturing test image...")
            cv2.imwrite("test_image.jpg", frame)
            print("Test image saved as 'test_image.jpg'")
        else:
            print("Failed to capture frame.")
    else:
        print("Camera not detected or inaccessible.")
    camera.release()
    print("Camera Test Complete.\n")

def ultrasonic_test():
    """Test the ultrasonic sensor."""
    print("\nStarting Ultrasonic Sensor Test...")
    
    # Set up GPIO pins
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    
    try:
        while True:
            print("Measuring distance...")
            # Ensure TRIG is low
            GPIO.output(TRIG, False)
            time.sleep(0.2)
            
            # Generate a 10-microsecond pulse on TRIG
            GPIO.output(TRIG, True)
            time.sleep(0.00001)
            GPIO.output(TRIG, False)
            
            # Measure the time for the echo
            while GPIO.input(ECHO) == 0:
                pulse_start = time.time()
            while GPIO.input(ECHO) == 1:
                pulse_end = time.time()
            
            # Calculate the distance
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150
            distance = round(distance, 2)
            
            # Display the distance
            print(f"Distance: {distance} cm")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nUltrasonic Sensor Test Stopped.")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup complete.\n")

def gpio_test():
    """Test GPIO input and output functionality."""
    print("\nStarting GPIO Test...")
    # Set up GPIO pins
    GPIO.setup(output_pin, GPIO.OUT)
    GPIO.setup(input_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    try:
        # Test GPIO functionality
        print("Testing GPIO pins 17 (output) and 18 (input)...")
        
        # Set the output pin HIGH
        GPIO.output(output_pin, GPIO.HIGH)
        time.sleep(1)  # Wait for the change to be reflected
        
        # Check the input pin state
        if GPIO.input(input_pin) == GPIO.HIGH:
            print("GPIO 18 detected HIGH (Output from GPIO 17 is working)")
        else:
            print("GPIO 18 failed to detect HIGH (Check wiring or GPIO 17)")
        
        # Set the output pin LOW
        GPIO.output(output_pin, GPIO.LOW)
        time.sleep(1)  # Wait for the change to be reflected

        # Check the input pin state again
        if GPIO.input(input_pin) == GPIO.LOW:
            print("GPIO 18 detected LOW (Output from GPIO 17 is working)")
        else:
            print("GPIO 18 failed to detect LOW (Check wiring or GPIO 17)")
    except KeyboardInterrupt:
        print("\nGPIO Test Interrupted.")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup complete.\n")

def main():
    """Main menu to select which test to run."""
    while True:
        print("\nSelect a test to run:")
        print("1. Camera Test")
        print("2. Ultrasonic Sensor Test")
        print("3. GPIO Test")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            camera_test()
        elif choice == '2':
            ultrasonic_test()
        elif choice == '3':
            gpio_test()
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
