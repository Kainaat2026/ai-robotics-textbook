---
id: chapter-02-ros2-basics
title: ROS 2 Basics - Getting Started
module: 1
week: 1
learning_objectives:
  - Install and configure ROS 2 Humble
  - Understand ROS 2 architecture and concepts
  - Create your first ROS 2 package
  - Write a simple publisher and subscriber
estimated_time_minutes: 60
---

# ROS 2 Basics - Getting Started

## What is ROS 2?

ROS 2 (Robot Operating System 2) is an open-source framework for building robot software. Despite its name, ROS is not an operating system but rather a middleware that provides:

- **Communication**: Message passing between processes
- **Tools**: Visualization, debugging, simulation integration
- **Libraries**: Navigation, manipulation, perception
- **Ecosystem**: Thousands of community packages

### ROS 1 vs ROS 2

ROS 2 is a complete redesign addressing limitations of ROS 1:

| Feature | ROS 1 | ROS 2 |
|---------|-------|-------|
| Real-time | Limited | Full support |
| Security | Minimal | DDS security |
| Multi-robot | Challenging | Native support |
| Windows | Poor | Full support |
| Communication | Custom protocol | DDS standard |

For new projects, always use ROS 2. We'll be using **ROS 2 Humble Hawksbill**, the LTS (Long Term Support) release.

## Installation

### Ubuntu 22.04 (Recommended)

```bash
# Add ROS 2 repository
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository universe

# Add ROS 2 GPG key
sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

# Add repository to sources list
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Install ROS 2 Humble
sudo apt update
sudo apt install ros-humble-desktop python3-colcon-common-extensions

# Source the setup script
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### Verify Installation

```bash
ros2 --help
```

You should see a list of ROS 2 commands.

## Core Concepts

### Nodes

A **node** is a process that performs a specific task. Examples:
- Camera driver node that publishes images
- Motion planner node that plans trajectories
- Controller node that sends motor commands

Nodes communicate via topics, services, and actions.

### Topics

**Topics** enable asynchronous, many-to-many communication:

- **Publishers** send messages to topics
- **Subscribers** receive messages from topics
- Message types are strictly defined (e.g., `sensor_msgs/Image`)

Example: A camera node publishes images to `/camera/image_raw` topic, while multiple nodes (object detector, recorder, viewer) can subscribe.

### Services

**Services** provide synchronous request-response communication:

- Client sends request
- Server processes and returns response
- Useful for actions like "compute inverse kinematics" or "capture image"

### Actions

**Actions** are for long-running tasks with feedback:

- Client sends goal
- Server provides periodic feedback
- Client can cancel
- Example: "Navigate to waypoint" with progress updates

## Creating Your First Package

### Workspace Setup

```bash
# Create workspace
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

# Create a package
ros2 pkg create --build-type ament_python my_robot_controller --dependencies rclpy
```

This creates a Python package with the `rclpy` dependency (ROS 2 Python client library).

### Package Structure

```
my_robot_controller/
├── package.xml         # Package metadata
├── setup.py           # Python package setup
├── setup.cfg          # Installation config
├── my_robot_controller/
│   ├── __init__.py
│   └── my_node.py     # Your node code
└── resource/
    └── my_robot_controller
```

## Writing a Simple Publisher

Let's create a node that publishes messages:

```python
# my_robot_controller/my_node.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class HelloPublisher(Node):
    def __init__(self):
        super().__init__('hello_publisher')

        # Create publisher
        self.publisher_ = self.create_publisher(String, 'greetings', 10)

        # Create timer (publish every 1 second)
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.counter = 0

        self.get_logger().info('Hello Publisher started')

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello ROS 2! Message #{self.counter}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Published: "{msg.data}"')
        self.counter += 1


def main(args=None):
    rclpy.init(args=args)
    node = HelloPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Key Components

- **`Node` class**: Base class for all ROS 2 nodes
- **`create_publisher()`**: Creates a publisher for a topic
- **`create_timer()`**: Schedules periodic callbacks
- **`rclpy.spin()`**: Keeps node running and processing callbacks

## Writing a Subscriber

Now let's create a subscriber:

```python
# my_robot_controller/listener_node.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class HelloSubscriber(Node):
    def __init__(self):
        super().__init__('hello_subscriber')

        # Create subscriber
        self.subscription = self.create_subscription(
            String,
            'greetings',
            self.listener_callback,
            10
        )

        self.get_logger().info('Hello Subscriber started')

    def listener_callback(self, msg):
        self.get_logger().info(f'Received: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)
    node = HelloSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Building and Running

### Update setup.py

Add entry points for your nodes:

```python
entry_points={
    'console_scripts': [
        'hello_pub = my_robot_controller.my_node:main',
        'hello_sub = my_robot_controller.listener_node:main',
    ],
},
```

### Build the Package

```bash
cd ~/ros2_ws
colcon build --packages-select my_robot_controller
source install/setup.bash
```

### Run Your Nodes

Terminal 1 - Publisher:
```bash
ros2 run my_robot_controller hello_pub
```

Terminal 2 - Subscriber:
```bash
ros2 run my_robot_controller hello_sub
```

You should see messages being published and received!

## Useful ROS 2 Commands

### List Topics

```bash
ros2 topic list
```

### Echo Topic Messages

```bash
ros2 topic echo /greetings
```

### Get Topic Info

```bash
ros2 topic info /greetings
```

### List Nodes

```bash
ros2 node list
```

### Node Info

```bash
ros2 node info /hello_publisher
```

## Quality of Service (QoS)

ROS 2 uses DDS (Data Distribution Service) which provides configurable QoS:

- **Reliability**: Reliable vs Best Effort
- **Durability**: Transient Local vs Volatile
- **History**: Keep last N messages

Example:
```python
from rclpy.qos import QoSProfile, ReliabilityPolicy

qos = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    depth=10
)
self.publisher_ = self.create_publisher(String, 'topic', qos)
```

## Best Practices

1. **Descriptive Names**: Use clear node and topic names
2. **Namespace**: Group related nodes under namespaces
3. **Parameters**: Use parameters for configuration
4. **Logging**: Use `get_logger()` instead of `print()`
5. **Lifecycle**: Properly initialize and cleanup resources

## Next Steps

In the next chapter, we'll dive deeper into ROS 2 topics and explore different message types used in robotics, including sensor data and robot control messages.

## Exercises

1. Modify the publisher to send your name instead of "Hello ROS 2"
2. Create a subscriber that counts the number of messages received
3. Experiment with different timer frequencies (0.5s, 2s)
4. Try echoing the topic from command line while nodes are running
