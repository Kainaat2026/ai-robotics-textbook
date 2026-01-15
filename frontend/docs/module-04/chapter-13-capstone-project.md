---
id: chapter-13-capstone-project
title: Capstone Project - Build Your Humanoid Agent
module: 4
week: 13
learning_objectives:
  - Integrate all course modules into a complete robotic system
  - Design and implement a real-world robotics application
  - Test and validate system performance
  - Document and present your project
  - Deploy on physical hardware or realistic simulation
estimated_time_minutes: 120
---

# Capstone Project - Build Your Humanoid Agent

## Introduction

Welcome to the capstone project! This is where you bring together everything you've learned throughout this course - ROS 2, simulation, AI models, humanoid control, and conversational interfaces - to build a complete autonomous robot system.

**Project Goal:** Build a humanoid robot agent capable of understanding natural language commands and executing complex manipulation and navigation tasks in realistic environments.

## Project Overview

### System Architecture

Your complete system will include:

```
┌──────────────────────────────────────────────────────┐
│              User Interface Layer                    │
│  - Voice Commands (Speech-to-Text)                   │
│  - Natural Language Understanding                    │
│  - Visual Feedback (Camera Stream)                   │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│           High-Level Planning (AI/LLM)               │
│  - Task Decomposition                                │
│  - VLA Models (RT-2, OpenVLA)                        │
│  - Behavior Trees                                    │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│           Perception & Sensing                       │
│  - Camera (RGB-D)                                    │
│  - LiDAR (2D/3D)                                     │
│  - IMU, Encoders                                     │
│  - Object Detection & Segmentation                   │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│              ROS 2 Middleware                        │
│  - Nodes, Topics, Services, Actions                  │
│  - Navigation Stack (Nav2)                           │
│  - MoveIt for Manipulation                           │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│         Low-Level Control & Simulation               │
│  - Whole-Body Controller                             │
│  - Balance & Stability (ZMP)                         │
│  - Gazebo/Isaac Sim                                  │
│  - Hardware Interface (Real Robot)                   │
└──────────────────────────────────────────────────────┘
```

## Project Options

Choose one of the following projects based on your interests:

### Option 1: Warehouse Assistant Robot

**Description:** Humanoid robot that assists in warehouse operations.

**Tasks:**
- Navigate autonomously through warehouse aisles
- Detect and locate objects using natural language descriptions
- Pick objects from shelves
- Place objects in designated locations
- Handle human requests via voice commands

**Key Technologies:**
- ROS 2 Navigation (Nav2)
- Object detection (YOLO, OWL-ViT)
- Manipulation (MoveIt)
- VLA models for language control

**Success Metrics:**
- Navigate to 5 different locations with >90% success
- Pick and place 10 objects with >80% success
- Respond to voice commands with less than 3s latency

---

### Option 2: Home Service Robot

**Description:** Humanoid robot for household assistance.

**Tasks:**
- Navigate home environments (rooms, stairs)
- Recognize and manipulate common household objects
- Perform tasks like "bring me the remote" or "clean the table"
- Interact naturally with humans

**Key Technologies:**
- SLAM for mapping
- Semantic segmentation
- Bimanual manipulation
- Conversational AI

**Success Metrics:**
- Map a 3-room environment
- Recognize 20+ common objects
- Complete 5 multi-step tasks

---

### Option 3: Research Lab Assistant

**Description:** Robot that assists in research lab tasks.

**Tasks:**
- Organize lab equipment
- Transport objects between stations
- Assist with repetitive tasks
- Document activities with vision

**Key Technologies:**
- Precise manipulation
- Multi-object tracking
- Task scheduling
- Data logging

**Success Metrics:**
- Organize 15 objects into categories
- Transport items with less than 5cm placement error
- Complete tasks in less than 2x human time

## Project Phases

### Phase 1: Planning and Design (Week 1)

**Deliverables:**
- System architecture diagram
- Component selection and justification
- Task decomposition
- Timeline and milestones

**Template:**

