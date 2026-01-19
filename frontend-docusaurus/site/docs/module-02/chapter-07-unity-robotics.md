---
id: chapter-07-unity-robotics
title: Unity Robotics - High-Fidelity Simulation
module: 2
week: 5
learning_objectives:
  - Set up Unity with ROS 2 integration
  - Create realistic physics-based environments in Unity
  - Use Unity for robotic perception and computer vision tasks
  - Leverage Unity ML-Agents for reinforcement learning
  - Build photorealistic simulation scenarios
estimated_time_minutes: 75
---

# Unity Robotics - High-Fidelity Simulation

## Introduction

Unity is a powerful game engine that has become increasingly popular for robotics simulation. While Gazebo excels at physics accuracy, Unity offers photorealistic graphics, advanced rendering, and a rich ecosystem of tools for creating complex simulation environments. Unity Robotics combines the visual fidelity of game engines with the robotic framework of ROS 2.

Unity is particularly valuable for:
- **Perception tasks**: Training computer vision models with synthetic data
- **Human-robot interaction**: Realistic avatars and environments
- **Reinforcement learning**: Unity ML-Agents provides state-of-the-art RL capabilities
- **Presentation and demos**: High-quality visualization for stakeholders

## Unity Robotics Hub

### Architecture Overview

Unity Robotics Hub provides the bridge between Unity and ROS 2:

```
┌─────────────────┐         ┌──────────────────┐
│   Unity Editor  │ ◄─────► │  ROS 2 Network   │
│                 │  TCP/IP │                  │
│  - Simulation   │         │  - Nodes         │
│  - Rendering    │         │  - Topics        │
│  - ML-Agents    │         │  - Services      │
└─────────────────┘         └──────────────────┘
```

**Key Components:**
1. **ROS-TCP-Connector**: Unity package for ROS communication
2. **ROS-TCP-Endpoint**: ROS 2 node that bridges Unity to ROS network
3. **URDF Importer**: Imports robot models from URDF to Unity
4. **Perception SDK**: Generates labeled synthetic data

### Installation

**Step 1: Install Unity Hub and Unity Editor**

