---
id: chapter-10-sim-to-real
title: Sim-to-Real Transfer - Bridging the Gap
module: 3
week: 8
learning_objectives:
  - Understand the reality gap and its causes
  - Apply domain randomization techniques
  - Perform system identification for accurate modeling
  - Use transfer learning strategies for sim-to-real deployment
  - Validate and measure sim-to-real performance
estimated_time_minutes: 90
---

# Sim-to-Real Transfer - Bridging the Gap

## Introduction

The **sim-to-real gap** (or **reality gap**) is one of the most challenging problems in robotics. Policies trained in simulation often fail when deployed on physical robots due to differences in physics, sensors, actuators, and environmental conditions. Sim-to-real transfer addresses this challenge through techniques like domain randomization, accurate modeling, and transfer learning.

**Why Sim-to-Real Matters:**
- Training in simulation is safe, fast, and scalable
- Physical robot testing is expensive, slow, and risky
- Bridging the gap enables rapid development and deployment
- Essential for deploying AI-trained behaviors on real robots

## Understanding the Reality Gap

### Sources of the Reality Gap

The gap between simulation and reality arises from multiple sources:

**1. Physics Discrepancies**
- Simplified collision models
- Approximate friction and damping
- Contact dynamics inaccuracies
- Material property variations

**2. Sensor Noise and Characteristics**
- Camera: motion blur, lens distortion, exposure variation
- LiDAR: reflectivity, beam divergence, multi-path
- IMU: drift, bias, temperature sensitivity
- Encoders: backlash, quantization

**3. Actuator Dynamics**
- Motor response delays
- Gear backlash and compliance
- Voltage fluctuations
- Temperature-dependent performance

**4. Environmental Factors**
- Lighting variations
- Surface textures and materials
- Air resistance
- Temperature and humidity

**5. Latency and Timing**
- Communication delays
- Computational overhead
- Non-deterministic execution

### Measuring the Reality Gap

Quantify sim-to-real transfer with metrics:

```python
import numpy as np

def compute_transfer_gap(sim_performance, real_performance):
    """
    Compute performance degradation from sim to real.

    Args:
        sim_performance: Success rate or metric in simulation (0-1)
        real_performance: Success rate or metric on real robot (0-1)

    Returns:
        Transfer gap (0-1, lower is better)
    """
    gap = (sim_performance - real_performance) / sim_performance
    return max(0, gap)

# Example
sim_success = 0.95  # 95% success in simulation
real_success = 0.72  # 72% success on real robot

gap = compute_transfer_gap(sim_success, real_success)
print(f"Reality gap: {gap:.2%}")  # 24.2%

def compute_behavior_divergence(sim_trajectory, real_trajectory):
    """
    Measure trajectory divergence between sim and real.

    Args:
        sim_trajectory: Nx3 array of simulated positions
        real_trajectory: Mx3 array of real robot positions

    Returns:
        Average position error
    """
    # Align trajectories (assuming same length)
    n = min(len(sim_trajectory), len(real_trajectory))
    sim_traj = sim_trajectory[:n]
    real_traj = real_trajectory[:n]

    # Compute Euclidean distance
    errors = np.linalg.norm(sim_traj - real_traj, axis=1)

    return {
        'mean_error': np.mean(errors),
        'max_error': np.max(errors),
        'std_error': np.std(errors)
    }
```

## Domain Randomization

Domain randomization is the most effective technique for sim-to-real transfer. By training on diverse simulated environments, the policy learns robust features that generalize to reality.

### Visual Domain Randomization

Randomize appearance to handle real-world visual variation:

