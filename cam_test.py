import pyrealsense2 as rs

pipeline = rs.pipeline()
config = rs.config()

config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

try:
    pipeline.start(config)
    print("Camera is streaming. Press Ctrl+C to stop.")
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if color_frame:
            print("Color frame detected.")
except Exception as e:
    print(f"Error: {e}")
finally:
    pipeline.stop()
