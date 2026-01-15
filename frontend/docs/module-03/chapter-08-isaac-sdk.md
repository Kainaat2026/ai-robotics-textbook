---
id: chapter-08-isaac-sdk
title: NVIDIA Isaac SDK - AI for Robotics
module: 3
week: 6
learning_objectives:
  - Install and configure NVIDIA Isaac SDK
  - Understand Isaac SDK architecture and components
  - Use Isaac GEMs (reusable perception and navigation modules)
  - Build behavior trees for robot decision-making
  - Leverage GPU acceleration for perception tasks
estimated_time_minutes: 80
---

# NVIDIA Isaac SDK - AI for Robotics

## Introduction

NVIDIA Isaac SDK is a comprehensive robotics framework designed for AI-powered autonomous machines. It provides GPU-accelerated libraries, algorithms, and tools for perception, navigation, and manipulation. Isaac SDK is particularly powerful for deploying AI on NVIDIA Jetson edge devices and integrating with ROS 2.

**Key Features:**
- **GPU-accelerated algorithms**: Perception, SLAM, path planning
- **Modular architecture**: Reusable components called GEMs
- **Behavior trees**: Visual programming for robot decision logic
- **Hardware integration**: NVIDIA Jetson, CUDA, TensorRT
- **ROS 2 compatibility**: Seamless integration with ROS ecosystem

## Isaac SDK Architecture

### Core Components

```
┌─────────────────────────────────────────────────┐
│             Isaac Application Layer             │
│  ┌──────────────┐  ┌──────────────────────────┐ │
│  │ Behavior Tree│  │   Custom Applications    │ │
│  └──────────────┘  └──────────────────────────┘ │
├─────────────────────────────────────────────────┤
│               Isaac Engine (Gems)               │
│  ┌──────┐ ┌───────┐ ┌──────┐ ┌──────────────┐  │
│  │Vision│ │ SLAM  │ │ Plan │ │ Manipulation │  │
│  └──────┘ └───────┘ └──────┘ └──────────────┘  │
├─────────────────────────────────────────────────┤
│            Isaac Core & Communication           │
│  ┌──────────┐  ┌─────────┐  ┌──────────────┐   │
│  │ Codelets │  │ Messages│  │ Sight (Web UI)│  │
│  └──────────┘  └─────────┘  └──────────────┘   │
├─────────────────────────────────────────────────┤
│         Hardware Abstraction Layer (HAL)        │
│  ┌─────────┐ ┌──────┐ ┌───────┐ ┌──────────┐   │
│  │ Cameras │ │ LiDAR│ │  IMU  │ │  Motors  │   │
│  └─────────┘ └──────┘ └───────┘ └──────────┘   │
└─────────────────────────────────────────────────┘
```

### Key Concepts

1. **Codelets**: Modular components that perform specific tasks
2. **Nodes**: Containers that run codelets
3. **Edges**: Message channels connecting codelets
4. **GEMs**: Pre-built, optimized perception/navigation modules
5. **Behavior Trees**: Visual programming for high-level logic

## Installation

### Prerequisites

**System Requirements:**
- Ubuntu 20.04 or 22.04
- NVIDIA GPU (GTX 1060 or better) OR NVIDIA Jetson device
- CUDA 11.4+ and cuDNN
- Bazel build system

### Installing Isaac SDK

**Step 1: Install Dependencies**

```bash
# Install CUDA (if not already installed)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda-repo-ubuntu2204-12-1-local_12.1.0-530.30.02-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2204-12-1-local_12.1.0-530.30.02-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2204-12-1-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda

# Install Bazel
sudo apt install apt-transport-https curl gnupg
curl -fsSL https://bazel.build/bazel-release.pub.gpg | gpg --dearmor > bazel.gpg
sudo mv bazel.gpg /etc/apt/trusted.gpg.d/
echo "deb [arch=amd64] https://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee /etc/apt/sources.list.d/bazel.list

sudo apt update && sudo apt install bazel-5.0.0
```

**Step 2: Clone Isaac SDK**

```bash
cd ~
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git
cd isaac_ros_common
git lfs pull
```

**Step 3: Build Isaac SDK**

