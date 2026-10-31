# Lab 1 – Program diffdrive_bot

## Introduction

This project implements the Lab 1 exercises for Introduction to Robotics and Intelligent Systems using ROS 2 Humble and Gazebo Harmonic.

The goal is to extend the `diffdrive_bot` robot with additional sensors, obstacle detection, motion control, ROS 2 services, custom interfaces, and action-based navigation.

## Requirements

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Harmonic
- Python 3
- `colcon`
- Required ROS 2 packages and dependencies

## Project Structure

```text
lab1_exercise/
├── diffdrive_bot/
├── lab_interfaces/
├── my_robot_interfaces/
├── my_robot_nodes/
└── README.md
```

## Implemented Exercises

### Step 1 – Sensors and ROS-Gazebo Bridges
- Added a depth camera to the robot.
- Added an IMU sensor.
- Configured ROS-Gazebo bridges for sensor topics.
- Verified depth images, point clouds, and IMU data.

### Step 2 – Obstacle Avoidance
- Implemented the `turn_away` node.
- Subscribed to `/obstacle`.
- Published velocity commands to `/cmd_vel`.
- Made the robot move forward when the path is clear and turn away when an obstacle is too close.

### Step 3 – ROS 2 Parameters
- Added configurable `forward_speed` and `turn_speed` parameters.
- Tested runtime parameter updates.

### Step 4 – Robot Status
- Created the custom `RobotStatus` message.
- Published robot states through `/robot_status`.
- Reported `forward` and `turning` states, including obstacle distance.

### Step 5 – ROS 2 Services
- Implemented `/turn_away_enable` to enable or disable obstacle avoidance.
- Created the custom `SetTurnSpeed` service.
- Added validation using the `max_turn_speed` parameter.

### Step 6 – Rotate Action
- Created the custom `Rotate` action.
- Implemented the `rotate_server` action server.
- Used odometry to measure rotation.
- Supported feedback, goal rejection, and cancellation.

### Step 7 – Square Driver
- Implemented the `square_driver` action client.
- Used the `/drive_distance` and `/rotate` actions.
- Added a configurable `side_length` parameter.
- Executed four driving goals and four 90-degree rotation goals.
- Verified successful completion of the square in Gazebo.

## Build Instructions

Open a terminal and run:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-up-to my_robot_nodes
source ~/ros2_ws/install/setup.bash
```

## Run the Square Driver

```bash
ros2 launch my_robot_nodes square.launch.py
```

To change the square side length:

```bash
ros2 launch my_robot_nodes square.launch.py side_length:=1.0
```

## Evidence

Screenshots demonstrating sensor operation, obstacle avoidance, service tests, rotation action execution, and successful square navigation are included in the project submission.

## Reflection

This lab provided practical experience with ROS 2 nodes, topics, parameters, custom messages, services, actions, and Gazebo simulation. It also helped develop a better understanding of robot sensing, odometry, motion control, and communication between ROS 2 components.

## Author

Fiker Mesfin