Download Unity Hub from [unity.com](https://unity.com/download):

```bash
# On Ubuntu, install Unity Hub
wget -qO - https://hub.unity3d.com/linux/keys/public | gpg --dearmor | sudo tee /usr/share/keyrings/unity-archive-keyring.gpg > /dev/null

sudo sh -c 'echo "deb [signed-by=/usr/share/keyrings/unity-archive-keyring.gpg] https://hub.unity3d.com/linux/repos/deb stable main" > /etc/apt/sources.list.d/unityhub.list'

sudo apt update
sudo apt install unityhub
```

Install Unity Editor version **2021.3 LTS** (recommended for robotics).

**Step 2: Create Unity Project**

1. Open Unity Hub
2. Click "New Project"
3. Select "3D" template
4. Name it "RoboticsSimulation"
5. Click "Create Project"

**Step 3: Install Unity Robotics Packages**

In Unity Editor:
1. Open **Window > Package Manager**
2. Click "+" > "Add package from git URL"
3. Add these packages:

```
https://github.com/Unity-Technologies/ROS-TCP-Connector.git?path=/com.unity.robotics.ros-tcp-connector
https://github.com/Unity-Technologies/URDF-Importer.git?path=/com.unity.robotics.urdf-importer
https://github.com/Unity-Technologies/com.unity.perception.git
```

**Step 4: Install ROS 2 Endpoint**

```bash
# In your ROS 2 workspace
cd ~/ros2_ws/src
git clone https://github.com/Unity-Technologies/ROS-TCP-Endpoint.git

cd ~/ros2_ws
colcon build --packages-select ros_tcp_endpoint
source install/setup.bash
```

## ROS-Unity Communication

### Setting Up the Connection

**Launch ROS-TCP-Endpoint:**

```bash
ros2 run ros_tcp_endpoint default_server_endpoint --ros-args -p ROS_IP:=127.0.0.1
```

This creates a TCP server on port 10000.

**Configure Unity:**

1. In Unity, go to **Robotics > ROS Settings**
2. Set **ROS IP Address**: `127.0.0.1`
3. Set **ROS Port**: `10000`
4. Set **Protocol**: `ROS 2`

### Publishing from Unity to ROS

Create a C# script `UnityRobotPublisher.cs`:

```csharp
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Geometry;

public class UnityRobotPublisher : MonoBehaviour
{
    ROSConnection ros;
    public string topicName = "unity/pose";
    public float publishRate = 10f;

    private float timer;

    void Start()
    {
        // Get ROS connection
        ros = ROSConnection.GetOrCreateInstance();

        // Register publisher
        ros.RegisterPublisher<PoseStampedMsg>(topicName);
    }

    void Update()
    {
        timer += Time.deltaTime;

        if (timer > 1f / publishRate)
        {
            timer = 0;
            PublishPose();
        }
    }

    void PublishPose()
    {
        // Create pose message
        PoseStampedMsg poseMsg = new PoseStampedMsg
        {
            header = new RosMessageTypes.Std.HeaderMsg
            {
                stamp = new RosMessageTypes.BuiltinInterfaces.TimeMsg
                {
                    sec = (int)Time.time,
                    nanosec = (uint)((Time.time % 1) * 1e9)
                },
                frame_id = "unity_frame"
            },
            pose = new PoseMsg
            {
                position = new PointMsg
                {
                    x = transform.position.x,
                    y = transform.position.y,
                    z = transform.position.z
                },
                orientation = new QuaternionMsg
                {
                    x = transform.rotation.x,
                    y = transform.rotation.y,
                    z = transform.rotation.z,
                    w = transform.rotation.w
                }
            }
        };

        // Publish
        ros.Publish(topicName, poseMsg);
    }
}
```

**Verify in ROS 2:**

```bash
ros2 topic echo /unity/pose
```

### Subscribing in Unity to ROS

Create `UnityRobotSubscriber.cs`:

```csharp
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Geometry;

public class UnityRobotSubscriber : MonoBehaviour
{
    public string topicName = "cmd_vel";
    public float speed = 1.0f;
    public float turnSpeed = 1.0f;

    void Start()
    {
        ROSConnection.GetOrCreateInstance().Subscribe<TwistMsg>(topicName, MoveRobot);
    }

    void MoveRobot(TwistMsg twist)
    {
        // Apply linear velocity
        Vector3 linearVel = new Vector3(
            (float)twist.linear.x,
            0,
            (float)twist.linear.y
        );
        transform.position += linearVel * speed * Time.deltaTime;

        // Apply angular velocity
        float angularVel = (float)twist.angular.z;
        transform.Rotate(0, angularVel * turnSpeed * Time.deltaTime, 0);
    }
}
```

## URDF Import and Robot Setup

### Importing URDF Models

Unity can import URDF files directly:

1. **Robotics > Import Robot from URDF**
2. Browse to your `.urdf` file
3. Configure import settings:
   - **Axis Type**: Y-axis (Unity) or Z-axis (ROS)
   - **Mesh Decomposer**: VHACD (for collision meshes)
4. Click **Import URDF**

### Configuring Physics

After import, configure Unity physics:

```csharp
using UnityEngine;

public class RobotPhysicsSetup : MonoBehaviour
{
    void Start()
    {
        // Set up articulation body (Unity's physics for robots)
        ArticulationBody body = GetComponent<ArticulationBody>();

        if (body != null)
        {
            body.immovable = false;
            body.useGravity = true;
            body.mass = 10f;

            // Joint settings
            body.jointFriction = 0.05f;
            body.angularDamping = 0.05f;
            body.linearDamping = 0.05f;
        }
    }
}
```

### Wheel Controller

Create differential drive controller:

```csharp
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Geometry;

public class DifferentialDriveController : MonoBehaviour
{
    public ArticulationBody leftWheel;
    public ArticulationBody rightWheel;

    public float wheelRadius = 0.1f;
    public float wheelSeparation = 0.34f;
    public float maxSpeed = 10f;

    private float leftWheelVel;
    private float rightWheelVel;

    void Start()
    {
        ROSConnection.GetOrCreateInstance().Subscribe<TwistMsg>("cmd_vel", OnCmdVel);
    }

    void OnCmdVel(TwistMsg twist)
    {
        // Convert twist to wheel velocities
        float linearVel = (float)twist.linear.x;
        float angularVel = (float)twist.angular.z;

        leftWheelVel = (linearVel - angularVel * wheelSeparation / 2f) / wheelRadius;
        rightWheelVel = (linearVel + angularVel * wheelSeparation / 2f) / wheelRadius;

        // Clamp to max speed
        leftWheelVel = Mathf.Clamp(leftWheelVel, -maxSpeed, maxSpeed);
        rightWheelVel = Mathf.Clamp(rightWheelVel, -maxSpeed, maxSpeed);
    }

    void FixedUpdate()
    {
        // Apply velocities to wheels
        SetWheelVelocity(leftWheel, leftWheelVel);
        SetWheelVelocity(rightWheel, rightWheelVel);
    }

    void SetWheelVelocity(ArticulationBody wheel, float velocity)
    {
        ArticulationDrive drive = wheel.xDrive;
        drive.target = velocity * Mathf.Rad2Deg * Time.fixedDeltaTime;
        wheel.xDrive = drive;
    }
}
```

## Unity ML-Agents for Robotics

Unity ML-Agents enables reinforcement learning in Unity environments.

### Installation

```bash
# Install ML-Agents Python package
pip install mlagents==0.30.0

# In Unity Package Manager, add:
# com.unity.ml-agents
```

### Creating a Training Environment

Create `RobotAgent.cs`:

```csharp
using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Sensors;
using Unity.MLAgents.Actuators;

public class RobotReachAgent : Agent
{
    public Transform target;
    public Transform robot;

    private Rigidbody robotRb;

    public override void Initialize()
    {
        robotRb = robot.GetComponent<Rigidbody>();
    }

    public override void OnEpisodeBegin()
    {
        // Reset robot position
        robot.localPosition = Vector3.zero;
        robotRb.velocity = Vector3.zero;
        robotRb.angularVelocity = Vector3.zero;

        // Randomize target position
        target.localPosition = new Vector3(
            Random.Range(-5f, 5f),
            0.5f,
            Random.Range(-5f, 5f)
        );
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        // Robot position
        sensor.AddObservation(robot.localPosition);

        // Target position
        sensor.AddObservation(target.localPosition);

        // Robot velocity
        sensor.AddObservation(robotRb.velocity);
    }

    public override void OnActionReceived(ActionBuffers actions)
    {
        // Get actions (linear and angular velocity)
        float linearVel = actions.ContinuousActions[0];
        float angularVel = actions.ContinuousActions[1];

        // Apply actions
        robotRb.AddForce(robot.forward * linearVel * 10f);
        robotRb.AddTorque(robot.up * angularVel * 10f);

        // Calculate reward
        float distanceToTarget = Vector3.Distance(robot.localPosition, target.localPosition);

        // Reward for getting closer
        if (distanceToTarget < 1.5f)
        {
            SetReward(1.0f);
            EndEpisode();
        }

        // Small penalty per step (encourage efficiency)
        AddReward(-0.001f);
    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        // Manual control for testing
        var continuousActions = actionsOut.ContinuousActions;
        continuousActions[0] = Input.GetAxis("Vertical");
        continuousActions[1] = Input.GetAxis("Horizontal");
    }
}
```

### Training Configuration

Create `robot_reach_config.yaml`:

```yaml
behaviors:
  RobotReach:
    trainer_type: ppo
    hyperparameters:
      batch_size: 1024
      buffer_size: 10240
      learning_rate: 3.0e-4
      beta: 5.0e-3
      epsilon: 0.2
      lambd: 0.95
      num_epoch: 3
      learning_rate_schedule: linear
    network_settings:
      normalize: true
      hidden_units: 128
      num_layers: 2
    reward_signals:
      extrinsic:
        gamma: 0.99
        strength: 1.0
    max_steps: 500000
    time_horizon: 64
    summary_freq: 10000
```

### Training

```bash
mlagents-learn robot_reach_config.yaml --run-id=robot_reach_01
```

In Unity, press **Play** to start training.

## Unity Perception SDK

The Perception SDK generates labeled synthetic data for computer vision.

### Setting Up Perception

1. Install Perception package (already added earlier)
2. Add **Perception Camera** to Main Camera
3. Create labeling configurations

### Object Labeling

Add labels to objects:

```csharp
using UnityEngine;
using UnityEngine.Perception.GroundTruth;

public class ObjectLabeler : MonoBehaviour
{
    void Start()
    {
        var labeling = gameObject.AddComponent<Labeling>();
        labeling.labels.Add("robot");
        labeling.labels.Add("obstacle");
    }
}
```

### Bounding Box Detection

Configure Perception Camera for object detection:

```csharp
using UnityEngine;
using UnityEngine.Perception.GroundTruth;

public class PerceptionSetup : MonoBehaviour
{
    void Start()
    {
        var perceptionCamera = GetComponent<PerceptionCamera>();

        // Create label config
        var labelConfig = ScriptableObject.CreateInstance<IdLabelConfig>();
        labelConfig.Init(new List<IdLabelEntry>
        {
            new IdLabelEntry { id = 1, label = "robot" },
            new IdLabelEntry { id = 2, label = "obstacle" },
            new IdLabelEntry { id = 3, label = "target" }
        });

        // Add bounding box labeler
        var boundingBoxLabeler = new BoundingBox2DLabeler(labelConfig);
        perceptionCamera.AddLabeler(boundingBoxLabeler);
    }
}
```

### Semantic Segmentation

```csharp
using UnityEngine.Perception.GroundTruth;

public class SemanticSegmentationSetup : MonoBehaviour
{
    void Start()
    {
        var perceptionCamera = GetComponent<PerceptionCamera>();

        // Create semantic segmentation labeler
        var semanticConfig = ScriptableObject.CreateInstance<SemanticSegmentationLabelConfig>();
        var segmentationLabeler = new SemanticSegmentationLabeler(semanticConfig);

        perceptionCamera.AddLabeler(segmentationLabeler);
    }
}
```

### Data Capture

Captured data is saved in **JSON** format:

```json
{
  "captures": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "annotations": [
        {
          "id": "bounding_box_2d",
          "values": [
            {
              "label_id": 1,
              "label_name": "robot",
              "x": 320,
              "y": 240,
              "width": 150,
              "height": 200
            }
          ]
        }
      ]
    }
  ]
}
```

## Realistic Environment Creation

### Lighting and Materials

Unity provides high-quality rendering:

```csharp
using UnityEngine;

public class RealisticLighting : MonoBehaviour
{
    public Light directionalLight;

    void Start()
    {
        // Configure sun/directional light
        directionalLight.type = LightType.Directional;
        directionalLight.intensity = 1.2f;
        directionalLight.color = new Color(1f, 0.95f, 0.9f);
        directionalLight.shadows = LightShadows.Soft;

        // Global settings
        RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Skybox;
        RenderSettings.ambientIntensity = 1.0f;
    }
}
```

### Procedural Environments

Generate random obstacles:

```csharp
using UnityEngine;

public class ProceduralObstacles : MonoBehaviour
{
    public GameObject obstaclePrefab;
    public int obstacleCount = 20;
    public Vector2 spawnArea = new Vector2(10f, 10f);

    void Start()
    {
        GenerateObstacles();
    }

    void GenerateObstacles()
    {
        for (int i = 0; i < obstacleCount; i++)
        {
            Vector3 position = new Vector3(
                Random.Range(-spawnArea.x, spawnArea.x),
                0.5f,
                Random.Range(-spawnArea.y, spawnArea.y)
            );

            GameObject obstacle = Instantiate(obstaclePrefab, position, Quaternion.identity);

            // Randomize scale
            float scale = Random.Range(0.5f, 2f);
            obstacle.transform.localScale = Vector3.one * scale;
        }
    }
}
```

## Summary

- Unity provides photorealistic simulation with advanced graphics
- ROS-TCP-Connector bridges Unity and ROS 2 ecosystems
- URDF Importer brings robot models into Unity
- ML-Agents enables reinforcement learning in Unity
- Perception SDK generates labeled synthetic data for computer vision
- Unity excels at perception tasks and human-robot interaction scenarios

## Exercises

1. Import a URDF robot model and control it via ROS 2 topics
2. Create an ML-Agents environment where a robot learns to navigate to random goals
3. Set up Perception SDK to generate a dataset of 1000 labeled images
4. Build a procedurally generated warehouse environment with obstacles
5. Implement a semantic segmentation pipeline for robot perception

## Next Chapter

In Chapter 8, we'll dive into NVIDIA Isaac SDK - a powerful framework for AI-powered robotics with GPU-accelerated perception and behavior trees.
