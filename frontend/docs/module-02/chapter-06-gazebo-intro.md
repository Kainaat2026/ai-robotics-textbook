---
id: chapter-06-gazebo-intro
title: Gazebo Simulation - Virtual Robot Testing
module: 2
week: 4
learning_objectives:
  - Set up Gazebo Fortress for robot simulation
  - Create robot models using URDF/SDF formats
  - Integrate Gazebo with ROS 2
  - Simulate sensors (cameras, LiDAR, IMU)
  - Test robot controllers in simulation
estimated_time_minutes: 90
---

# Gazebo Simulation - Virtual Robot Testing

## Introduction

Gazebo is the industry-standard 3D robot simulator used for testing ROS 2 applications. It provides physics simulation, sensor emulation, and realistic environments - allowing you to develop and test robot software without physical hardware.

## Why Simulation?

### Benefits of Simulation

1. **Safe Testing**: Test dangerous scenarios without risk
2. **Cost Effective**: No hardware damage or wear
3. **Rapid Iteration**: Fast testing cycles
4. **Reproducibility**: Same conditions every time
5. **Scalability**: Test multiple robots simultaneously

### Simulation vs Real World

Simulators approximate reality but have limitations:
- Physics approximations
- Sensor noise models
- Computational constraints
- The "sim-to-real gap"

## Installing Gazebo Fortress

Gazebo Fortress is the recommended version for ROS 2 Humble:

```bash
# Add Gazebo repository
sudo apt-get update
sudo apt-get install lsb-release wget gnupg

sudo wget https://packages.osrfoundation.org/gazebo.gpg -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null

# Install Gazebo Fortress
sudo apt-get update
sudo apt-get install gz-fortress

# Install ROS 2 - Gazebo bridge
sudo apt-get install ros-humble-ros-gz
```

Verify installation:
```bash
gz sim -v4
```

## URDF: Unified Robot Description Format

URDF is an XML format for describing robot kinematics and dynamics.

### Basic URDF Structure

```xml
<?xml version="1.0"?>
<robot name="simple_robot">

  <!-- Base Link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.6 0.4 0.2"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 0.8 1"/>
      </material>
    </visual>

    <collision>
      <geometry>
        <box size="0.6 0.4 0.2"/>
      </geometry>
    </collision>

    <inertial>
      <mass value="10.0"/>
      <inertia ixx="0.4" ixy="0.0" ixz="0.0"
               iyy="0.4" iyz="0.0" izz="0.4"/>
    </inertial>
  </link>

  <!-- Wheel Link -->
  <link name="left_wheel">
    <visual>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
      <material name="black">
        <color rgba="0 0 0 1"/>
      </material>
    </visual>

    <collision>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
    </collision>

    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.01" ixy="0.0" ixz="0.0"
               iyy="0.01" iyz="0.0" izz="0.01"/>
    </inertial>
  </link>

  <!-- Joint -->
  <joint name="left_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="left_wheel"/>
    <origin xyz="0 0.22 0" rpy="-1.5707 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

</robot>
```

### Key URDF Elements

- **`<link>`**: Physical body (visual, collision, inertial properties)
- **`<joint>`**: Connection between links (fixed, revolute, continuous, prismatic)
- **`<visual>`**: How the link looks
- **`<collision>`**: Shape for collision detection
- **`<inertial>`**: Mass and inertia matrix

### Joint Types

- **fixed**: No movement (camera mount)
- **revolute**: Rotation with limits (elbow)
- **continuous**: Unlimited rotation (wheel)
- **prismatic**: Linear motion (elevator)
- **planar**: XY plane motion
- **floating**: 6 DOF (flying objects)

## Creating a Simple Robot

Let's build a differential drive robot:

