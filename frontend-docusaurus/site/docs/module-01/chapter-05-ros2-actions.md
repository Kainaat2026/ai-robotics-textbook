---
id: chapter-05-ros2-actions
title: ROS 2 Actions - Long-Running Tasks with Feedback
module: 1
week: 3
learning_objectives:
  - Understand the action pattern for long-running tasks
  - Implement action servers and clients
  - Handle goals, feedback, and results
  - Cancel actions gracefully
  - Choose between topics, services, and actions
estimated_time_minutes: 70
---

# ROS 2 Actions - Long-Running Tasks with Feedback

## Introduction

Actions are the most complex ROS 2 communication pattern, designed for long-running tasks that provide feedback and can be canceled. Think of actions as "services with progress updates" - perfect for robot navigation, manipulation, or any task that takes time.

## Why Actions?

### Limitations of Services
Services are synchronous and blocking. For a task that takes 30 seconds (like navigating across a room), the client would be blocked for the entire duration with no way to:
- Monitor progress
- Cancel if needed
- Know if the task is making progress or stuck

### Actions Solve This
Actions provide:
- **Goals**: What you want to achieve
- **Feedback**: Periodic progress updates
- **Results**: Final outcome when complete
- **Cancelation**: Ability to abort mid-execution
- **Status**: Track if goal is pending, active, or done

## Action Architecture

### Components

1. **Action Server**: Executes the long-running task
   - Accepts goals
   - Publishes feedback periodically
   - Returns result when done
   - Handles cancel requests

2. **Action Client**: Sends goals and monitors progress
   - Sends goal to server
   - Receives feedback updates
   - Gets final result
   - Can cancel goal

3. **Action Type**: Defines goal, result, and feedback structures

### Communication Flow

```
Client                    Server
  |                         |
  |--- Send Goal ---------->|
  |                         |--- Start Execution
  |<-- Accept/Reject -------|
  |                         |
  |<-- Feedback 10% --------|
  |<-- Feedback 25% --------|
  |<-- Feedback 50% --------|
  |                         |
  |- Cancel (optional) ---->|
  |                         |--- Stop Execution
  |<-- Result -------------|
```

## Standard Action Types

### example_interfaces/action/Fibonacci

Simple example for learning:

```
# Goal
int32 order
---
# Result
int32[] sequence
---
# Feedback
int32[] partial_sequence
```

### nav2_msgs/action/NavigateToPose

Real-world navigation action:

```
# Goal
geometry_msgs/PoseStamped pose
---
# Result
std_msgs/Empty result
---
# Feedback
geometry_msgs/PoseStamped current_pose
float32 distance_remaining
```

## Creating an Action Server

Let's implement a Fibonacci action server:

```python
# fibonacci_server.py
import time
import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from example_interfaces.action import Fibonacci


class FibonacciActionServer(Node):
    def __init__(self):
        super().__init__('fibonacci_action_server')

        # Create action server
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            self.execute_callback
        )

        self.get_logger().info('Fibonacci action server ready')

    def execute_callback(self, goal_handle):
        """
        Execute the Fibonacci sequence calculation.

        Args:
            goal_handle: Handle to manage goal lifecycle

        Returns:
            Result message
        """
        self.get_logger().info(f'Executing goal: order={goal_handle.request.order}')

        # Initialize feedback message
        feedback_msg = Fibonacci.Feedback()
        feedback_msg.partial_sequence = [0, 1]

        # Generate Fibonacci sequence
        for i in range(1, goal_handle.request.order):
            # Check if goal was canceled
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Goal canceled')

                result = Fibonacci.Result()
                result.sequence = feedback_msg.partial_sequence
                return result

            # Calculate next number
            feedback_msg.partial_sequence.append(
                feedback_msg.partial_sequence[i] + feedback_msg.partial_sequence[i - 1]
            )

            # Publish feedback
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(f'Publishing feedback: {feedback_msg.partial_sequence}')

            # Simulate work (1 second per number)
            time.sleep(1)

        # Goal succeeded
        goal_handle.succeed()

        # Return result
        result = Fibonacci.Result()
        result.sequence = feedback_msg.partial_sequence
        self.get_logger().info(f'Goal succeeded! Result: {result.sequence}')

        return result


def main(args=None):
    rclpy.init(args=args)
    server = FibonacciActionServer()

    try:
        rclpy.spin(server)
    except KeyboardInterrupt:
        pass

    server.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Key Points:
- `ActionServer()` creates the action server
- `execute_callback()` runs when a goal is received
- `publish_feedback()` sends progress updates
- `is_cancel_requested` checks for cancellation
- `succeed()` or `canceled()` marks completion

## Creating an Action Client

Now the client to send goals:

```python
# fibonacci_client.py
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from example_interfaces.action import Fibonacci