```python
import numpy as np
import random

class VisualRandomizer:
    """Randomize visual properties for sim-to-real transfer."""

    def __init__(self):
        self.texture_library = self.load_textures()

    def randomize_lighting(self, scene):
        """Randomize lighting conditions."""
        # Ambient light intensity
        ambient = random.uniform(0.3, 1.2)
        scene.set_ambient_intensity(ambient)

        # Directional light
        direction = np.random.uniform(-1, 1, size=3)
        direction = direction / np.linalg.norm(direction)
        intensity = random.uniform(0.5, 2.0)
        color_temp = random.uniform(3000, 8000)  # Kelvin

        scene.set_directional_light(
            direction=direction,
            intensity=intensity,
            temperature=color_temp
        )

        # Additional point lights
        num_lights = random.randint(0, 3)
        for _ in range(num_lights):
            position = np.random.uniform(-5, 5, size=3)
            scene.add_point_light(
                position=position,
                intensity=random.uniform(100, 1000),
                color=np.random.uniform(0.8, 1.0, size=3)
            )

    def randomize_camera(self, camera):
        """Randomize camera parameters."""
        # Exposure
        camera.set_exposure(random.uniform(0.5, 2.0))

        # White balance
        camera.set_white_balance(random.uniform(2500, 9000))

        # Gain/ISO
        camera.set_gain(random.uniform(1.0, 4.0))

        # Slight pose variation
        pos_noise = np.random.normal(0, 0.05, size=3)
        rot_noise = np.random.normal(0, 2.0, size=3)  # degrees

        camera.add_pose_noise(pos_noise, rot_noise)

    def randomize_textures(self, objects):
        """Apply random textures to objects."""
        for obj in objects:
            # Random texture from library
            texture = random.choice(self.texture_library)
            obj.set_texture(texture)

            # Random color tint
            tint = np.random.uniform(0.7, 1.3, size=3)
            obj.set_color_tint(tint)

            # Random material properties
            obj.set_roughness(random.uniform(0.1, 0.9))
            obj.set_metallic(random.uniform(0.0, 0.5))

    def randomize_background(self, scene):
        """Randomize background/skybox."""
        skybox = random.choice([
            'clear_sky', 'cloudy', 'indoor_warehouse',
            'office', 'outdoor_grass', 'sunset'
        ])
        scene.set_skybox(skybox)

    def load_textures(self):
        """Load texture library."""
        return [
            'wood_oak', 'wood_pine', 'metal_brushed',
            'metal_rusty', 'concrete_smooth', 'concrete_rough',
            'plastic_white', 'plastic_black', 'fabric_cotton',
            'tiles_ceramic', 'brick_red', 'stone_granite'
        ]

# Usage in training loop
randomizer = VisualRandomizer()

for episode in range(num_episodes):
    # Reset environment
    env.reset()

    # Apply randomization
    randomizer.randomize_lighting(env.scene)
    randomizer.randomize_camera(env.camera)
    randomizer.randomize_textures(env.get_all_objects())
    randomizer.randomize_background(env.scene)

    # Train policy
    train_episode(env, policy)
```

### Physics Domain Randomization

Randomize physical parameters:

```python
class PhysicsRandomizer:
    """Randomize physics parameters for robust policies."""

    def randomize_robot(self, robot):
        """Randomize robot properties."""
        # Link masses (±20%)
        for link in robot.links:
            nominal_mass = link.get_nominal_mass()
            randomized_mass = nominal_mass * random.uniform(0.8, 1.2)
            link.set_mass(randomized_mass)

        # Friction coefficients
        for link in robot.links:
            friction = random.uniform(0.3, 1.2)
            link.set_friction(friction)

        # Joint damping and friction
        for joint in robot.joints:
            damping = random.uniform(0.01, 0.5)
            friction = random.uniform(0.01, 0.2)
            joint.set_damping(damping)
            joint.set_friction(friction)

        # Actuator noise and delay
        for actuator in robot.actuators:
            # Command noise
            noise_std = random.uniform(0.01, 0.05)
            actuator.set_command_noise(noise_std)

            # Response delay
            delay = random.uniform(0, 0.02)  # 0-20ms
            actuator.set_delay(delay)

            # Torque limits variation
            nominal_torque = actuator.get_nominal_torque()
            max_torque = nominal_torque * random.uniform(0.9, 1.1)
            actuator.set_max_torque(max_torque)

    def randomize_objects(self, objects):
        """Randomize object properties."""
        for obj in objects:
            # Mass (±30%)
            mass = obj.get_mass() * random.uniform(0.7, 1.3)
            obj.set_mass(mass)

            # Size (±10%)
            scale = random.uniform(0.9, 1.1)
            obj.set_scale(scale)

            # Friction
            friction = random.uniform(0.2, 1.5)
            restitution = random.uniform(0.0, 0.8)
            obj.set_friction(friction)
            obj.set_restitution(restitution)

    def randomize_environment(self, env):
        """Randomize environmental conditions."""
        # Gravity (Earth ±5%)
        gravity = -9.81 * random.uniform(0.95, 1.05)
        env.set_gravity(gravity)

        # Air density (affects drag)
        air_density = random.uniform(1.0, 1.3)  # kg/m^3
        env.set_air_density(air_density)

        # Ground friction
        ground_friction = random.uniform(0.5, 1.5)
        env.ground.set_friction(ground_friction)

# Usage
physics_rand = PhysicsRandomizer()

for episode in range(num_episodes):
    env.reset()

    physics_rand.randomize_robot(env.robot)
    physics_rand.randomize_objects(env.objects)
    physics_rand.randomize_environment(env)

    train_episode(env, policy)
```