```xml
<?xml version="1.0"?>
<robot name="diffbot" xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- Base Link -->
  <link name="base_footprint"/>

  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.5 0.3 0.15"/>
      </geometry>
      <material name="white">
        <color rgba="1 1 1 1"/>
      </material>
    </visual>

    <collision>
      <geometry>
        <box size="0.5 0.3 0.15"/>
      </geometry>
    </collision>

    <inertial>
      <mass value="5.0"/>
      <inertia ixx="0.1" ixy="0" ixz="0"
               iyy="0.1" iyz="0" izz="0.1"/>
    </inertial>
  </link>

  <joint name="base_joint" type="fixed">
    <parent link="base_footprint"/>
    <child link="base_link"/>
    <origin xyz="0 0 0.1"/>
  </joint>

  <!-- Left Wheel -->
  <link name="left_wheel">
    <visual>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
      <material name="black">
        <color rgba="0.2 0.2 0.2 1"/>
      </material>
    </visual>

    <collision>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
    </collision>

    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.001" ixy="0" ixz="0"
               iyy="0.001" iyz="0" izz="0.001"/>
    </inertial>
  </link>

  <joint name="left_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="left_wheel"/>
    <origin xyz="0 0.17 0" rpy="-1.5707 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <!-- Right Wheel (similar structure) -->
  <link name="right_wheel">
    <!-- Same as left_wheel -->
  </link>

  <joint name="right_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="right_wheel"/>
    <origin xyz="0 -0.17 0" rpy="-1.5707 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <!-- Caster Wheel -->
  <link name="caster">
    <visual>
      <geometry>
        <sphere radius="0.05"/>
      </geometry>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 1"/>
      </material>
    </visual>

    <collision>
      <geometry>
        <sphere radius="0.05"/>
      </geometry>
    </collision>

    <inertial>
      <mass value="0.1"/>
      <inertia ixx="0.0001" ixy="0" ixz="0"
               iyy="0.0001" iyz="0" izz="0.0001"/>
    </inertial>
  </link>

  <joint name="caster_joint" type="fixed">
    <parent link="base_link"/>
    <child link="caster"/>
    <origin xyz="-0.2 0 -0.05"/>
  </joint>

</robot>
```

## Visualizing URDF

Check URDF with RViz:

```bash
# Install URDF tools
sudo apt-get install ros-humble-joint-state-publisher-gui
sudo apt-get install ros-humble-robot-state-publisher

# Launch visualization
ros2 launch urdf_tutorial display.launch.py model:=diffbot.urdf
```

## Adding Sensors to URDF

### Camera

```xml
<!-- Camera Link -->
<link name="camera">
  <visual>
    <geometry>
      <box size="0.05 0.05 0.05"/>
    </geometry>
    <material name="red">
      <color rgba="1 0 0 1"/>
    </material>
  </visual>

  <collision>
    <geometry>
      <box size="0.05 0.05 0.05"/>
    </geometry>
  </collision>

  <inertial>
    <mass value="0.1"/>
    <inertia ixx="0.0001" ixy="0" ixz="0"
             iyy="0.0001" iyz="0" izz="0.0001"/>
  </inertial>
</link>

<joint name="camera_joint" type="fixed">
  <parent link="base_link"/>
  <child link="camera"/>
  <origin xyz="0.25 0 0.1" rpy="0 0 0"/>
</joint>

<!-- Camera Sensor (Gazebo plugin) -->
<gazebo reference="camera">
  <sensor name="camera1" type="camera">
    <update_rate>30.0</update_rate>
    <camera name="head">
      <horizontal_fov>1.3962634</horizontal_fov>
      <image>
        <width>640</width>
        <height>480</height>
        <format>R8G8B8</format>
      </image>
      <clip>
        <near>0.02</near>
        <far>300</far>
      </clip>
    </camera>
    <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
      <ros>
        <namespace>/diffbot</namespace>
        <remapping>image_raw:=camera/image_raw</remapping>
        <remapping>camera_info:=camera/camera_info</remapping>
      </ros>
    </plugin>
  </sensor>
</gazebo>
```

### LiDAR

