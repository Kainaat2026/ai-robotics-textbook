---
id: chapter-09-isaac-sim
title: NVIDIA Isaac Sim - Photorealistic Simulation
module: 3
week: 7
learning_objectives:
  - Set up and launch NVIDIA Isaac Sim with Omniverse
  - Create photorealistic simulation environments
  - Generate synthetic training data with domain randomization
  - Simulate physics-accurate robot behaviors
  - Integrate Isaac Sim with ROS 2 and Isaac SDK
estimated_time_minutes: 85
---

# NVIDIA Isaac Sim - Photorealistic Simulation

## Introduction

NVIDIA Isaac Sim is a robotics simulation platform built on NVIDIA Omniverse, providing photorealistic rendering, physics-accurate simulation, and scalable synthetic data generation. Unlike traditional simulators, Isaac Sim leverages RTX ray tracing for realistic lighting and materials, making it ideal for training computer vision models and testing perception algorithms.

**Key Capabilities:**
- **Photorealistic rendering**: RTX ray tracing and path tracing
- **Physics accuracy**: PhysX 5.0 with GPU acceleration
- **Synthetic data generation**: Labeled data for ML training
- **Domain randomization**: Automatic variation for sim-to-real transfer
- **ROS 2 integration**: Native support for ROS 2 communication
- **Cloud deployment**: Headless simulation on cloud GPUs

## Architecture Overview

```
┌────────────────────────────────────────────────────┐
│           Isaac Sim Application Layer              │
│  ┌──────────────┐  ┌───────────────────────────┐  │
│  │   Python API │  │  Extension Framework      │  │
│  └──────────────┘  └───────────────────────────┘  │
├────────────────────────────────────────────────────┤
│              Isaac Sim Core Features               │
│  ┌─────────┐ ┌──────────┐ ┌────────────────────┐  │
│  │  Robots │ │ Sensors  │ │ Synthetic Data Gen │  │
│  └─────────┘ └──────────┘ └────────────────────┘  │
├────────────────────────────────────────────────────┤
│            NVIDIA Omniverse Platform               │
│  ┌──────┐ ┌───────┐ ┌────────┐ ┌──────────────┐   │
│  │  USD │ │ PhysX │ │  RTX   │ │   Nucleus    │   │
│  └──────┘ └───────┘ └────────┘ └──────────────┘   │
└────────────────────────────────────────────────────┘
```

**Key Technologies:**
- **USD (Universal Scene Description)**: Open-source scene format
- **PhysX 5.0**: High-fidelity physics simulation
- **RTX**: Real-time ray tracing for photorealistic rendering
- **Nucleus**: Collaboration and asset management

## Installation

### System Requirements

- **OS**: Ubuntu 20.04/22.04 or Windows 10/11
- **GPU**: NVIDIA RTX 2070 or higher (RTX 3080+ recommended)
- **RAM**: 32 GB minimum (64 GB recommended)
- **VRAM**: 8 GB minimum (12+ GB recommended)
- **Storage**: 50 GB free space

### Installing Isaac Sim

**Method 1: Omniverse Launcher (Recommended)**

1. Download NVIDIA Omniverse Launcher:
   ```bash
   wget https://install.launcher.omniverse.nvidia.com/installers/omniverse-launcher-linux.AppImage
   chmod +x omniverse-launcher-linux.AppImage
   ./omniverse-launcher-linux.AppImage
   ```

2. In Omniverse Launcher:
   - Navigate to **Exchange** tab
   - Search for "Isaac Sim"
   - Click **Install** (version 2023.1.0 or later)

3. Launch Isaac Sim from **Library** tab

**Method 2: Docker Container**