### Sensor Domain Randomization

Add realistic noise to sensors:

```python
class SensorRandomizer:
    """Add realistic sensor noise for sim-to-real."""

    def add_camera_noise(self, image):
        """Add camera sensor noise."""
        # Gaussian noise
        noise = np.random.normal(0, random.uniform(0, 10), image.shape)
        noisy_image = np.clip(image + noise, 0, 255).astype(np.uint8)

        # Motion blur (random direction)
        if random.random() < 0.3:
            kernel_size = random.randint(3, 9)
            angle = random.uniform(0, 360)
            noisy_image = self.apply_motion_blur(noisy_image, kernel_size, angle)

        # Auto-exposure variation
        exposure_factor = random.uniform(0.7, 1.3)
        noisy_image = np.clip(noisy_image * exposure_factor, 0, 255).astype(np.uint8)

        return noisy_image

    def add_lidar_noise(self, ranges, intensities):
        """Add LiDAR sensor noise."""
        # Range noise (Gaussian)
        range_noise = np.random.normal(0, 0.02, ranges.shape)
        noisy_ranges = ranges + range_noise

        # Dropout (missed returns)
        dropout_prob = random.uniform(0.01, 0.05)
        dropout_mask = np.random.random(ranges.shape) > dropout_prob
        noisy_ranges = np.where(dropout_mask, noisy_ranges, np.inf)

        # Intensity noise
        intensity_noise = np.random.normal(0, 0.1, intensities.shape)
        noisy_intensities = np.clip(intensities + intensity_noise, 0, 1)

        return noisy_ranges, noisy_intensities

    def add_imu_noise(self, accel, gyro):
        """Add IMU sensor noise."""
        # Accelerometer noise and bias
        accel_noise = np.random.normal(0, 0.05, accel.shape)
        accel_bias = np.random.normal(0, 0.02, 3)
        noisy_accel = accel + accel_noise + accel_bias

        # Gyroscope noise and drift
        gyro_noise = np.random.normal(0, 0.01, gyro.shape)
        gyro_drift = np.random.normal(0, 0.005, 3)
        noisy_gyro = gyro + gyro_noise + gyro_drift

        return noisy_accel, noisy_gyro

    def add_encoder_noise(self, positions):
        """Add encoder quantization and noise."""
        # Quantization (e.g., 0.01 rad resolution)
        resolution = random.uniform(0.005, 0.02)
        quantized = np.round(positions / resolution) * resolution

        # Small measurement noise
        noise = np.random.normal(0, 0.001, positions.shape)

        return quantized + noise
```

## System Identification

Accurate modeling of the real robot improves sim-to-real transfer.

### Identifying Physical Parameters

