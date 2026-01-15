---
id: chapter-03-ros2-topics
title: ROS 2 Topics and Message Types
module: 2
week: 2
learning_objectives:
  - Master the publisher-subscriber pattern in ROS 2
  - Work with standard message types (geometry, sensor)
  - Create custom message definitions
  - Understand topic introspection and debugging
  - Implement Quality of Service policies
estimated_time_minutes: 75
---

# ROS 2 Topics and Message Types

## Understanding the Publisher-Subscriber Pattern

ROS 2 Topics enable asynchronous communication between nodes using a publish-subscribe pattern. Publishers send messages to topics without knowing who will receive them, and subscribers receive messages without knowing who sent them.

### Key Characteristics

- **Decoupling**: Publishers and subscribers don't need to know about each other
- **Many-to-Many**: Multiple publishers and subscribers per topic
- **Asynchronous**: No blocking - fire and forget
- **Typed**: Each topic has a specific message type

### When to Use Topics

Topics are ideal for:
- Continuous data streams (sensor readings, camera images)
- Broadcasting information to multiple consumers
- One-way communication without waiting for response

## Standard Message Types

ROS 2 provides standard message packages for common robotics data.

### std_msgs - Basic Types

Simple, single-field messages:

```python
from std_msgs.msg import String, Int32, Float64, Bool

# String message
msg = String()
msg.data = "Hello"

# Numeric messages
counter = Int32()
counter.data = 42

temperature = Float64()
temperature.data = 25.5
```

### geometry_msgs - Spatial Data

Messages for positions, velocities, and transformations:

```python
from geometry_msgs.msg import Twist, Point, Pose

# Twist - linear and angular velocity (robot control)
cmd_vel = Twist()
cmd_vel.linear.x = 0.5   # Move forward at 0.5 m/s
cmd_vel.angular.z = 0.2  # Turn left at 0.2 rad/s

# Point - 3D coordinates
point = Point()
point.x = 1.0
point.y = 2.0
point.z = 0.5

# Pose - position + orientation
pose = Pose()
pose.position.x = 1.0
pose.position.y = 2.0
pose.orientation.w = 1.0  # No rotation (quaternion)
```

### sensor_msgs - Sensor Data

Messages for common sensors:

```python
from sensor_msgs.msg import Image, LaserScan, Imu, JointState

# Image - camera data
# Contains: height, width, encoding, data array

# LaserScan - LiDAR/laser range finder
# Contains: angle_min, angle_max, ranges array

# Imu - Inertial Measurement Unit
# Contains: orientation, angular_velocity, linear_acceleration

# JointState - robot joint positions
joint_state = JointState()
joint_state.name = ['joint1', 'joint2', 'joint3']
joint_state.position = [0.0, 1.57, -1.57]  # radians
joint_state.velocity = [0.1, 0.2, 0.3]     # rad/s
```

## Creating Custom Messages

Sometimes you need custom message types for your application.

### 1. Create Message Definition

In your package, create `msg/RobotStatus.msg`:

```
# RobotStatus.msg - Custom message for robot state
string robot_name
float32 battery_percentage
bool is_moving
geometry_msgs/Pose current_pose
```

### 2. Update package.xml

```xml
<build_depend>rosidl_default_generators</build_depend>
<exec_depend>rosidl_default_runtime</exec_depend>
<member_of_group>rosidl_interface_packages</member_of_group>
```

### 3. Update CMakeLists.txt (for C++)

Or for Python packages, update setup.py:

```python
from setuptools import setup

package_name = 'my_robot_msgs'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/msg', ['msg/RobotStatus.msg']),
    ],
    # ... rest of setup
)
```

### 4. Build and Use

```bash
colcon build --packages-select my_robot_msgs
source install/setup.bash

# Use in your code
from my_robot_msgs.msg import RobotStatus

msg = RobotStatus()
msg.robot_name = "Atlas"
msg.battery_percentage = 85.5
msg.is_moving = True
```

## Practical Example: Robot Control

Let's create a complete example of controlling a simulated robot.

### Publisher - Velocity Command

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class RobotController(Node):
    def __init__(self):
        super().__init__('robot_controller')

        # Publish to /cmd_vel topic (standard for robot control)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Control loop at 10 Hz
        self.timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info('Robot Controller started')

    def control_loop(self):
        """Send velocity commands to robot"""
        cmd = Twist()

        # Move in a circle
        cmd.linear.x = 0.5    # Forward speed
        cmd.angular.z = 0.3   # Turn rate

        self.cmd_pub.publish(cmd)


def main():
    rclpy.init()
    node = RobotController()
    rclpy.spin(node)
    rclpy.shutdown()