```markdown
# Project Plan: [Your Project Name]

## 1. Executive Summary
[Brief description of your project and goals]

## 2. System Architecture
[Diagram showing all components and their connections]

## 3. Hardware/Simulation Setup
- Robot platform: [Gazebo/Isaac Sim/Physical robot]
- Sensors: [Cameras, LiDAR, etc.]
- Compute: [CPU/GPU specifications]

## 4. Software Stack
- ROS 2 packages: [List packages]
- AI models: [VLA, object detection, etc.]
- Custom nodes: [List custom nodes to develop]

## 5. Task Breakdown
| Task | Description | Dependencies | Estimated Time |
|------|-------------|--------------|----------------|
| ... | ... | ... | ... |

## 6. Success Criteria
- Criterion 1: [Metric and target]
- Criterion 2: [Metric and target]
- ...

## 7. Risk Analysis
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| ... | ... | ... | ... |
```

### Phase 2: Core System Implementation (Week 2-3)

**Step 1: Simulation Environment Setup**

Create your simulation world:

```python
# File: launch/simulation_world.launch.py

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    # Gazebo or Isaac Sim
    pkg_gazebo = get_package_share_directory('gazebo_ros')

    # World file
    world_file = os.path.join(
        get_package_share_directory('your_package'),
        'worlds',
        'warehouse.world'
    )

    # Launch Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': world_file}.items()
    )

    # Spawn robot
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-file', '/path/to/robot.urdf',
            '-entity', 'humanoid_robot',
            '-x', '0', '-y', '0', '-z', '0.5'
        ]
    )

    # Robot state publisher
    robot_state_pub = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': open('/path/to/robot.urdf').read()}]
    )

    return LaunchDescription([
        gazebo,
        spawn_robot,
        robot_state_pub
    ])
```

**Step 2: Perception Pipeline**

```python
# File: perception_node.py

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray, Detection2D
from cv_bridge import CvBridge
import cv2
import numpy as np
import torch


class PerceptionNode(Node):
    """
    Perception node for object detection and semantic understanding.
    """

    def __init__(self):
        super().__init__('perception_node')

        # Subscribers
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # Publishers
        self.detection_pub = self.create_publisher(
            Detection2DArray,
            '/detections',
            10
        )

        # CV Bridge
        self.bridge = CvBridge()

        # Load object detection model
        self.detector = self.load_detection_model()

        self.get_logger().info("Perception node initialized")

    def load_detection_model(self):
        """Load YOLO or similar detector."""
        # Example: YOLOv8
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt')
        return model

    def image_callback(self, msg):
        """Process incoming images."""
        # Convert ROS image to OpenCV
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Run detection
        detections = self.detect_objects(cv_image)

        # Publish detections
        detection_msg = self.create_detection_msg(detections)
        self.detection_pub.publish(detection_msg)

    def detect_objects(self, image):
        """Detect objects in image."""
        results = self.detector(image)

        detections = []
        for result in results:
            for box in result.boxes:
                det = {
                    'class_id': int(box.cls[0]),
                    'class_name': result.names[int(box.cls[0])],
                    'confidence': float(box.conf[0]),
                    'bbox': box.xyxy[0].tolist()
                }
                detections.append(det)

        return detections

    def create_detection_msg(self, detections):
        """Convert detections to ROS message."""
        msg = Detection2DArray()

        for det in detections:
            detection = Detection2D()
            detection.bbox.center.x = (det['bbox'][0] + det['bbox'][2]) / 2
            detection.bbox.center.y = (det['bbox'][1] + det['bbox'][3]) / 2
            detection.bbox.size_x = det['bbox'][2] - det['bbox'][0]
            detection.bbox.size_y = det['bbox'][3] - det['bbox'][1]

            # Add to array
            msg.detections.append(detection)

        return msg


def main():
    rclpy.init()
    node = PerceptionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

**Step 3: Navigation System**

```python
# File: navigation_controller.py

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
import numpy as np