```python
import numpy as np
from scipy.optimize import minimize

class SystemIdentification:
    """Identify real robot parameters from data."""

    def identify_friction(self, joint_velocities, joint_torques):
        """
        Identify friction parameters using least squares.

        Model: τ_friction = b*v + c*sign(v)
        where b = viscous friction, c = Coulomb friction
        """
        # Build data matrix
        n = len(joint_velocities)
        A = np.zeros((n, 2))
        A[:, 0] = joint_velocities
        A[:, 1] = np.sign(joint_velocities)

        # Solve least squares
        params, residuals, rank, s = np.linalg.lstsq(A, joint_torques, rcond=None)

        viscous_friction = params[0]
        coulomb_friction = params[1]

        return {
            'viscous_friction': viscous_friction,
            'coulomb_friction': coulomb_friction,
            'residual_error': np.sqrt(residuals[0] / n) if residuals.size > 0 else 0
        }

    def identify_inertia(self, accelerations, torques, velocities):
        """
        Identify link inertia using dynamic measurements.

        Model: τ = I*α + b*v + g(q)
        """
        # Remove gravity and friction effects (simplified)
        # In practice, need full dynamics model

        n = len(accelerations)
        # Least squares: I = (τ - b*v) / α

        inertias = []
        for i in range(n):
            if abs(accelerations[i]) > 0.01:  # Avoid division by small numbers
                I = (torques[i] - self.viscous_friction * velocities[i]) / accelerations[i]
                inertias.append(I)

        return np.mean(inertias)

    def calibrate_camera(self, checkerboard_images):
        """
        Calibrate camera intrinsics and distortion.

        Uses OpenCV camera calibration.
        """
        import cv2

        # Checkerboard dimensions
        pattern_size = (9, 6)

        obj_points = []  # 3D points
        img_points = []  # 2D points

        # Prepare object points
        objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)

        for img in checkerboard_images:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, pattern_size, None)

            if ret:
                obj_points.append(objp)
                img_points.append(corners)

        # Calibrate camera
        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            obj_points, img_points, gray.shape[::-1], None, None
        )

        return {
            'camera_matrix': camera_matrix,
            'distortion_coeffs': dist_coeffs,
            'reprojection_error': ret
        }

    def fit_actuator_model(self, commanded_torques, measured_torques):
        """
        Fit actuator response model.

        Model: τ_actual = k*τ_cmd + delay
        """
        def model_error(params):
            k, delay_steps = params
            delay_steps = int(delay_steps)

            # Shift commanded torques by delay
            if delay_steps > 0:
                cmd_delayed = np.roll(commanded_torques, delay_steps)
                cmd_delayed[:delay_steps] = 0
            else:
                cmd_delayed = commanded_torques

            predicted = k * cmd_delayed
            error = np.sum((predicted - measured_torques) ** 2)
            return error

        # Optimize
        result = minimize(
            model_error,
            x0=[1.0, 0],
            bounds=[(0.5, 1.5), (0, 10)],
            method='L-BFGS-B'
        )

        gain = result.x[0]
        delay = int(result.x[1])

        return {'gain': gain, 'delay_steps': delay}

# Example usage
sysid = SystemIdentification()

# Collect data from real robot
joint_vels = np.array([...])  # measured velocities
joint_torques = np.array([...])  # measured torques

# Identify friction
friction_params = sysid.identify_friction(joint_vels, joint_torques)
print(f"Viscous friction: {friction_params['viscous_friction']:.4f}")
print(f"Coulomb friction: {friction_params['coulomb_friction']:.4f}")

# Update simulation with identified parameters
sim.robot.set_joint_friction(
    viscous=friction_params['viscous_friction'],
    coulomb=friction_params['coulomb_friction']
)
```

## Transfer Learning Strategies

### Fine-Tuning on Real Robot

Start with sim-trained policy, then fine-tune on real hardware:

```python
import torch
import torch.optim as optim

class SimToRealFineTuner:
    """Fine-tune sim-trained policy on real robot."""

    def __init__(self, sim_policy, learning_rate=1e-5):
        self.policy = sim_policy
        self.optimizer = optim.Adam(self.policy.parameters(), lr=learning_rate)

        # Lower learning rate for fine-tuning
        self.initial_lr = learning_rate

    def finetune(self, real_robot, num_episodes=50):
        """
        Fine-tune policy on real robot data.

        Uses conservative updates to avoid catastrophic forgetting.
        """
        print("Starting fine-tuning on real robot...")

        for episode in range(num_episodes):
            # Collect trajectory from real robot
            states, actions, rewards = self.collect_real_trajectory(real_robot)

            # Compute loss
            loss = self.compute_policy_loss(states, actions, rewards)

            # Update policy (small steps)
            self.optimizer.zero_grad()
            loss.backward()

            # Clip gradients for stability
            torch.nn.utils.clip_grad_norm_(self.policy.parameters(), max_norm=0.5)

            self.optimizer.step()

            # Evaluate
            if episode % 10 == 0:
                success_rate = self.evaluate_on_real(real_robot, num_trials=5)
                print(f"Episode {episode}: Loss={loss.item():.4f}, "
                      f"Success Rate={success_rate:.2%}")

        print("Fine-tuning complete!")

    def collect_real_trajectory(self, real_robot):
        """Collect one trajectory from real robot."""
        states = []
        actions = []
        rewards = []

        state = real_robot.reset()
        done = False

        while not done:
            # Get action from policy
            action = self.policy(torch.FloatTensor(state)).detach().numpy()

            # Execute on real robot (with safety checks)
            next_state, reward, done = real_robot.step(action)

            states.append(state)
            actions.append(action)
            rewards.append(reward)

            state = next_state

        return states, actions, rewards

    def compute_policy_loss(self, states, actions, rewards):
        """Compute policy loss for fine-tuning."""
        # Convert to tensors
        states_t = torch.FloatTensor(states)
        actions_t = torch.FloatTensor(actions)
        rewards_t = torch.FloatTensor(rewards)

        # Compute advantages (simplified)
        returns = self.compute_returns(rewards_t)

        # Policy loss (e.g., policy gradient)
        action_preds = self.policy(states_t)
        loss = -torch.mean((action_preds - actions_t) ** 2 * returns)

        return loss

    def compute_returns(self, rewards, gamma=0.99):
        """Compute discounted returns."""
        returns = []
        G = 0
        for r in reversed(rewards):
            G = r + gamma * G
            returns.insert(0, G)
        return torch.FloatTensor(returns)

    def evaluate_on_real(self, real_robot, num_trials=10):
        """Evaluate policy success rate on real robot."""
        successes = 0

        for trial in range(num_trials):
            state = real_robot.reset()
            done = False

            while not done:
                action = self.policy(torch.FloatTensor(state)).detach().numpy()
                state, reward, done = real_robot.step(action)

            if real_robot.task_successful():
                successes += 1

        return successes / num_trials

# Usage
sim_policy = load_pretrained_policy('sim_policy.pth')
finetuner = SimToRealFineTuner(sim_policy, learning_rate=1e-5)

# Connect to real robot
real_robot = RealRobotInterface()

# Fine-tune with limited real-world data
finetuner.finetune(real_robot, num_episodes=50)

# Save fine-tuned policy
torch.save(sim_policy.state_dict(), 'real_policy.pth')
```

### Progressive Transfer

Gradually transition from sim to real:

```python
class ProgressiveTransfer:
    """Gradually increase real-world data proportion."""

    def __init__(self, sim_env, real_robot, policy):
        self.sim_env = sim_env
        self.real_robot = real_robot
        self.policy = policy

    def progressive_training(self, total_steps=100000):
        """Train with increasing proportion of real data."""
        steps = 0

        while steps < total_steps:
            # Compute real data ratio (0 to 1)
            real_ratio = min(steps / total_steps, 0.3)  # Max 30% real

            # Sample from sim or real
            if np.random.random() < real_ratio:
                # Use real robot
                trajectory = self.collect_trajectory(self.real_robot)
            else:
                # Use simulation
                trajectory = self.collect_trajectory(self.sim_env)

            # Update policy
            self.update_policy(trajectory)

            steps += len(trajectory)

            if steps % 10000 == 0:
                print(f"Steps: {steps}, Real ratio: {real_ratio:.2%}")
```

