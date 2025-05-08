# Overview
This is our repository of the working implementation of our prototype rover using webpage

## Demo Videos

### Rover working in the citrus farm
[![Rover video ](https://img.youtube.com/vi/w_ep-jKaQc/0.jpg)](https://www.youtube.com/watch?v=w_ep-jKaQc)

### Fruit counting analysis application
[![Fruit counting application](https://img.youtube.com/vi/kfau-Py49ds/0.jpg)](https://www.youtube.com/watch?v=kfau-Py49ds)([https://www.youtube.com/watch?v=VIDEO_ID2](https://www.youtube.com/shorts/kfau-Py49ds))

# Prerequisites 

You need Python installed, as the main scripts are written in Python.

## Library Dependencies
The following dependencies are required to run this project.
  
```
pip install flask RPi.GPIO opencv-python-headless

```
## To run the code

### Step 1 (if you are attaching a USB camera to the Raspberry Pi to record data, else skip to Step 2)

``` 
lsusb
 ```
- Check if the USB camera is detected (lists connected USB devices).

``` 
ls /dev/video*
```

- Find the video device port (e.g., /dev/video0, /dev/video1).

``` 
sudo python3 cam_test.py
```

- Test and verify the correct camera port. 
- Ensure the script runs properly and confirms the camera is working.

### Step 2

``` 
sudo python3 rover.py
```

- Update the camera port inside the code if necessary based on Step 1 results.
- You need to make the circuit connections as shown in ``` Circuit_toy_car.pdf ``` and refer ``` rover.py ``` for the GPIO pins. If any changes made should be made in the code.
- Run this program to control the rover through the web interface.
- Do not change any of the files in static and templates folders.
- Files in Robot_raspberrypi can be ignored. they are the previous codes used for building the prototype rover

# Contributors
- Pawan Kumar (pkumar97@asu.edu), Ph.D. student at Arizona State University
- Yejur Dube (ydube@asu.edu), Masters student at Arizona State University
- Hokeun Kim (hokeun@asu.edu, https://hokeun.github.io/), Assistant professor at Arizona State University 