class FibonacciActionClient(Node):
    def __init__(self):
        super().__init__('fibonacci_action_client')

        # Create action client
        self._action_client = ActionClient(
            self,
            Fibonacci,
            'fibonacci'
        )

    def send_goal(self, order):
        """Send goal to action server."""
        self.get_logger().info('Waiting for action server...')

        # Wait for server to be available
        self._action_client.wait_for_server()

        # Create goal message
        goal_msg = Fibonacci.Goal()
        goal_msg.order = order

        self.get_logger().info(f'Sending goal: order={order}')

        # Send goal asynchronously
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        # Register callback for when goal is accepted/rejected
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        """Called when server accepts or rejects goal."""
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')

        # Get result asynchronously
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        """Called when action completes."""
        result = future.result().result
        self.get_logger().info(f'Result: {result.sequence}')

        # Shutdown after getting result
        rclpy.shutdown()

    def feedback_callback(self, feedback_msg):
        """Called when feedback is received."""
        feedback = feedback_msg.feedback
        self.get_logger().info(f'Feedback: {feedback.partial_sequence}')


def main(args=None):
    rclpy.init(args=args)

    client = FibonacciActionClient()
    client.send_goal(10)  # Calculate Fibonacci(10)

    rclpy.spin(client)


if __name__ == '__main__':
    main()
```

### Key Points:
- `ActionClient()` creates the client
- `send_goal_async()` sends goal without blocking
- `feedback_callback` receives progress updates
- Multiple callbacks handle async workflow

## Running the Action

Terminal 1 - Start server:
```bash
ros2 run my_package fibonacci_server
```

Terminal 2 - Send goal:
```bash
ros2 run my_package fibonacci_client
```

Output:
```
[fibonacci_action_client]: Sending goal: order=10
[fibonacci_action_client]: Goal accepted
[fibonacci_action_client]: Feedback: [0, 1]
[fibonacci_action_client]: Feedback: [0, 1, 1]
[fibonacci_action_client]: Feedback: [0, 1, 1, 2]
...
[fibonacci_action_client]: Result: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
```

## Canceling Actions

Client can cancel a running action:

```python
class CancelableClient(Node):
    def __init__(self):
        super().__init__('cancelable_client')
        self._action_client = ActionClient(self, Fibonacci, 'fibonacci')
        self._goal_handle = None

    def send_goal(self, order):
        goal_msg = Fibonacci.Goal()
        goal_msg.order = order

        self._send_goal_future = self._action_client.send_goal_async(goal_msg)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        self._goal_handle = future.result()

        if not self._goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')

        # Cancel after 3 seconds
        self.timer = self.create_timer(3.0, self.cancel_goal)

    def cancel_goal(self):
        """Cancel the current goal."""
        if self._goal_handle is not None:
            self.get_logger().info('Canceling goal...')
            cancel_future = self._goal_handle.cancel_goal_async()
            cancel_future.add_done_callback(self.cancel_done_callback)
            self.timer.cancel()

    def cancel_done_callback(self, future):
        cancel_response = future.result()
        if cancel_response.return_code == 0:  # SUCCESS
            self.get_logger().info('Goal successfully canceled')
        else:
            self.get_logger().info('Goal cancellation failed')
```

## Creating Custom Actions

Define custom actions for your robot's needs.

### 1. Create Action Definition

Create `action/MoveRobot.action`:

```
# Goal - Where to move
float64 target_x
float64 target_y
float64 target_theta
---
# Result - Final position
float64 final_x
float64 final_y
float64 final_theta
bool success
string message
---
# Feedback - Current position and progress
float64 current_x
float64 current_y
float64 current_theta
float32 distance_remaining
float32 percent_complete
```

### 2. Build Action

Update package configuration and build:

```bash
colcon build --packages-select my_package
source install/setup.bash
```

### 3. Implement Action Server

```python
from my_package.action import MoveRobot
from geometry_msgs.msg import Twist
import math