## Validation and Testing

### Sim-to-Real Validation Protocol

```python
class SimToRealValidator:
    """Validate sim-to-real transfer quality."""

    def run_validation(self, policy, sim_env, real_robot, num_tasks=20):
        """
        Compare policy performance in sim vs real.
        """
        print("Running sim-to-real validation...")

        # Evaluate in simulation
        sim_results = []
        for task in range(num_tasks):
            sim_env.reset_task(task)
            success, metrics = self.evaluate_policy(policy, sim_env)
            sim_results.append({'success': success, 'metrics': metrics})

        # Evaluate on real robot
        real_results = []
        for task in range(num_tasks):
            real_robot.reset_task(task)
            success, metrics = self.evaluate_policy(policy, real_robot)
            real_results.append({'success': success, 'metrics': metrics})

        # Compute statistics
        report = self.generate_report(sim_results, real_results)

        return report

    def evaluate_policy(self, policy, env):
        """Evaluate policy on one task."""
        state = env.get_state()
        done = False
        metrics = {'steps': 0, 'reward': 0}

        while not done and metrics['steps'] < 100:
            action = policy(state)
            state, reward, done = env.step(action)
            metrics['steps'] += 1
            metrics['reward'] += reward

        success = env.check_success()
        return success, metrics

    def generate_report(self, sim_results, real_results):
        """Generate validation report."""
        sim_success = np.mean([r['success'] for r in sim_results])
        real_success = np.mean([r['success'] for r in real_results])

        gap = compute_transfer_gap(sim_success, real_success)

        report = {
            'sim_success_rate': sim_success,
            'real_success_rate': real_success,
            'transfer_gap': gap,
            'sim_avg_steps': np.mean([r['metrics']['steps'] for r in sim_results]),
            'real_avg_steps': np.mean([r['metrics']['steps'] for r in real_results])
        }

        print("\n=== Sim-to-Real Validation Report ===")
        print(f"Simulation Success Rate: {sim_success:.2%}")
        print(f"Real Robot Success Rate: {real_success:.2%}")
        print(f"Transfer Gap: {gap:.2%}")
        print(f"Sim Avg Steps: {report['sim_avg_steps']:.1f}")
        print(f"Real Avg Steps: {report['real_avg_steps']:.1f}")

        return report

# Usage
validator = SimToRealValidator()
report = validator.run_validation(policy, sim_env, real_robot, num_tasks=20)
```

## Best Practices

### Checklist for Sim-to-Real Success

1. **Use domain randomization extensively**
   - Visual: lighting, textures, camera parameters
   - Physics: masses, friction, dynamics
   - Sensors: noise, dropout, calibration errors

2. **Accurate system identification**
   - Measure real robot parameters
   - Update simulation to match reality
   - Validate dynamics match

3. **Conservative policy design**
   - Add safety margins
   - Smooth actions (low-pass filter)
   - Graceful failure modes

4. **Gradual deployment**
   - Test in constrained real environments first
   - Progressively increase task difficulty
   - Monitor for failure modes

5. **Continuous validation**
   - Regular sim-vs-real comparisons
   - Update sim based on real-world observations
   - Retrain as needed

## Summary

- The sim-to-real gap arises from physics, sensor, and environmental differences
- Domain randomization creates robust policies that generalize
- System identification improves simulation accuracy
- Transfer learning leverages both sim and real data efficiently
- Validation protocols quantify transfer quality
- Successful deployment requires iterative refinement

## Exercises

1. Implement visual domain randomization for a pick-and-place task
2. Perform system identification to measure friction on a real robot joint
3. Train a policy with domain randomization and test sim-to-real transfer
4. Create a validation protocol comparing sim and real success rates
5. Fine-tune a sim-trained policy using 20 real robot episodes

## Next Chapter

In Chapter 11, we'll explore humanoid robot development - tackling the challenges of whole-body control, balance, locomotion, and manipulation for human-like robots.