```bash
# Set up environment
export ISAAC_SDK_PATH=~/isaac_sdk
cd $ISAAC_SDK_PATH

# Build core SDK
bazel build //...
```

### Docker Installation (Recommended)

For easier setup, use NVIDIA's Docker containers:

```bash
# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Pull Isaac ROS Docker image
docker pull nvcr.io/nvidia/isaac-ros:2.0.0

# Run container
docker run -it --gpus all \
    --network host \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e DISPLAY=$DISPLAY \
    nvcr.io/nvidia/isaac-ros:2.0.0
```

## Understanding Codelets

Codelets are the fundamental building blocks of Isaac applications.

### Creating a Custom Codelet

Create `MyPerceptionCodelet.hpp`:

```cpp
#pragma once

#include "engine/alice/alice_codelet.hpp"
#include "messages/camera.capnp.h"
#include "messages/tensor.capnp.h"

namespace isaac {

class MyPerceptionCodelet : public alice::Codelet {
 public:
  void start() override;
  void tick() override;
  void stop() override;

  // Input: camera image
  ISAAC_PROTO_RX(ImageProto, image);

  // Output: detected objects
  ISAAC_PROTO_TX(TensorListProto, detections);

  // Parameters
  ISAAC_PARAM(double, confidence_threshold, 0.5);
  ISAAC_PARAM(int, max_detections, 10);

 private:
  void processImage(const ImageProto::Reader& image);
};

}  // namespace isaac

ISAAC_ALICE_REGISTER_CODELET(isaac::MyPerceptionCodelet);
```

Implementation `MyPerceptionCodelet.cpp`:

```cpp
#include "MyPerceptionCodelet.hpp"

namespace isaac {

void MyPerceptionCodelet::start() {
  // Initialize resources
  LOG_INFO("Perception codelet started");

  // Set tick frequency (10 Hz)
  tickPeriodically(0.1);
}

void MyPerceptionCodelet::tick() {
  // Receive image
  auto maybe_image = rx_image().tryGet();
  if (!maybe_image) {
    return;
  }

  const auto& image = *maybe_image;

  // Process image
  processImage(image.getProto());
}

void MyPerceptionCodelet::processImage(const ImageProto::Reader& image) {
  // Get parameters
  double threshold = get_confidence_threshold();
  int max_det = get_max_detections();

  LOG_INFO("Processing image with threshold: %f", threshold);

  // TODO: Run inference, detect objects

  // Create output tensor
  auto detections_proto = tx_detections().initProto();
  // ... populate with detection results

  // Publish
  tx_detections().publish();
}

void MyPerceptionCodelet::stop() {
  LOG_INFO("Perception codelet stopped");
}

}  // namespace isaac
```

### Application JSON Configuration

Create `perception_app.json`:

```json
{
  "name": "perception_application",
  "modules": [
    "perception",
    "viewers"
  ],
  "graph": {
    "nodes": [
      {
        "name": "camera",
        "components": [
          {
            "name": "camera_driver",
            "type": "isaac::sensors::V4L2Camera"
          }
        ]
      },
      {
        "name": "perception",
        "components": [
          {
            "name": "processor",
            "type": "isaac::MyPerceptionCodelet"
          }
        ]
      },
      {
        "name": "viewer",
        "components": [
          {
            "name": "image_viewer",
            "type": "isaac::viewers::ImageViewer"
          }
        ]
      }
    ],
    "edges": [
      {
        "source": "camera/camera_driver/frame",
        "target": "perception/processor/image"
      },
      {
        "source": "camera/camera_driver/frame",
        "target": "viewer/image_viewer/image"
      }
    ]
  },
  "config": {
    "camera": {
      "camera_driver": {
        "device_id": 0,
        "fps": 30,
        "resolution": [640, 480]
      }
    },
    "perception": {
      "processor": {
        "confidence_threshold": 0.7,
        "max_detections": 20
      }
    }
  }
}
```

### Running the Application

```bash
bazel run //apps/perception:perception_app
```

## Isaac GEMs - Reusable Modules

GEMs are optimized, GPU-accelerated modules for common robotics tasks.

### Stereo Depth Estimation

Use Isaac's stereo vision GEM:

```json
{
  "name": "stereo_depth_app",
  "modules": ["perception::stereo_depth"],
  "graph": {
    "nodes": [
      {
        "name": "stereo_camera",
        "components": [
          {
            "name": "left_camera",
            "type": "isaac::sensors::Camera"
          },
          {
            "name": "right_camera",
            "type": "isaac::sensors::Camera"
          }
        ]
      },
      {
        "name": "depth_estimation",
        "components": [
          {
            "name": "disparity",
            "type": "isaac::sgm::StereoDepth"
          }
        ]
      }
    ],
    "edges": [
      {
        "source": "stereo_camera/left_camera/frame",
        "target": "depth_estimation/disparity/left_image"
      },
      {
        "source": "stereo_camera/right_camera/frame",
        "target": "depth_estimation/disparity/right_image"
      }
    ]
  },
  "config": {
    "depth_estimation": {
      "disparity": {
        "min_disparity": 0,
        "max_disparity": 64,
        "use_cuda": true
      }
    }
  }
}
```

### Object Detection with DOPE

Deep Object Pose Estimation (DOPE) for 6D pose detection:

```python
from isaac import Application
import argparse

def main():
    app = Application(name="dope_inference")

    # Load DOPE module
    app.load_module('dope')

    # Create DOPE inference node
    dope_node = app.add('dope_inference')
    dope = dope_node.add(app.registry.isaac.dope.DopeInference)

    # Configure DOPE
    dope.config.model_file_path = '/path/to/dope_model.onnx'
    dope.config.object_name = 'soup_can'
    dope.config.detection_threshold = 0.5

    # Connect camera
    camera_node = app.add('camera')
    camera = camera_node.add(app.registry.isaac.sensors.V4L2Camera)

    app.connect(camera, 'frame', dope, 'image')

    # Run
    app.run()

if __name__ == '__main__':
    main()
```

### Navigation with Laikago

Use Isaac's navigation stack:

```json
{
  "name": "navigation_app",
  "modules": [
    "navigation",
    "planner",
    "sight"
  ],
  "graph": {
    "nodes": [
      {
        "name": "global_planner",
        "components": [
          {
            "name": "planner",
            "type": "isaac::planner::GlobalPlanner"
          }
        ]
      },
      {
        "name": "local_planner",
        "components": [
          {
            "name": "dwa",
            "type": "isaac::planner::DifferentialBaseControl"
          }
        ]
      },
      {
        "name": "lidar",
        "components": [
          {
            "name": "scan",
            "type": "isaac::sensors::Lidar"
          }
        ]
      }
    ],
    "edges": [
      {
        "source": "lidar/scan/scan",
        "target": "local_planner/dwa/flatscan"
      }
    ]
  },
  "config": {
    "global_planner": {
      "planner": {
        "graph_file": "maps/warehouse.json"
      }
    },
    "local_planner": {
      "dwa": {
        "robot_radius": 0.3,
        "max_linear_speed": 1.0,
        "max_angular_speed": 1.5
      }
    }
  }
}
```

## Behavior Trees

Behavior trees provide visual, hierarchical decision-making.

### Creating a Behavior Tree

Create `navigation_behavior.json`:

```json
{
  "root": {
    "type": "sequence",
    "children": [
      {
        "type": "action",
        "name": "localize",
        "action": "isaac::navigation::Localization"
      },
      {
        "type": "selector",
        "children": [
          {
            "type": "condition",
            "name": "is_goal_reached",
            "condition": "isaac::navigation::IsGoalReached"
          },
          {
            "type": "sequence",
            "children": [
              {
                "type": "action",
                "name": "compute_path",
                "action": "isaac::planner::ComputePath"
              },
              {
                "type": "action",
                "name": "follow_path",
                "action": "isaac::planner::FollowPath"
              }
            ]
          }
        ]
      }
    ]
  }
}
```

### Behavior Tree Nodes

**Sequence**: Execute children in order (fails if any child fails)
**Selector**: Try children until one succeeds
**Parallel**: Execute children simultaneously
**Decorator**: Modify child behavior (repeat, invert, etc.)

### Python API for Behavior Trees

