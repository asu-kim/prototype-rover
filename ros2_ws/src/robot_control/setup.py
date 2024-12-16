from setuptools import setup

package_name = 'robot_control'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/robot_control_launch.py']),
        ('share/' + package_name + '/templates', ['templates/control.html']),
        ('share/' + package_name + '/static', ['static/forward.jpg', 'static/backward.jpg']),
    ],
    install_requires=['setuptools', 'flask', 'RPi.GPIO'],
    zip_safe=True,
    maintainer='pk',
    maintainer_email='saipavan4@gmail.com',
    description='ROS 2 package for motor control',
    license='Apache License 2.0',
    entry_points={
        'console_scripts': [
	    'gpio_control = robot_control.gpio_control:main',
            'web_server = robot_control.web_server:main',
        ],
    },
)