class NavigationController(Node):
    """High-level navigation controller."""

    def __init__(self):
        super().__init__('navigation_controller')

        # Nav2 interface
        self.navigator = BasicNavigator()

        # Define waypoints
        self.waypoints = {
            'home': [0.0, 0.0, 0.0],
            'shelf_A': [2.0, 1.0, 0.0],
            'shelf_B': [2.0, -1.0, 1.57],
            'workstation': [-1.0, 0.0, 3.14]
        }

        self.get_logger().info("Navigation controller initialized")

    def navigate_to(self, location_name):
        """Navigate to named location."""
        if location_name not in self.waypoints:
            self.get_logger().error(f"Unknown location: {location_name}")
            return False

        # Create goal pose
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = self.navigator.get_clock().now().to_msg()

        x, y, theta = self.waypoints[location_name]
        goal_pose.pose.position.x = x
        goal_pose.pose.position.y = y
        goal_pose.pose.orientation.z = np.sin(theta / 2)
        goal_pose.pose.orientation.w = np.cos(theta / 2)

        # Send goal
        self.navigator.goToPose(goal_pose)

        # Wait for completion
        while not self.navigator.isTaskComplete():
            feedback = self.navigator.getFeedback()
            # Monitor progress

        result = self.navigator.getResult()

        if result == BasicNavigator.TaskResult.SUCCEEDED:
            self.get_logger().info(f"Reached {location_name}")
            return True
        else:
            self.get_logger().error(f"Failed to reach {location_name}")
            return False

    def navigate_to_pose(self, x, y, theta):
        """Navigate to arbitrary pose."""
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.pose.position.x = x
        goal_pose.pose.position.y = y
        goal_pose.pose.orientation.z = np.sin(theta / 2)
        goal_pose.pose.orientation.w = np.cos(theta / 2)

        self.navigator.goToPose(goal_pose)
```

**Step 4: Manipulation Controller**

```python
# File: manipulation_controller.py

import rclpy
from rclpy.node import Node
from moveit_msgs.srv import GetPositionIK
from geometry_msgs.msg import Pose
import numpy as np


class ManipulationController(Node):
    """High-level manipulation controller using MoveIt."""

    def __init__(self):
        super().__init__('manipulation_controller')

        # MoveIt interface (simplified)
        self.ik_client = self.create_client(GetPositionIK, '/compute_ik')

        # Gripper control
        self.gripper_open = False

        self.get_logger().info("Manipulation controller initialized")

    def pick_object(self, object_pose):
        """
        Pick object at given pose.

        Args:
            object_pose: geometry_msgs/Pose
        """
        # 1. Move to pre-grasp pose
        pre_grasp = self.compute_pre_grasp_pose(object_pose)
        self.move_to_pose(pre_grasp)

        # 2. Open gripper
        self.open_gripper()

        # 3. Move to grasp pose
        self.move_to_pose(object_pose)

        # 4. Close gripper
        self.close_gripper()

        # 5. Lift object
        lift_pose = self.compute_lift_pose(object_pose)
        self.move_to_pose(lift_pose)

        self.get_logger().info("Object picked successfully")

    def place_object(self, target_pose):
        """Place object at target pose."""
        # 1. Move to pre-place pose
        pre_place = self.compute_pre_place_pose(target_pose)
        self.move_to_pose(pre_place)

        # 2. Move to place pose
        self.move_to_pose(target_pose)

        # 3. Open gripper
        self.open_gripper()

        # 4. Retract
        retract_pose = self.compute_retract_pose(target_pose)
        self.move_to_pose(retract_pose)

        self.get_logger().info("Object placed successfully")

    def compute_pre_grasp_pose(self, grasp_pose):
        """Compute approach pose (10cm above grasp)."""
        pre_grasp = Pose()
        pre_grasp.position.x = grasp_pose.position.x
        pre_grasp.position.y = grasp_pose.position.y
        pre_grasp.position.z = grasp_pose.position.z + 0.1
        pre_grasp.orientation = grasp_pose.orientation
        return pre_grasp

    def compute_lift_pose(self, grasp_pose):
        """Compute lift pose (15cm above grasp)."""
        lift = Pose()
        lift.position.x = grasp_pose.position.x
        lift.position.y = grasp_pose.position.y
        lift.position.z = grasp_pose.position.z + 0.15
        lift.orientation = grasp_pose.orientation
        return lift

    def move_to_pose(self, target_pose):
        """Move arm to target pose using MoveIt."""
        # Use MoveIt's move_group interface
        # Simplified for example
        self.get_logger().info(f"Moving to pose: {target_pose.position}")

    def open_gripper(self):
        """Open gripper."""
        # Send gripper command
        self.gripper_open = True
        self.get_logger().info("Gripper opened")

    def close_gripper(self):
        """Close gripper."""
        self.gripper_open = False
        self.get_logger().info("Gripper closed")