```python
from isaac import Application, BehaviorTree

app = Application()

# Create behavior tree
bt = BehaviorTree(app, "navigation_bt")

# Build tree structure
root = bt.add_sequence("root")

localize = root.add_action(
    "localize",
    "isaac::navigation::Localization"
)

selector = root.add_selector("goal_check")

is_goal_reached = selector.add_condition(
    "is_goal_reached",
    "isaac::navigation::IsGoalReached"
)

navigate = selector.add_sequence("navigate")

compute_path = navigate.add_action(
    "compute_path",
    "isaac::planner::ComputePath"
)

follow_path = navigate.add_action(
    "follow_path",
    "isaac::planner::FollowPath"
)

# Run application
app.run()
```

## Isaac Sight - Web-based Visualization

Isaac Sight provides real-time visualization through a web browser.

### Enabling Sight

In your application JSON:

```json
{
  "name": "my_app",
  "modules": ["sight"],
  "config": {
    "websight": {
      "WebsightServer": {
        "port": 3000,
        "ui_config": {
          "windows": {
            "Camera View": {
              "renderer": "2d",
              "channels": [
                {
                  "name": "my_app/camera/camera_driver/frame"
                }
              ]
            },
            "Robot Pose": {
              "renderer": "2d",
              "channels": [
                {
                  "name": "my_app/navigation/pose"
                }
              ]
            }
          }
        }
      }
    }
  }
}
```

Access Sight at `http://localhost:3000`.

### Publishing Custom Data

```cpp
#include "engine/alice/alice_codelet.hpp"
#include "engine/gems/sight/sight.hpp"

void MyCodelet::tick() {
  // Publish scalar
  sight::Show(node(), "speed", robot_speed_);

  // Publish plot
  sight::Plot(node(), "trajectory", timestamp(), {x_, y_});

  // Publish 2D marker
  sight::Circle(node(), {x_, y_}, radius_, sight::Color::kRed);
}
```

## GPU Acceleration

Isaac SDK leverages CUDA for performance.

### Using CUDA in Codelets

```cpp
#include "engine/gems/cuda_utils/cuda_utils.hpp"

class GpuCodelet : public alice::Codelet {
 public:
  void tick() override {
    // Allocate GPU memory
    CudaBuffer<float> device_data(1024);

    // Copy to GPU
    CudaMemcpyHostToDevice(device_data.data(), host_data, 1024);

    // Launch kernel
    myKernel<<<blocks, threads>>>(device_data.data());

    // Synchronize
    cudaDeviceSynchronize();

    // Copy back
    CudaMemcpyDeviceToHost(host_result, device_data.data(), 1024);
  }
};
```

## Integration with ROS 2

Isaac SDK can bridge to ROS 2:

```json
{
  "name": "isaac_ros2_bridge",
  "modules": ["ros_bridge"],
  "graph": {
    "nodes": [
      {
        "name": "ros_bridge",
        "components": [
          {
            "name": "ros_to_isaac",
            "type": "isaac::ros_bridge::RosToIsaacBridge"
          },
          {
            "name": "isaac_to_ros",
            "type": "isaac::ros_bridge::IsaacToRosBridge"
          }
        ]
      }
    ]
  },
  "config": {
    "ros_bridge": {
      "ros_to_isaac": {
        "topics": [
          {
            "ros_topic": "/cmd_vel",
            "isaac_channel": "base_controller/command"
          }
        ]
      },
      "isaac_to_ros": {
        "topics": [
          {
            "isaac_channel": "camera/image",
            "ros_topic": "/camera/image_raw"
          }
        ]
      }
    }
  }
}
```

## Summary

- Isaac SDK provides GPU-accelerated robotics algorithms
- Codelets are modular, reusable components
- GEMs offer optimized perception and navigation capabilities
- Behavior trees enable visual programming of robot logic
- Isaac Sight provides powerful web-based visualization
- Seamless integration with ROS 2 ecosystem

## Exercises

1. Create a custom codelet that processes camera images and publishes detections
2. Build a navigation application using Isaac's global and local planners
3. Implement a behavior tree for a warehouse robot (navigate, pick, place)
4. Use Isaac DOPE for 6D object pose estimation
5. Set up Isaac Sight to visualize sensor data and robot state

## Next Chapter

In Chapter 9, we'll explore NVIDIA Isaac Sim - a photorealistic simulation platform built on Omniverse for testing and training robots in virtual environments.
