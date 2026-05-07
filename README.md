# El-Fanan: Turtle Catching Robot System

[![Watch the video](https://img.youtube.com/vi/VvY_FBQFREU/maxresdefault.jpg)](https://youtu.be/VvY_FBQFREU)

## Overview

El-Fanan is a ROS2 system that autonomously catches turtles in a simulated TurtleSim environment using real-time tracking and intelligent movement control.

## Packages

**elfanan_pkg**: Core control nodes
- `elfanan_controller`: Tracks and catches the closest turtle
- `elfanan_spawner`: Spawns turtles and manages the catch service

**my_robot_interfaces**: Custom ROS2 messages and services
- `Turtle.msg`: Single turtle data (name, x, y, theta)
- `TurtleArray.msg`: Array of turtles
- `CatchTurtle.srv`: Service to catch turtles

**my_robot_bringup**: Launch files and configuration
- `turtlesim_catch_them_all.launch.xml`: Main launch file
- `catch_them_all_config.yaml`: Parameter configuration

## Quick Start

```bash
# Build
cd ~/ros2_ws && colcon build

# Run
source install/setup.bash
ros2 launch my_robot_bringup turtlesim_catch_them_all.launch.xml
```

## How It Works

1. Spawner creates random turtles and publishes the alive turtle list
2. Controller receives the turtle list and identifies the closest one
3. Controller calculates movement commands toward the target
4. When close enough, controller calls the catch service
5. Spawner removes the caught turtle and process repeats

## Configuration

Edit `catch_them_all_config.yaml`:
- `catch_closest_turtle_first`: Enable/disable closest-turtle targeting
- `turtle_frequency`: Spawn rate (Hz)
- `turtle_name`: Prefix for spawned turtles

## Dependencies

ROS2, rclpy, turtlesim, geometry_msgs

---

**Maintainer**: kerolus | **Updated**: May 2026
