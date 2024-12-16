from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='robot_control',
            executable='gpio_control',
            name='gpio_control',
            output='screen',
        ),
        Node(
            package='robot_control',
            executable='web_server',
            name='web_server',
            output='screen',
        ),
    ])