```

### Phase 3: AI Integration (Week 4)

**VLA-based Task Executor**

```python
# File: vla_task_executor.py

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image
import torch
import numpy as np


class VLATaskExecutor(Node):
    """
    Execute tasks using Vision-Language-Action model.
    """

    def __init__(self):
        super().__init__('vla_task_executor')

        # Subscribers
        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10
        )

        self.command_sub = self.create_subscription(
            String, '/voice_command', self.command_callback, 10
        )

        # VLA model
        self.vla_model = self.load_vla_model()

        # Current observation
        self.current_image = None

        self.get_logger().info("VLA Task Executor initialized")

    def load_vla_model(self):
        """Load VLA model (RT-2, OpenVLA, etc.)."""
        # Placeholder - load your trained model
        from transformers import AutoModel
        # model = AutoModel.from_pretrained('openvla/openvla-7b')
        return None

    def image_callback(self, msg):
        """Store current image."""
        self.current_image = msg

    def command_callback(self, msg):
        """Process voice command."""
        command = msg.data
        self.get_logger().info(f"Received command: {command}")

        # Execute command using VLA
        self.execute_vla_command(command)

    def execute_vla_command(self, command):
        """
        Execute command using VLA model.

        Args:
            command: Natural language command
        """
        if self.current_image is None:
            self.get_logger().warn("No image available")
            return

        # Convert image
        # image = self.bridge.imgmsg_to_cv2(self.current_image)

        # Predict action from VLA model
        # action = self.vla_model.predict(image, command)

        # Execute action
        # self.execute_action(action)

        self.get_logger().info(f"Executed: {command}")


def main():
    rclpy.init()
    node = VLATaskExecutor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

### Phase 4: Testing and Validation (Week 5)

**Test Suite**

```python
# File: test_robot_system.py

import unittest
import rclpy
from your_package.navigation_controller import NavigationController
from your_package.manipulation_controller import ManipulationController


class TestRobotSystem(unittest.TestCase):
    """Test suite for robot system."""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def test_navigation_to_waypoint(self):
        """Test navigation to predefined waypoint."""
        nav = NavigationController()

        success = nav.navigate_to('shelf_A')
        self.assertTrue(success, "Failed to navigate to shelf_A")

    def test_object_detection(self):
        """Test object detection accuracy."""
        # Load test image
        # Run detection
        # Verify results
        pass

    def test_pick_and_place(self):
        """Test pick and place operation."""
        manip = ManipulationController()

        # Define test poses
        object_pose = ...
        target_pose = ...

        # Execute pick and place
        manip.pick_object(object_pose)
        manip.place_object(target_pose)

        # Verify success
        # ...

    def test_voice_command_latency(self):
        """Test voice command response time."""
        import time

        start = time.time()
        # Send voice command
        # Wait for execution
        latency = time.time() - start

        self.assertLess(latency, 3.0, "Voice command latency > 3s")

    def test_end_to_end_task(self):
        """Test complete workflow."""
        # 1. Navigate to location
        # 2. Detect object
        # 3. Pick object
        # 4. Navigate to target
        # 5. Place object
        # Verify success
        pass


if __name__ == '__main__':
    unittest.main()
```

## Evaluation Criteria

Your project will be evaluated on:

### Technical Implementation (40%)
- System architecture and design quality
- Code quality and documentation
- Integration of multiple components
- Use of best practices (ROS 2, Python)

### Functionality (30%)
- Achievement of stated goals
- Robustness and error handling
- Performance metrics (success rate, latency)

### Innovation (15%)
- Novel approaches or techniques
- Creative problem-solving
- Advanced features beyond requirements