```

### Subscriber - Sensor Processing

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class ObstacleDetector(Node):
    def __init__(self):
        super().__init__('obstacle_detector')

        # Subscribe to laser scan data
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.get_logger().info('Obstacle Detector started')

    def scan_callback(self, msg: LaserScan):
        """Process laser scan to detect obstacles"""

        # Check for obstacles in front (middle of scan)
        mid_index = len(msg.ranges) // 2
        front_distance = msg.ranges[mid_index]

        if front_distance < 0.5:  # Less than 50cm
            self.get_logger().warn(f'Obstacle ahead! Distance: {front_distance:.2f}m')
        else:
            self.get_logger().info(f'Clear ahead: {front_distance:.2f}m')


def main():
    rclpy.init()
    node = ObstacleDetector()
    rclpy.spin(node)
    rclpy.shutdown()
```

## Quality of Service (QoS) Policies

QoS determines how messages are delivered and stored.

### Key QoS Settings

1. **Reliability**
   - `RELIABLE`: Guaranteed delivery (retries on packet loss)
   - `BEST_EFFORT`: Fast, no guarantees (like UDP)

2. **Durability**
   - `TRANSIENT_LOCAL`: Store last message for new subscribers
   - `VOLATILE`: Only deliver to existing subscribers

3. **History**
   - `KEEP_LAST(N)`: Keep last N messages
   - `KEEP_ALL`: Keep all messages (memory intensive)

### QoS Profiles

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy

# Sensor data QoS (lossy but fast)
sensor_qos = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE,
    history=HistoryPolicy.KEEP_LAST,
    depth=10
)

# Command QoS (reliable)
command_qos = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.VOLATILE,
    history=HistoryPolicy.KEEP_LAST,
    depth=10
)

# Use custom QoS
self.publisher_ = self.create_publisher(
    LaserScan,
    '/scan',
    sensor_qos
)
```

### QoS Compatibility

Publisher and subscriber QoS must be compatible:

- Reliable publisher → Best effort subscriber: ✅ Works
- Best effort publisher → Reliable subscriber: ❌ Incompatible
- Transient local publisher → Volatile subscriber: ✅ Works

## Topic Introspection

ROS 2 provides powerful tools to inspect and debug topics.

### List All Topics

```bash
ros2 topic list
```

Output:
```
/cmd_vel
/scan
/camera/image_raw
/odom
```

### Topic Information

```bash
ros2 topic info /cmd_vel
```

Output:
```
Type: geometry_msgs/msg/Twist
Publisher count: 1
Subscription count: 2
```

### Echo Messages

View messages in real-time:

```bash
ros2 topic echo /scan
```

### Message Frequency

Check publishing rate:

```bash
ros2 topic hz /camera/image_raw
```

Output:
```
average rate: 30.012
  min: 0.032s max: 0.034s std dev: 0.00051s window: 30
```

### Bandwidth Usage

Monitor data throughput:

```bash
ros2 topic bw /camera/image_raw
```

## Remapping Topics

Change topic names at runtime:

```bash
# Remap /cmd_vel to /robot1/cmd_vel
ros2 run my_package robot_controller --ros-args -r /cmd_vel:=/robot1/cmd_vel
```

Useful for:
- Running multiple robots
- Testing with different topics
- Integrating third-party nodes

## Performance Considerations

### Message Size

- Keep messages small for high-frequency topics
- Use compressed formats for images
- Consider downsampling sensor data

### Publishing Rate

- Match rate to consumer needs
- Avoid unnecessary high-frequency publishing
- Use timers for consistent rates

### Queues and Buffering

```python
# Queue depth affects memory and latency
self.publisher_ = self.create_publisher(Image, '/camera', 10)  # Keep last 10
self.publisher_ = self.create_publisher(Image, '/camera', 1)   # Keep only latest
```

## Best Practices

1. **Standard Topics**: Use standard names (`/cmd_vel`, `/scan`, `/odom`)
2. **Namespaces**: Group robot topics (`/robot1/cmd_vel`, `/robot1/scan`)
3. **Message Types**: Prefer standard messages over custom when possible
4. **QoS Matching**: Ensure publisher/subscriber QoS compatibility
5. **Monitoring**: Regularly check topic rates and bandwidth

## Common Patterns

### Periodic Publishing

```python
self.timer = self.create_timer(0.1, self.publish_callback)  # 10 Hz
```

### Triggered Publishing

```python
def sensor_callback(self, msg):
    # Process sensor data
    processed_msg = self.process(msg)
    # Publish result
    self.result_pub.publish(processed_msg)
```

### Multi-Topic Subscriber

```python
self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_cb, 10)
self.camera_sub = self.create_subscription(Image, '/camera', self.camera_cb, 10)
```

## Debugging Tips

1. **No Messages**: Check QoS compatibility with `ros2 topic info`
2. **Slow Performance**: Monitor bandwidth with `ros2 topic bw`
3. **Dropped Messages**: Check queue depth and publishing rate
4. **Type Errors**: Verify message fields with `ros2 interface show`

## Next Chapter Preview

In the next chapter, we'll explore ROS 2 services for request-response communication and learn when to use services vs topics. We'll build a robot task planning system using services.

## Exercises

1. Create a node that publishes robot joint angles at 50Hz
2. Build a subscriber that calculates average laser scan distance
3. Implement a "safety monitor" that stops the robot if obstacles are detected
4. Create a custom message for battery status with voltage, current, and percentage
