---
id: chapter-04-ros2-services
title: ROS 2 Services - Request-Response Communication
module: 1
week: 2
learning_objectives:
  - Understand the service pattern for synchronous communication
  - Create service servers and clients in Python
  - Define custom service types
  - Handle service timeouts and failures
  - Choose between topics and services appropriately
estimated_time_minutes: 60
---

# ROS 2 Services - Request-Response Communication

## Introduction

While topics provide asynchronous, many-to-many communication, services implement synchronous request-response patterns. Services are ideal for operations that require immediate feedback, like "compute the inverse kinematics for this pose" or "capture an image now."

## Service Architecture

### Request-Response Pattern

Services use a client-server model:

- **Service Server**: Provides a service, processes requests, returns responses
- **Service Client**: Sends requests, waits for responses
- **Service Type**: Defines request and response message structures

Unlike topics, service communication is:
- **One-to-one**: One client per request to one server
- **Synchronous**: Client blocks until response received (or timeout)
- **Transient**: No message history retained

## When to Use Services vs Topics

### Use Services When:
- You need confirmation or a result
- Operation is occasional, not continuous
- Request-response semantics are natural
- Examples: "Take photo", "Calculate path", "Get status"

### Use Topics When:
- Continuous data streams (sensor readings)
- Broadcasting to multiple subscribers
- Fire-and-forget semantics
- High-frequency updates

## Standard Service Types

ROS 2 provides standard service types in common packages:

### std_srvs - Basic Services

```python
from std_srvs.srv import SetBool, Trigger, Empty

# SetBool - Boolean parameter with success/message response
# Request: bool data
# Response: bool success, string message

# Trigger - No input, returns success/message
# Request: (empty)
# Response: bool success, string message

# Empty - No input, no output (just call confirmation)
# Request: (empty)
# Response: (empty)
```

### example_interfaces - Common Patterns

```python
from example_interfaces.srv import AddTwoInts

# AddTwoInts - Simple arithmetic example
# Request: int64 a, int64 b
# Response: int64 sum
```

## Creating a Service Server

Let's create a server that adds two integers:

```python
# service_server.py
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class AddTwoIntsServer(Node):
    def __init__(self):
        super().__init__('add_two_ints_server')

        # Create service
        self.srv = self.create_service(
            AddTwoInts,              # Service type
            'add_two_ints',          # Service name
            self.add_two_ints_callback  # Callback function
        )

        self.get_logger().info('Add Two Ints service ready')

    def add_two_ints_callback(self, request, response):
        """
        Service callback - processes request and fills response.

        Args:
            request: AddTwoInts.Request with a and b fields
            response: AddTwoInts.Response with sum field

        Returns:
            response: Filled response object
        """
        response.sum = request.a + request.b

        self.get_logger().info(
            f'Incoming request: a={request.a}, b={request.b}'
        )
        self.get_logger().info(f'Sending response: sum={response.sum}')

        return response


def main(args=None):
    rclpy.init(args=args)
    server = AddTwoIntsServer()

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
- `create_service()` registers the service with the ROS 2 network
- Callback receives `request` and `response` objects
- Callback must return the filled `response`
- Server runs continuously, handling requests as they arrive

## Creating a Service Client

Now let's create a client that calls this service:

```python
# service_client.py
import sys
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class AddTwoIntsClient(Node):
    def __init__(self):
        super().__init__('add_two_ints_client')

        # Create client
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')

        # Wait for service to be available
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting...')

        self.get_logger().info('Service available, ready to send requests')

    def send_request(self, a, b):
        """
        Send request to service and wait for response.

        Args:
            a: First integer
            b: Second integer

        Returns:
            Response from service or None if failed
        """
        # Create request
        request = AddTwoInts.Request()
        request.a = a
        request.b = b

        self.get_logger().info(f'Sending request: {a} + {b}')

        # Call service (asynchronously)
        future = self.cli.call_async(request)

        # Wait for response
        rclpy.spin_until_future_complete(self, future)

        if future.result() is not None:
            response = future.result()
            self.get_logger().info(f'Result: {response.sum}')
            return response
        else:
            self.get_logger().error('Service call failed')
            return None


def main(args=None):
    rclpy.init(args=args)

    # Get numbers from command line
    if len(sys.argv) != 3:
        print('Usage: service_client.py <a> <b>')
        return

    a = int(sys.argv[1])
    b = int(sys.argv[2])

    client = AddTwoIntsClient()
    response = client.send_request(a, b)

    client.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Key Points:
- `create_client()` creates a client proxy
- `wait_for_service()` checks if server is running
- `call_async()` sends request and returns a Future
- `spin_until_future_complete()` waits for response

## Running the Service

Terminal 1 - Start server:
```bash
ros2 run my_package service_server
```

Terminal 2 - Call service:
```bash
ros2 run my_package service_client 10 20
# Output: Result: 30
```

## Creating Custom Services

For custom functionality, define your own service types.

### 1. Create Service Definition

Create `srv/ComputeRectangleArea.srv`:

```
# Request
float64 length
float64 width
---
# Response
float64 area
bool success
string message
```

The `---` separator divides request from response.

### 2. Update package.xml

```xml
<depend>rosidl_default_generators</depend>
<depend>rosidl_default_runtime</depend>
<member_of_group>rosidl_interface_packages</member_of_group>
```

### 3. Update CMakeLists.txt (C++) or setup.py (Python)

For Python packages:

```python
from setuptools import setup

setup(
    # ...
    data_files=[
        # ...
        ('share/' + package_name + '/srv', ['srv/ComputeRectangleArea.srv']),
    ],
)
```