class MoveRobotServer(Node):
    def __init__(self):
        super().__init__('move_robot_server')

        self._action_server = ActionServer(
            self,
            MoveRobot,
            'move_robot',
            self.execute_callback
        )

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Simulated robot position
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_theta = 0.0

    def execute_callback(self, goal_handle):
        """Move robot to target position."""
        goal = goal_handle.request

        self.get_logger().info(
            f'Moving to ({goal.target_x}, {goal.target_y}, {goal.target_theta})'
        )

        # Calculate distance to target
        start_distance = math.sqrt(
            (goal.target_x - self.current_x) ** 2 +
            (goal.target_y - self.current_y) ** 2
        )

        feedback_msg = MoveRobot.Feedback()

        # Simulate movement
        rate = self.create_rate(10)  # 10 Hz
        while not self.reached_goal(goal):
            # Check for cancel
            if goal_handle.is_cancel_requested:
                self.stop_robot()
                goal_handle.canceled()

                result = MoveRobot.Result()
                result.final_x = self.current_x
                result.final_y = self.current_y
                result.final_theta = self.current_theta
                result.success = False
                result.message = 'Canceled by client'
                return result

            # Update position (simulated)
            self.move_towards_goal(goal)

            # Publish feedback
            distance = math.sqrt(
                (goal.target_x - self.current_x) ** 2 +
                (goal.target_y - self.current_y) ** 2
            )

            feedback_msg.current_x = self.current_x
            feedback_msg.current_y = self.current_y
            feedback_msg.current_theta = self.current_theta
            feedback_msg.distance_remaining = distance
            feedback_msg.percent_complete = (
                (1.0 - distance / start_distance) * 100.0
            )

            goal_handle.publish_feedback(feedback_msg)

            rate.sleep()

        # Goal reached
        self.stop_robot()
        goal_handle.succeed()

        result = MoveRobot.Result()
        result.final_x = self.current_x
        result.final_y = self.current_y
        result.final_theta = self.current_theta
        result.success = True
        result.message = 'Successfully reached target'

        return result

    def move_towards_goal(self, goal):
        """Publish velocity commands to move toward goal."""
        cmd = Twist()

        # Simple proportional control
        dx = goal.target_x - self.current_x
        dy = goal.target_y - self.current_y

        cmd.linear.x = 0.5 * math.sqrt(dx**2 + dy**2)
        cmd.angular.z = 0.5 * (goal.target_theta - self.current_theta)

        self.cmd_pub.publish(cmd)

        # Update simulated position
        self.current_x += cmd.linear.x * 0.1
        self.current_y += cmd.linear.x * 0.1
        self.current_theta += cmd.angular.z * 0.1

    def reached_goal(self, goal, tolerance=0.1):
        """Check if robot reached goal."""
        distance = math.sqrt(
            (goal.target_x - self.current_x) ** 2 +
            (goal.target_y - self.current_y) ** 2
        )
        return distance < tolerance

    def stop_robot(self):
        """Stop robot movement."""
        self.cmd_pub.publish(Twist())
```

## Command Line Tools

### List Actions

```bash
ros2 action list
```

Output:
```
/fibonacci
/move_robot
```

### Action Type

```bash
ros2 action type /fibonacci
```

Output:
```
example_interfaces/action/Fibonacci
```

### Send Goal from CLI

```bash
ros2 action send_goal /fibonacci example_interfaces/action/Fibonacci "{order: 5}" --feedback
```

Output:
```
Waiting for an action server to become available...
Sending goal:
   order: 5

Goal accepted with ID: ...

Feedback:
  partial_sequence: [0, 1]

Feedback:
  partial_sequence: [0, 1, 1]

...

Result:
  sequence: [0, 1, 1, 2, 3, 5]
```

### Action Info

```bash
ros2 action info /fibonacci
```

Output:
```
Type: example_interfaces/action/Fibonacci
Clients: 1
Servers: 1
```

## Best Practices

1. **Provide Meaningful Feedback**: Update clients on real progress, not just iteration counts

2. **Handle Cancellation**: Always check `is_cancel_requested` and stop cleanly

3. **Set Reasonable Timeouts**: Don't let actions run indefinitely

4. **Use Status Codes**: Return clear success/failure information in results

5. **Feedback Frequency**: Update every 0.5-2 seconds - not too fast, not too slow

6. **Thread Safety**: Action callbacks run in separate threads - be careful with shared state

7. **Error Handling**: Catch exceptions and return meaningful error results

## Actions in Navigation

ROS 2 Navigation Stack (Nav2) heavily uses actions:

```python
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped


class NavigationClient(Node):
    def __init__(self):
        super().__init__('navigation_client')
        self._action_client = ActionClient(
            self,
            NavigateToPose,
            'navigate_to_pose'
        )

    def navigate_to_pose(self, x, y, theta):
        """Navigate robot to target pose."""
        goal_msg = NavigateToPose.Goal()

        # Set target pose
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y

        # Set orientation (quaternion from yaw)
        goal_msg.pose.pose.orientation.w = math.cos(theta / 2)
        goal_msg.pose.pose.orientation.z = math.sin(theta / 2)

        self._action_client.wait_for_server()

        send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.navigation_feedback
        )
        send_goal_future.add_done_callback(self.goal_response_callback)

    def navigation_feedback(self, feedback_msg):
        """Display navigation progress."""
        feedback = feedback_msg.feedback
        self.get_logger().info(
            f'Distance remaining: {feedback.distance_remaining:.2f}m'
        )
```

## Summary

- Actions are for long-running, cancelable tasks with feedback
- Three components: Goal, Result, Feedback
- Server executes task, publishes feedback, returns result
- Client sends goal, receives feedback, can cancel
- Perfect for navigation, manipulation, and any multi-second operation
- Use `ActionServer` and `ActionClient` from `rclpy.action`

## Exercises

1. Create an action that counts down from N to 0 with 1-second delays
2. Implement an action server that can be paused and resumed
3. Build a client that sends multiple goals in sequence
4. Create an action for "charging battery" with feedback showing charge percentage
5. Implement timeout handling in an action client

## Next Module Preview

You've completed Module 1: ROS 2 Fundamentals! You now understand topics, services, and actions - the three core communication patterns in ROS 2.

In Module 2, we'll explore robot simulation with Gazebo and Unity, allowing you to test your ROS 2 code in virtual environments before deploying to real hardware.