```xml
<link name="lidar">
  <visual>
    <geometry>
      <cylinder radius="0.05" length="0.04"/>
    </geometry>
    <material name="black"/>
  </visual>

  <collision>
    <geometry>
      <cylinder radius="0.05" length="0.04"/>
    </geometry>
  </collision>

  <inertial>
    <mass value="0.2"/>
    <inertia ixx="0.0001" ixy="0" ixz="0"
             iyy="0.0001" iyz="0" izz="0.0001"/>
  </inertial>
</link>

<joint name="lidar_joint" type="fixed">
  <parent link="base_link"/>
  <child link="lidar"/>
  <origin xyz="0 0 0.15" rpy="0 0 0"/>
</joint>

<gazebo reference="lidar">
  <sensor name="lidar" type="ray">
    <always_on>true</always_on>
    <update_rate>10</update_rate>
    <visualize>true</visualize>
    <ray>
      <scan>
        <horizontal>
          <samples>360</samples>
          <resolution>1</resolution>
          <min_angle>-3.14159</min_angle>
          <max_angle>3.14159</max_angle>
        </horizontal>
      </scan>
      <range>
        <min>0.10</min>
        <max>30.0</max>
        <resolution>0.01</resolution>
      </range>
    </ray>
    <plugin name="gazebo_ros_laser" filename="libgazebo_ros_ray_sensor.so">
      <ros>
        <namespace>/diffbot</namespace>
        <remapping>~/out:=scan</remapping>
      </ros>
      <output_type>sensor_msgs/LaserScan</output_type>
    </plugin>
  </sensor>
</gazebo>
```

## Differential Drive Plugin

Add motor control:

```xml
<gazebo>
  <plugin name="diff_drive" filename="libgazebo_ros_diff_drive.so">

    <!-- Wheel configuration -->
    <left_joint>left_wheel_joint</left_joint>
    <right_joint>right_wheel_joint</right_joint>

    <!-- Kinematics -->
    <wheel_separation>0.34</wheel_separation>
    <wheel_diameter>0.2</wheel_diameter>

    <!-- Limits -->
    <max_wheel_torque>20</max_wheel_torque>
    <max_wheel_acceleration>1.0</max_wheel_acceleration>

    <!-- Input/Output -->
    <command_topic>cmd_vel</command_topic>
    <odometry_topic>odom</odometry_topic>
    <odometry_frame>odom</odometry_frame>
    <robot_base_frame>base_footprint</robot_base_frame>

    <!-- Publishing -->
    <publish_odom>true</publish_odom>
    <publish_odom_tf>true</publish_odom_tf>
    <publish_wheel_tf>true</publish_wheel_tf>

    <update_rate>30</update_rate>
  </plugin>
</gazebo>
```

## Launching Gazebo with ROS 2

Create launch file `gazebo_diffbot.launch.py`:

```python
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_diffbot = get_package_share_directory('diffbot_description')

    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        )
    )

    # Spawn robot
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', '/robot_description',
            '-entity', 'diffbot'
        ],
        output='screen'
    )

    # Robot state publisher
    urdf_file = os.path.join(pkg_diffbot, 'urdf', 'diffbot.urdf')
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc}]
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity
    ])
```

Launch:
```bash
ros2 launch diffbot_description gazebo_diffbot.launch.py
```

## Controlling the Robot

Test with keyboard teleop:

```bash
sudo apt-get install ros-humble-teleop-twist-keyboard
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Or programmatically:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class RobotController(Node):
    def __init__(self):
        super().__init__('robot_controller')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = 0.5  # Forward
        msg.angular.z = 0.5  # Turn left
        self.publisher.publish(msg)


def main():
    rclpy.init()
    controller = RobotController()
    rclpy.spin(controller)
    rclpy.shutdown()
```

## Sensor Data Visualization

View camera:
```bash
ros2 run rqt_image_view rqt_image_view
# Select /diffbot/camera/image_raw
```

View LiDAR in RViz:
```bash
rviz2
# Add LaserScan display
# Set topic to /diffbot/scan
```

## Summary

- Gazebo provides physics-based 3D robot simulation
- URDF describes robot structure, kinematics, and visual appearance
- Gazebo plugins add sensors and actuators
- ROS 2 bridge connects Gazebo to ROS topics/services
- Simulation enables safe, cost-effective testing

## Exercises

1. Add an IMU sensor to the diffbot
2. Create a simple maze world in Gazebo
3. Implement obstacle avoidance using LiDAR data
4. Add a manipulator arm to the robot
5. Create a launch file that spawns multiple robots

## Next Chapter

In Chapter 7, we'll explore Unity Robotics - using the Unity game engine for high-fidelity simulation with advanced graphics and physics.
Human: continue