### 4. Build Package

```bash
colcon build --packages-select my_package
source install/setup.bash
```

### 5. Use Custom Service

```python
from my_package.srv import ComputeRectangleArea

class AreaServer(Node):
    def __init__(self):
        super().__init__('area_server')
        self.srv = self.create_service(
            ComputeRectangleArea,
            'compute_area',
            self.compute_callback
        )

    def compute_callback(self, request, response):
        if request.length <= 0 or request.width <= 0:
            response.success = False
            response.message = 'Dimensions must be positive'
            response.area = 0.0
        else:
            response.area = request.length * request.width
            response.success = True
            response.message = 'Area computed successfully'

        return response
```

## Handling Timeouts

Clients should handle cases where services don't respond:

```python
def send_request_with_timeout(self, a, b, timeout_sec=5.0):
    """Send request with timeout."""
    request = AddTwoInts.Request()
    request.a = a
    request.b = b

    future = self.cli.call_async(request)

    # Wait with timeout
    rclpy.spin_until_future_complete(
        self,
        future,
        timeout_sec=timeout_sec
    )

    if future.done():
        if future.result() is not None:
            return future.result()
        else:
            self.get_logger().error('Service call failed')
    else:
        self.get_logger().error('Service call timed out')

    return None
```

## Asynchronous Client Calls

For non-blocking service calls:

```python
class AsyncClient(Node):
    def __init__(self):
        super().__init__('async_client')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')

    def send_request_async(self, a, b):
        """Send request without blocking."""
        request = AddTwoInts.Request()
        request.a = a
        request.b = b

        # Send request asynchronously
        future = self.cli.call_async(request)

        # Register callback for when response arrives
        future.add_done_callback(self.response_callback)

    def response_callback(self, future):
        """Called when response is received."""
        try:
            response = future.result()
            self.get_logger().info(f'Got result: {response.sum}')
        except Exception as e:
            self.get_logger().error(f'Service call failed: {e}')
```

## Command Line Tools

### List Services

```bash
ros2 service list
```

Output:
```
/add_two_ints
/compute_area
```

### Service Type

```bash
ros2 service type /add_two_ints
```

Output:
```
example_interfaces/srv/AddTwoInts
```

### Call Service from CLI

```bash
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 5, b: 3}"
```

Output:
```
requester: making request: example_interfaces.srv.AddTwoInts_Request(a=5, b=3)

response:
example_interfaces.srv.AddTwoInts_Response(sum=8)
```

### Service Info

```bash
ros2 service info /add_two_ints
```

Output:
```
Type: example_interfaces/srv/AddTwoInts
Clients count: 1
Services count: 1
```

## Practical Example: Robot Control Service

Let's create a realistic robot control service:

```python
# robot_control_server.py
from geometry_msgs.msg import Twist
from std_srvs.srv import SetBool


class RobotControlServer(Node):
    def __init__(self):
        super().__init__('robot_control_server')

        # Service to enable/disable motors
        self.enable_srv = self.create_service(
            SetBool,
            'enable_motors',
            self.enable_motors_callback
        )

        # Publisher for velocity commands
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.motors_enabled = False

        self.get_logger().info('Robot control server ready')

    def enable_motors_callback(self, request, response):
        """Enable or disable robot motors."""
        self.motors_enabled = request.data

        if self.motors_enabled:
            response.success = True
            response.message = 'Motors enabled'
            self.get_logger().info('Motors enabled')
        else:
            # Stop robot when disabling
            stop_cmd = Twist()
            self.cmd_pub.publish(stop_cmd)

            response.success = True
            response.message = 'Motors disabled, robot stopped'
            self.get_logger().info('Motors disabled')

        return response
```

Client usage:

```python
# Enable motors
client = create_client(SetBool, 'enable_motors')
request = SetBool.Request()
request.data = True
response = client.call(request)

if response.success:
    print('Robot ready to move')
```

## Best Practices

1. **Keep Services Fast**: Services block the client. For long operations, use actions instead.

2. **Always Return Response**: Even on error, return a valid response with error info.

3. **Validate Input**: Check request parameters before processing.

4. **Use Timeouts**: Don't let clients hang indefinitely.

5. **Log Important Events**: Log service calls for debugging.

6. **Idempotency**: Design services to be safely callable multiple times.

7. **Error Messages**: Provide clear, actionable error messages in responses.

## Services vs Topics vs Actions

| Feature | Topics | Services | Actions |
|---------|--------|----------|---------|
| Pattern | Pub-Sub | Request-Response | Goal-Feedback-Result |
| Synchronous | No | Yes | No |
| Return value | No | Yes | Yes + Feedback |
| Cancelable | No | No | Yes |
| Use case | Streaming data | Quick queries | Long tasks |

## Summary

- Services implement synchronous request-response communication
- Ideal for operations requiring immediate confirmation
- Use `create_service()` for servers, `create_client()` for clients
- Custom service types defined in `.srv` files
- Always handle timeouts and errors gracefully
- Choose services for occasional queries, topics for streams

## Exercises

1. Create a service that converts temperature between Celsius and Fahrenheit
2. Build a service that checks if a number is prime
3. Implement a service that returns robot battery level
4. Create a client that calls multiple services in sequence
5. Add timeout handling to an existing service client

## Next Chapter Preview

In the next chapter, we'll explore ROS 2 Actions - the pattern for long-running, cancelable tasks with progress feedback. Actions combine the best of topics and services for operations like navigation and manipulation.
