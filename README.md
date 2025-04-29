# Overview
This is our repository of the working implementation of our prototype rover using webpage

# Prerequisites 

You need Python installed, as the main scripts are written in Python.

## Library Dependencies
The following dependencies are required to run this project.
  
```
pip install flask RPi.GPIO opencv-python opencv-python-headless

```
### To run the code

In the terminal, go to the `Robot_raspberrypi` directory:

```bash
# Step 1 (if you are attaching a USB camera to the Raspberry Pi to record data, else skip to Step 2)

``` lsusb ```
# Check if the USB camera is detected (lists connected USB devices).

``` ls /dev/video* ```
# Find the video device port (e.g., /dev/video0, /dev/video1).

``` sudo python3 cam_test.py ```
# Test and verify the correct camera port. 
# Ensure the script runs properly and confirms the camera is working.

# Step 2

``` sudo python3 newrover_3.py ```
# Update the camera port inside the code if necessary based on Step 1 results.
# Run this program to control the rover through the web interface.

# Contributors
- Pawan Kumar (pkumar97@asu.edu), Ph.D. student at Arizona State University
- Hokeun Kim (hokeun@asu.edu, https://hokeun.github.io/), Assistant professor at Arizona State University 