### Documentation and Presentation (15%)
- Clear documentation (README, code comments)
- Video demonstration
- Presentation quality
- Reproducibility

## Deliverables

### 1. Source Code
- Well-organized ROS 2 package(s)
- Clear file structure
- Comprehensive comments

### 2. Documentation

**README.md:**
```markdown
# [Project Name]

## Overview
[Brief description and goals]

## System Requirements
- ROS 2 Humble
- Python 3.10+
- GPU (recommended)
- Dependencies: [list]

## Installation
```bash
# Clone repository
git clone [url]

# Install dependencies
cd [project]
pip install -r requirements.txt

# Build ROS 2 workspace
colcon build
source install/setup.bash
```

## Usage
```bash
# Launch simulation
ros2 launch [package] simulation.launch.py

# Run system
ros2 launch [package] main.launch.py
```

## Architecture
[Diagram and description]

## Demo
[Link to video or instructions]

## Performance Metrics
- Navigation success: X%
- Pick/place success: Y%
- Average task time: Z seconds

## Future Work
[Ideas for improvement]

## Contributors
[Your name]

## License
[License type]
```

### 3. Demo Video (3-5 minutes)
- System overview
- Key features demonstration
- Live task execution
- Results and metrics

### 4. Presentation Slides (10-15 slides)
- Problem statement
- Approach and architecture
- Key technical challenges
- Results and evaluation
- Lessons learned
- Future directions

## Tips for Success

### Development Best Practices

1. **Start Simple, Iterate**
   - Build core functionality first
   - Add features incrementally
   - Test frequently

2. **Version Control**
   - Use Git from day one
   - Commit regularly with clear messages
   - Tag milestones

3. **Modular Design**
   - Separate concerns (perception, planning, control)
   - Use ROS 2 nodes for modularity
   - Write reusable code

4. **Testing**
   - Test individual components
   - Integration tests
   - Simulation before hardware

5. **Documentation**
   - Document as you code
   - Explain design decisions
   - Include diagrams

### Common Pitfalls to Avoid

- Don't hardcode values - use parameters
- Don't skip error handling
- Don't neglect edge cases
- Don't wait until the end to integrate
- Don't forget to back up your work

## Resources

### Sample Projects for Inspiration

- [TIAGo Robot](https://github.com/pal-robotics/tiago_tutorials)
- [Fetch Robot](https://github.com/fetchrobotics)
- [Boston Dynamics Spot SDK](https://github.com/boston-dynamics/spot-sdk)

### Useful Tools

- **RViz 2**: Visualization
- **rqt**: Debugging and monitoring
- **Foxglove Studio**: Advanced visualization
- **Docker**: Consistent environments

## Course Reflection

Congratulations on completing the Physical AI & Humanoid Robotics course! You've learned:

1. **ROS 2 Fundamentals**: Communication patterns, tooling, development
2. **Simulation**: Gazebo, Unity, Isaac Sim
3. **AI Integration**: VLA models, perception, planning
4. **Humanoid Control**: Kinematics, balance, locomotion, manipulation
5. **Conversational AI**: Natural language interfaces

## Next Steps

Continue your robotics journey:

1. **Contribute to Open Source**
   - ROS 2 packages
   - Simulation tools
   - AI models

2. **Join Robotics Communities**
   - ROS Discourse
   - Robotics Stack Exchange
   - Local robotics clubs

3. **Advanced Topics**
   - Multi-robot systems
   - Learning from demonstration
   - Soft robotics
   - Bio-inspired control

4. **Career Opportunities**
   - Robotics engineer
   - AI researcher
   - Simulation specialist
   - Product development

## Final Thoughts

Robotics is an interdisciplinary field that combines mechanical engineering, computer science, AI, and control theory. The skills you've developed in this course provide a strong foundation for tackling real-world robotic challenges.

Remember: **The best way to learn robotics is by building robots!**

Good luck with your capstone project, and may your robots always find their way home.

---

**Congratulations on completing the Physical AI & Humanoid Robotics course!**

*For questions, reach out to the course instructors or the community forum.*