```bash
# Pull Isaac Sim container
docker pull nvcr.io/nvidia/isaac-sim:2023.1.0

# Run container
docker run --name isaac-sim --entrypoint bash -it --gpus all \
  -e "ACCEPT_EULA=Y" \
  -v ~/docker/isaac-sim/cache/kit:/isaac-sim/kit/cache:rw \
  -v ~/docker/isaac-sim/cache/ov:/root/.cache/ov:rw \
  -v ~/docker/isaac-sim/cache/pip:/root/.cache/pip:rw \
  -v ~/docker/isaac-sim/cache/glcache:/root/.cache/nvidia/GLCache:rw \
  -v ~/docker/isaac-sim/cache/computecache:/root/.nv/ComputeCache:rw \
  -v ~/docker/isaac-sim/logs:/root/.nvidia-omniverse/logs:rw \
  -v ~/docker/isaac-sim/data:/root/.local/share/ov/data:rw \
  -v ~/docker/isaac-sim/documents:/root/Documents:rw \
  nvcr.io/nvidia/isaac-sim:2023.1.0

# Inside container, run Isaac Sim
./runheadless.native.sh
```

**Method 3: pip Installation**

```bash
# Create virtual environment
python3 -m venv isaac_sim_venv
source isaac_sim_venv/bin/activate

# Install Isaac Sim Python package
pip install isaacsim==2023.1.0 --extra-index-url https://pypi.nvidia.com
```

### Verification

Launch Isaac Sim:

```bash
# GUI mode
~/.local/share/ov/pkg/isaac_sim-2023.1.0/isaac-sim.sh

# Headless mode (no GUI)
~/.local/share/ov/pkg/isaac_sim-2023.1.0/isaac-sim.headless.sh
```

## Getting Started with Isaac Sim

### Basic Python API

Create `hello_isaac_sim.py`:

```python
from omni.isaac.kit import SimulationApp

# Launch Isaac Sim
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.core.objects import DynamicCuboid
from omni.isaac.core.prims import RigidPrim
import numpy as np

# Create world
world = World()

# Add ground plane
world.scene.add_default_ground_plane()

# Add a cube
cube = world.scene.add(
    DynamicCuboid(
        prim_path="/World/Cube",
        name="my_cube",
        position=np.array([0, 0, 1.0]),
        size=np.array([0.5, 0.5, 0.5]),
        color=np.array([0.8, 0.2, 0.2])
    )
)

# Reset world
world.reset()

# Run simulation
for i in range(1000):
    world.step(render=True)

# Cleanup
simulation_app.close()
```

Run:
```bash
python hello_isaac_sim.py
```

### Loading Robot Models

Import a robot from URDF/USD:

```python
from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.core.robots import Robot
from omni.isaac.core.utils.stage import add_reference_to_stage
import carb

# Create world
world = World()
world.scene.add_default_ground_plane()

# Import robot from USD
robot_usd_path = "/Isaac/Robots/Franka/franka.usd"
robot_prim_path = "/World/Franka"

add_reference_to_stage(
    usd_path=carb.tokens.get_tokens_interface().resolve(robot_usd_path),
    prim_path=robot_prim_path
)

# Create robot object
robot = world.scene.add(
    Robot(
        prim_path=robot_prim_path,
        name="franka"
    )
)

# Reset and run
world.reset()

for i in range(1000):
    world.step(render=True)

simulation_app.close()
```

## Creating Environments

### Building a Scene

Create a warehouse environment:

```python
from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.core.objects import VisualCuboid, DynamicCuboid
from omni.isaac.core.prims import GeometryPrim
import numpy as np

world = World()
world.scene.add_default_ground_plane()

# Create warehouse walls
def create_wall(path, position, size):
    wall = world.scene.add(
        VisualCuboid(
            prim_path=path,
            name=path.split("/")[-1],
            position=position,
            size=size,
            color=np.array([0.7, 0.7, 0.7])
        )
    )
    return wall

# Walls (forming a rectangular room)
create_wall("/World/Wall_North", np.array([0, 5, 1.5]), np.array([10, 0.2, 3]))
create_wall("/World/Wall_South", np.array([0, -5, 1.5]), np.array([10, 0.2, 3]))
create_wall("/World/Wall_East", np.array([5, 0, 1.5]), np.array([0.2, 10, 3]))
create_wall("/World/Wall_West", np.array([-5, 0, 1.5]), np.array([0.2, 10, 3]))

# Create shelving units
for i in range(4):
    for j in range(3):
        shelf = world.scene.add(
            VisualCuboid(
                prim_path=f"/World/Shelf_{i}_{j}",
                name=f"shelf_{i}_{j}",
                position=np.array([-3 + i * 2, -3 + j * 2.5, 0.75]),
                size=np.array([0.8, 1.5, 1.5]),
                color=np.array([0.6, 0.4, 0.2])
            )
        )

# Create boxes to pick
for i in range(10):
    box = world.scene.add(
        DynamicCuboid(
            prim_path=f"/World/Box_{i}",
            name=f"box_{i}",
            position=np.array([
                np.random.uniform(-4, 4),
                np.random.uniform(-4, 4),
                0.5
            ]),
            size=np.array([0.3, 0.3, 0.3]),
            color=np.array([
                np.random.rand(),
                np.random.rand(),
                np.random.rand()
            ])
        )
    )

world.reset()

# Run simulation
for i in range(2000):
    world.step(render=True)

simulation_app.close()
```

### Importing Custom Assets

Load custom 3D models:

```python
from omni.isaac.core.utils.stage import add_reference_to_stage
from pxr import UsdGeom, Gf

# Import OBJ/FBX/USD file
asset_path = "/path/to/your/model.usd"
prim_path = "/World/CustomAsset"

add_reference_to_stage(usd_path=asset_path, prim_path=prim_path)

# Set transform
xform = UsdGeom.Xformable(stage.GetPrimAtPath(prim_path))
xform.ClearXformOpOrder()
xform.AddTranslateOp().Set(Gf.Vec3d(0, 0, 1))
xform.AddRotateXYZOp().Set(Gf.Vec3d(0, 0, 90))
xform.AddScaleOp().Set(Gf.Vec3d(0.01, 0.01, 0.01))
```

## Sensors in Isaac Sim

### Camera Sensor

Create RGB camera:

```python
from omni.isaac.sensor import Camera
import numpy as np

# Create camera
camera = Camera(
    prim_path="/World/Camera",
    position=np.array([2.0, 2.0, 2.0]),
    frequency=30,
    resolution=(1280, 720),
    orientation=np.array([0.5, -0.5, 0.5, -0.5])  # quaternion
)

# Initialize camera
camera.initialize()

# Get camera data
world.reset()
world.step(render=True)

# Capture frame
rgb = camera.get_rgba()[:, :, :3]  # Get RGB (drop alpha)
print(f"Captured image shape: {rgb.shape}")

# Save image
import cv2
cv2.imwrite("camera_output.png", cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
```

### Depth Camera

```python
from omni.isaac.sensor import Camera

depth_camera = Camera(
    prim_path="/World/DepthCamera",
    position=np.array([2.0, 0.0, 2.0]),
    frequency=20,
    resolution=(640, 480)
)

depth_camera.initialize()
depth_camera.add_depth_to_frame()

world.step(render=True)

# Get depth data
depth = depth_camera.get_depth()
print(f"Depth range: {depth.min():.2f}m to {depth.max():.2f}m")
```

### LiDAR Sensor

Create rotating LiDAR:

```python
from omni.isaac.range_sensor import _range_sensor

# Create LiDAR using RTX raytracing
lidar_config = _range_sensor.acquire_lidar_sensor_interface()

result, lidar = lidar_config.create_lidar(
    "/World/Lidar",
    parent="/World/Robot",
    min_range=0.4,
    max_range=100.0,
    draw_points=True,
    draw_lines=False,
    horizontal_fov=360.0,
    vertical_fov=30.0,
    horizontal_resolution=0.4,
    vertical_resolution=4.0,
    rotation_rate=20.0,  # Hz
    high_lod=True,
    yaw_offset=0.0,
    enable_semantics=False
)

# Read LiDAR data
def get_lidar_data():
    depth = lidar_config.get_linear_depth_data("/World/Lidar")
    points = lidar_config.get_point_cloud_data("/World/Lidar")
    return depth, points

world.step(render=True)
depth, points = get_lidar_data()
print(f"LiDAR captured {len(points)} points")
```

## Synthetic Data Generation

### Replicator for Data Generation

Isaac Sim uses Replicator for synthetic data:

```python
import omni.replicator.core as rep

# Register camera
camera = rep.create.camera(position=(5, 5, 5), look_at=(0, 0, 0))

# Create randomizer function
def randomize_scene():
    # Randomize lighting
    light = rep.create.light(
        light_type="Sphere",
        color=rep.distribution.uniform((0.8, 0.8, 0.8), (1.0, 1.0, 1.0)),
        intensity=rep.distribution.uniform(10000, 50000),
        position=rep.distribution.uniform((-5, -5, 3), (5, 5, 8))
    )

    # Randomize object poses
    with rep.create.group(["/World/Box_*"]):
        rep.modify.pose(
            position=rep.distribution.uniform((-4, -4, 0.5), (4, 4, 2)),
            rotation=rep.distribution.uniform((0, 0, 0), (360, 360, 360))
        )

    return light.node

# Register randomization
rep.randomizer.register(randomize_scene)

# Attach writer for RGB images
writer = rep.WriterRegistry.get("BasicWriter")
writer.initialize(
    output_dir="_output_rgb",
    rgb=True,
    bounding_box_2d_tight=True
)

# Run data generation
rep.orchestrator.run_until_complete(num_frames=1000)
```

### Bounding Box Annotations

Generate labeled bounding boxes:

```python
import omni.replicator.core as rep
from omni.isaac.core.utils.semantics import add_update_semantics

# Add semantic labels to objects
for i in range(10):
    prim_path = f"/World/Box_{i}"
    add_update_semantics(
        prim=stage.GetPrimAtPath(prim_path),
        semantic_label="box",
        type_label="class"
    )

# Create camera with semantic segmentation
camera = rep.create.camera()

# Enable bounding box annotations
render_product = rep.create.render_product(camera, (1024, 1024))

# Attach writer with bounding boxes
writer = rep.WriterRegistry.get("BasicWriter")
writer.initialize(
    output_dir="_output_labeled",
    rgb=True,
    bounding_box_2d_tight=True,
    semantic_segmentation=True,
    instance_segmentation=True
)
writer.attach([render_product])

# Generate data
with rep.trigger.on_frame(num_frames=500):
    rep.randomizer.randomize_scene()

rep.orchestrator.run()
```

### Domain Randomization

Randomize appearance for sim-to-real transfer:

```python
import omni.replicator.core as rep

def domain_randomize():
    # Randomize textures
    with rep.create.group(["/World/Floor", "/World/Wall_*"]):
        rep.randomizer.texture(
            textures=rep.distribution.choice([
                "concrete",
                "wood",
                "metal",
                "tiles"
            ])
        )

    # Randomize colors
    with rep.create.group(["/World/Box_*"]):
        rep.randomizer.color(
            colors=rep.distribution.uniform((0, 0, 0), (1, 1, 1))
        )

    # Randomize lighting
    rep.create.light(
        light_type="Dome",
        intensity=rep.distribution.uniform(500, 2000),
        temperature=rep.distribution.uniform(4000, 8000)
    )

    # Randomize camera parameters
    camera = rep.get.prims(path_pattern="/World/Camera")
    with camera:
        rep.modify.pose(
            position=rep.distribution.uniform((3, 3, 2), (7, 7, 5)),
            look_at=(0, 0, 0)
        )

rep.randomizer.register(domain_randomize)

# Generate diverse dataset
with rep.trigger.on_frame(num_frames=2000):
    rep.randomizer.domain_randomize()

rep.orchestrator.run()
```

## Physics Simulation

### Configuring PhysX

Adjust physics parameters:

```python
from omni.isaac.core.utils.physics import set_physics_scene_asyncsimrender
from omni.isaac.core import PhysicsContext

# Create physics context
physics_context = PhysicsContext()

# Configure physics scene
physics_context.set_gravity(-9.81)  # m/s^2
physics_context.set_solver_type("TGS")  # Temporal Gauss-Seidel
physics_context.enable_gpu_dynamics(True)
physics_context.enable_ccd(True)  # Continuous collision detection

# Set simulation parameters
physics_context.set_physics_dt(1.0 / 120.0)  # 120 Hz physics
```

### Contact Sensors

Detect collisions:

```python
from omni.isaac.sensor import ContactSensor

# Create contact sensor
contact_sensor = ContactSensor(
    prim_path="/World/Robot/contact_sensor",
    min_threshold=0,
    max_threshold=1000000,
    radius=0.05
)

contact_sensor.initialize()

# Check for contact
world.step(render=True)

reading = contact_sensor.get_current_frame()
if reading["is_valid"]:
    if reading["in_contact"]:
        force = reading["value"]
        print(f"Contact detected! Force: {force} N")
```

## ROS 2 Integration

### Enabling ROS 2 Bridge

```python
from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

# Enable ROS2 extension
from omni.isaac.core.utils.extensions import enable_extension
enable_extension("omni.isaac.ros2_bridge")

import rclpy
from omni.isaac.core import World

# Initialize ROS 2
rclpy.init()

world = World()
world.scene.add_default_ground_plane()

# Rest of your simulation code...

world.reset()

for i in range(1000):
    world.step(render=True)
    rclpy.spin_once(timeout_sec=0.0)

# Cleanup
rclpy.shutdown()
simulation_app.close()
```

### Publishing Camera Images

```python
from omni.isaac.ros2_bridge import Camera

# Create ROS 2 camera publisher
ros_camera = Camera(
    prim_path="/World/Camera",
    topic_name="/camera/image_raw",
    freq=30
)

ros_camera.initialize()

# Camera images automatically published to ROS 2 topic
```

### Subscribing to cmd_vel

Control robot via ROS 2:

```python
from omni.isaac.core.robots import Robot
from omni.isaac.ros2_bridge import TwistSubscriber

robot = world.scene.add(Robot(prim_path="/World/Robot"))

# Create twist subscriber
twist_sub = TwistSubscriber("/cmd_vel")

def control_loop():
    twist = twist_sub.get_twist()
    if twist:
        # Apply velocities to robot
        robot.set_linear_velocity(np.array([twist.linear.x, twist.linear.y, 0]))
        robot.set_angular_velocity(np.array([0, 0, twist.angular.z]))

# In simulation loop
for i in range(1000):
    control_loop()
    world.step(render=True)
```

## Summary

- Isaac Sim provides photorealistic, physics-accurate robot simulation
- Built on Omniverse with USD, PhysX 5.0, and RTX rendering
- Synthetic data generation with Replicator enables ML training
- Domain randomization bridges the sim-to-real gap
- Native ROS 2 integration for seamless communication
- Scalable cloud deployment for large-scale simulations

## Exercises

1. Create a custom warehouse environment with shelves and boxes
2. Set up a camera to generate 1,000 labeled images with bounding boxes
3. Implement domain randomization for lighting and textures
4. Create a LiDAR sensor and visualize point clouds in RViz
5. Build a ROS 2 controlled robot that navigates using Isaac Sim sensors

## Next Chapter

In Chapter 10, we'll tackle the sim-to-real transfer challenge - learning how to bridge the gap between simulation and physical robots through domain randomization, system identification, and transfer learning.
