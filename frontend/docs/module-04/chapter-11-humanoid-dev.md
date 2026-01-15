---
id: chapter-11-humanoid-dev
title: Humanoid Robot Development
module: 4
week: 9
learning_objectives:
  - Understand humanoid robot kinematics and dynamics
  - Implement whole-body control for multi-limb coordination
  - Design balance and stability controllers
  - Develop locomotion controllers for bipedal walking
  - Integrate manipulation capabilities with arms and hands
estimated_time_minutes: 120
---

# Humanoid Robot Development

## Introduction

Humanoid robots are the pinnacle of robotic engineering - machines designed to replicate human form and function. Companies like Tesla (Optimus), Figure AI (Figure 01), Boston Dynamics (Atlas), and others are pushing the boundaries of what humanoid robots can achieve. Developing humanoid robots requires solving complex problems in kinematics, dynamics, balance, locomotion, and manipulation.

**Why Humanoids?**
- Designed for human environments (stairs, doors, furniture)
- Intuitive for human-robot interaction
- Versatile: locomotion + manipulation
- Commercial applications: warehouses, elderly care, dangerous environments

## Humanoid Robot Anatomy

### Typical Humanoid Configuration

```
            [Head] - Cameras, sensors
               |
         [Torso/Chest]
               |
     +---------+---------+
     |                   |
  [Left Arm]        [Right Arm]
  - Shoulder (3 DOF)
  - Elbow (1-2 DOF)
  - Wrist (2-3 DOF)
  - Hand/Gripper
     |                   |
  [Pelvis/Hip]
     |
     +---------+---------+
     |                   |
  [Left Leg]        [Right Leg]
  - Hip (3 DOF)
  - Knee (1 DOF)
  - Ankle (2 DOF)
  - Foot
```

### Degrees of Freedom (DOF)

**Tesla Optimus Gen 2:**
- Total: ~40 DOF
- Arms: 6 DOF each (shoulder: 3, elbow: 1, wrist: 2)
- Hands: 11 DOF each (articulated fingers)
- Legs: 6 DOF each (hip: 3, knee: 1, ankle: 2)
- Torso: 2-3 DOF

**Figure 01:**
- Total: ~38 DOF
- Similar configuration with emphasis on dexterous manipulation

## Kinematics and Dynamics

### Forward Kinematics

Calculate end-effector pose from joint angles:

```python
import numpy as np

class HumanoidKinematics:
    """Compute forward and inverse kinematics for humanoid robot."""

    def __init__(self):
        # DH parameters for 6-DOF arm (example)
        # [theta, d, a, alpha]
        self.dh_params = np.array([
            [0, 0.1,  0,     np.pi/2],  # Shoulder pitch
            [0, 0,    0,     np.pi/2],  # Shoulder roll
            [0, 0,    0.3,   0],        # Shoulder yaw
            [0, 0,    0,     np.pi/2],  # Elbow
            [0, 0,    0.25,  0],        # Wrist pitch
            [0, 0.1,  0,     0],        # Wrist roll
        ])

    def dh_matrix(self, theta, d, a, alpha):
        """Compute DH transformation matrix."""
        ct = np.cos(theta)
        st = np.sin(theta)
        ca = np.cos(alpha)
        sa = np.sin(alpha)

        return np.array([
            [ct, -st*ca,  st*sa, a*ct],
            [st,  ct*ca, -ct*sa, a*st],
            [0,   sa,     ca,    d],
            [0,   0,      0,     1]
        ])

    def forward_kinematics(self, joint_angles):
        """
        Compute end-effector pose from joint angles.

        Args:
            joint_angles: Array of 6 joint angles (radians)

        Returns:
            4x4 homogeneous transformation matrix
        """
        T = np.eye(4)

        for i, theta in enumerate(joint_angles):
            theta_i, d, a, alpha = self.dh_params[i]
            theta_total = theta_i + theta

            T_i = self.dh_matrix(theta_total, d, a, alpha)
            T = T @ T_i

        return T

    def get_position_and_orientation(self, T):
        """Extract position and orientation from transformation matrix."""
        position = T[:3, 3]

        # Convert rotation matrix to quaternion
        rotation_matrix = T[:3, :3]
        quat = self.rotation_matrix_to_quaternion(rotation_matrix)

        return position, quat

    def rotation_matrix_to_quaternion(self, R):
        """Convert rotation matrix to quaternion [w, x, y, z]."""
        trace = np.trace(R)

        if trace > 0:
            s = 0.5 / np.sqrt(trace + 1.0)
            w = 0.25 / s
            x = (R[2, 1] - R[1, 2]) * s
            y = (R[0, 2] - R[2, 0]) * s
            z = (R[1, 0] - R[0, 1]) * s
        else:
            if R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
                s = 2.0 * np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2])
                w = (R[2, 1] - R[1, 2]) / s
                x = 0.25 * s
                y = (R[0, 1] + R[1, 0]) / s
                z = (R[0, 2] + R[2, 0]) / s
            elif R[1, 1] > R[2, 2]:
                s = 2.0 * np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2])
                w = (R[0, 2] - R[2, 0]) / s
                x = (R[0, 1] + R[1, 0]) / s
                y = 0.25 * s
                z = (R[1, 2] + R[2, 1]) / s
            else:
                s = 2.0 * np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1])
                w = (R[1, 0] - R[0, 1]) / s
                x = (R[0, 2] + R[2, 0]) / s
                y = (R[1, 2] + R[2, 1]) / s
                z = 0.25 * s

        return np.array([w, x, y, z])

# Example usage
kin = HumanoidKinematics()

# Joint angles (radians)
joint_angles = np.array([0.5, 0.3, 0.2, 1.0, 0.4, 0.1])

# Compute forward kinematics
T = kin.forward_kinematics(joint_angles)
position, orientation = kin.get_position_and_orientation(T)

print(f"End-effector position: {position}")
print(f"End-effector orientation (quat): {orientation}")
```

### Inverse Kinematics

Compute joint angles to reach desired pose:

```python
from scipy.optimize import minimize

class InverseKinematics:
    """Solve inverse kinematics for humanoid arm."""

    def __init__(self, kinematics):
        self.kin = kinematics

    def solve_ik(self, target_position, target_orientation=None, initial_guess=None):
        """
        Solve IK using numerical optimization.

        Args:
            target_position: Desired 3D position
            target_orientation: Desired quaternion (optional)
            initial_guess: Initial joint angles

        Returns:
            Joint angles that achieve target pose
        """
        if initial_guess is None:
            initial_guess = np.zeros(6)

        def objective(joint_angles):
            # Compute current pose
            T = self.kin.forward_kinematics(joint_angles)
            current_pos, current_orient = self.kin.get_position_and_orientation(T)

            # Position error
            pos_error = np.linalg.norm(current_pos - target_position)

            # Orientation error (if specified)
            if target_orientation is not None:
                orient_error = self.quaternion_distance(current_orient, target_orientation)
            else:
                orient_error = 0

            # Total error
            return pos_error + 0.5 * orient_error

        # Joint limits
        bounds = [
            (-np.pi, np.pi),  # Shoulder pitch
            (-np.pi/2, np.pi/2),  # Shoulder roll
            (-np.pi, np.pi),  # Shoulder yaw
            (0, np.pi),  # Elbow
            (-np.pi/2, np.pi/2),  # Wrist pitch
            (-np.pi, np.pi),  # Wrist roll
        ]

        # Optimize
        result = minimize(
            objective,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            options={'maxiter': 1000}
        )

        if result.success:
            return result.x
        else:
            print(f"IK failed: {result.message}")
            return None

    def quaternion_distance(self, q1, q2):
        """Compute distance between two quaternions."""
        dot = np.abs(np.dot(q1, q2))
        dot = np.clip(dot, -1.0, 1.0)
        return 1 - dot

# Example
ik = InverseKinematics(kin)

# Target position
target_pos = np.array([0.4, 0.2, 0.3])

# Solve IK
joint_solution = ik.solve_ik(target_pos)

if joint_solution is not None:
    print(f"IK solution: {joint_solution}")

    # Verify
    T_verify = kin.forward_kinematics(joint_solution)
    pos_verify, _ = kin.get_position_and_orientation(T_verify)
    error = np.linalg.norm(pos_verify - target_pos)
    print(f"Position error: {error:.6f} m")
```

## Whole-Body Control

Coordinate all limbs simultaneously for complex tasks.

### Quadratic Programming (QP) Controller

```python
import numpy as np
from qpsolvers import solve_qp

class WholeBodyController:
    """
    Whole-body controller using QP optimization.

    Formulation:
        minimize:   (1/2) * x^T * H * x + f^T * x
        subject to: A * x <= b  (inequality constraints)
                    C * x = d   (equality constraints)
    """

    def __init__(self, num_joints=20):
        self.num_joints = num_joints

    def compute_joint_accelerations(self, q, qd, tasks, constraints):
        """
        Compute joint accelerations for multiple tasks.

        Args:
            q: Joint positions
            qd: Joint velocities
            tasks: List of tasks (e.g., foot contact, hand reaching)
            constraints: Physical constraints (torque limits, etc.)

        Returns:
            Joint accelerations
        """
        n = self.num_joints

        # Build QP problem
        H = np.eye(n)  # Minimize accelerations (regularization)
        f = np.zeros(n)

        # Equality constraints (task Jacobians)
        C_eq = []
        d_eq = []

        for task in tasks:
            if task['type'] == 'position':
                J = task['jacobian']  # Task Jacobian
                x_des = task['desired_acceleration']

                # Task constraint: J * qdd = x_des
                C_eq.append(J)
                d_eq.append(x_des)

        if C_eq:
            C = np.vstack(C_eq)
            d = np.hstack(d_eq)
        else:
            C = None
            d = None

        # Inequality constraints (joint limits, torque limits)
        A = []
        b = []

        # Joint acceleration limits
        qdd_max = constraints.get('qdd_max', 10.0)
        A.append(np.eye(n))
        A.append(-np.eye(n))
        b.append(qdd_max * np.ones(n))
        b.append(qdd_max * np.ones(n))

        A = np.vstack(A)
        b = np.hstack(b)

        # Solve QP
        qdd = solve_qp(H, f, A, b, C, d, solver='quadprog')

        return qdd

    def compute_torques(self, q, qd, qdd, M, C, G):
        """
        Compute joint torques using inverse dynamics.

        tau = M(q) * qdd + C(q, qd) * qd + G(q)

        Args:
            q: Joint positions
            qd: Joint velocities
            qdd: Joint accelerations (from QP)
            M: Mass matrix
            C: Coriolis matrix
            G: Gravity vector

        Returns:
            Joint torques
        """
        tau = M @ qdd + C @ qd + G
        return tau

# Example usage
controller = WholeBodyController(num_joints=20)

# Define tasks
tasks = [
    {
        'type': 'position',
        'jacobian': np.random.randn(3, 20),  # Hand position Jacobian
        'desired_acceleration': np.array([0.1, 0, -0.05])  # Move hand
    },
    {
        'type': 'position',
        'jacobian': np.random.randn(6, 20),  # Foot contact Jacobian
        'desired_acceleration': np.zeros(6)  # Keep foot stationary
    }
]

# Constraints
constraints = {
    'qdd_max': 5.0  # Max joint acceleration (rad/s^2)
}

# Current state
q = np.zeros(20)
qd = np.zeros(20)

# Compute accelerations
qdd = controller.compute_joint_accelerations(q, qd, tasks, constraints)

print(f"Computed joint accelerations: {qdd}")
```

## Balance and Stability

### Zero Moment Point (ZMP)

ZMP is a key concept for bipedal balance:

```python
class BalanceController:
    """Maintain balance using ZMP control."""

    def __init__(self, foot_length=0.2, foot_width=0.1):
        self.foot_length = foot_length
        self.foot_width = foot_width

    def compute_zmp(self, com_pos, com_acc, height):
        """
        Compute Zero Moment Point.

        ZMP equation:
        x_zmp = x_com - (z_com / (g + z_acc)) * x_acc

        Args:
            com_pos: Center of mass position [x, y, z]
            com_acc: Center of mass acceleration [x, y, z]
            height: COM height above ground

        Returns:
            ZMP position [x, y]
        """
        g = 9.81  # Gravity

        x_zmp = com_pos[0] - (height / (g + com_acc[2])) * com_acc[0]
        y_zmp = com_pos[1] - (height / (g + com_acc[2])) * com_acc[1]

        return np.array([x_zmp, y_zmp])

    def is_stable(self, zmp, support_foot_pos):
        """
        Check if ZMP is within support polygon.

        Args:
            zmp: ZMP position [x, y]
            support_foot_pos: Support foot position [x, y]

        Returns:
            True if stable, False otherwise
        """
        # Support polygon (rectangular foot)
        x_min = support_foot_pos[0] - self.foot_length / 2
        x_max = support_foot_pos[0] + self.foot_length / 2
        y_min = support_foot_pos[1] - self.foot_width / 2
        y_max = support_foot_pos[1] + self.foot_width / 2

        # Check if ZMP inside polygon
        stable = (x_min <= zmp[0] <= x_max) and (y_min <= zmp[1] <= y_max)

        return stable

    def compute_stabilizing_torque(self, zmp, zmp_desired, kp=1000, kd=100):
        """
        Compute ankle torque to move ZMP toward desired position.

        Args:
            zmp: Current ZMP
            zmp_desired: Desired ZMP
            kp, kd: PD gains

        Returns:
            Ankle torque [pitch, roll]
        """
        zmp_error = zmp_desired - zmp

        # PD control (simplified, no derivative term here)
        torque_pitch = kp * zmp_error[0]  # Forward/backward
        torque_roll = kp * zmp_error[1]   # Left/right

        return np.array([torque_pitch, torque_roll])

# Example
balance_ctrl = BalanceController()

# Current state
com_pos = np.array([0.05, 0.01, 0.8])  # COM slightly forward
com_acc = np.array([0.2, 0.0, 0.1])
height = 0.8

# Compute ZMP
zmp = balance_ctrl.compute_zmp(com_pos, com_acc, height)
print(f"ZMP: {zmp}")

# Check stability
support_foot = np.array([0.0, 0.0])
stable = balance_ctrl.is_stable(zmp, support_foot)
print(f"Stable: {stable}")

# Compute stabilizing torque
zmp_desired = np.array([0.0, 0.0])  # Center of foot
torque = balance_ctrl.compute_stabilizing_torque(zmp, zmp_desired)
print(f"Ankle torque: {torque}")
```

## Locomotion - Walking Gait

### Walking Pattern Generator

```python
import numpy as np
import matplotlib.pyplot as plt

class WalkingGaitGenerator:
    """Generate walking trajectories for humanoid robot."""

    def __init__(self, step_length=0.15, step_height=0.05, step_duration=0.6):
        self.step_length = step_length
        self.step_height = step_height
        self.step_duration = step_duration

    def generate_foot_trajectory(self, t, is_swing_phase):
        """
        Generate foot trajectory for one step.

        Args:
            t: Time within step (0 to step_duration)
            is_swing_phase: True if swing phase, False if stance

        Returns:
            Foot position [x, y, z]
        """
        if not is_swing_phase:
            # Stance phase: foot on ground
            x = 0
            y = 0
            z = 0
        else:
            # Swing phase: foot lifted and moved forward
            # Normalized time (0 to 1)
            s = t / self.step_duration

            # Forward motion (linear)
            x = s * self.step_length

            # Vertical motion (parabolic)
            z = 4 * self.step_height * s * (1 - s)

            # No lateral motion
            y = 0

        return np.array([x, y, z])

    def generate_com_trajectory(self, t, num_steps):
        """
        Generate center of mass trajectory.

        Simple model: COM shifts side-to-side for balance.
        """
        # COM height (constant)
        z_com = 0.8

        # Forward velocity
        x_com = (t / self.step_duration) * self.step_length

        # Lateral shift (sinusoidal)
        y_com = 0.05 * np.sin(2 * np.pi * t / self.step_duration)

        return np.array([x_com, y_com, z_com])

    def plan_walking(self, num_steps=4, dt=0.01):
        """
        Plan complete walking motion.

        Returns:
            Dictionary with trajectories for left foot, right foot, COM
        """
        total_time = num_steps * self.step_duration
        time = np.arange(0, total_time, dt)

        left_foot_traj = []
        right_foot_traj = []
        com_traj = []

        for t in time:
            # Determine which step we're in
            step_idx = int(t / self.step_duration)
            t_in_step = t % self.step_duration

            # Alternate swing leg
            left_is_swing = (step_idx % 2 == 0)
            right_is_swing = not left_is_swing

            # Generate trajectories
            left_foot = self.generate_foot_trajectory(t_in_step, left_is_swing)
            right_foot = self.generate_foot_trajectory(t_in_step, right_is_swing)
            com = self.generate_com_trajectory(t, num_steps)

            # Offset right foot laterally
            right_foot[1] -= 0.15
            left_foot[1] += 0.15

            # Accumulate step progress
            if step_idx > 0:
                offset = step_idx * self.step_length
                if not left_is_swing:
                    left_foot[0] += offset
                if not right_is_swing:
                    right_foot[0] += offset

            left_foot_traj.append(left_foot)
            right_foot_traj.append(right_foot)
            com_traj.append(com)

        return {
            'time': time,
            'left_foot': np.array(left_foot_traj),
            'right_foot': np.array(right_foot_traj),
            'com': np.array(com_traj)
        }

# Generate walking motion
gait_gen = WalkingGaitGenerator(step_length=0.2, step_height=0.05, step_duration=0.6)
trajectories = gait_gen.plan_walking(num_steps=4)

# Visualize
fig, axes = plt.subplots(3, 1, figsize=(10, 8))

# X position
axes[0].plot(trajectories['time'], trajectories['left_foot'][:, 0], label='Left Foot X')
axes[0].plot(trajectories['time'], trajectories['right_foot'][:, 0], label='Right Foot X')
axes[0].plot(trajectories['time'], trajectories['com'][:, 0], label='COM X', linestyle='--')
axes[0].set_ylabel('X Position (m)')
axes[0].legend()
axes[0].grid(True)

# Y position
axes[1].plot(trajectories['time'], trajectories['left_foot'][:, 1], label='Left Foot Y')
axes[1].plot(trajectories['time'], trajectories['right_foot'][:, 1], label='Right Foot Y')
axes[1].plot(trajectories['time'], trajectories['com'][:, 1], label='COM Y', linestyle='--')
axes[1].set_ylabel('Y Position (m)')
axes[1].legend()
axes[1].grid(True)

# Z position (height)
axes[2].plot(trajectories['time'], trajectories['left_foot'][:, 2], label='Left Foot Z')
axes[2].plot(trajectories['time'], trajectories['right_foot'][:, 2], label='Right Foot Z')
axes[2].plot(trajectories['time'], trajectories['com'][:, 2], label='COM Z', linestyle='--')
axes[2].set_ylabel('Z Position (m)')
axes[2].set_xlabel('Time (s)')
axes[2].legend()
axes[2].grid(True)

plt.tight_layout()
# plt.savefig('walking_gait.png')
print("Walking gait planned successfully!")
```

## Manipulation with Arms

### Dual-Arm Coordination

```python
class DualArmController:
    """Coordinate both arms for bimanual manipulation."""

    def __init__(self, left_arm_ik, right_arm_ik):
        self.left_ik = left_arm_ik
        self.right_ik = right_arm_ik

    def pick_and_place_bimanual(self, object_pos, object_size, goal_pos):
        """
        Plan bimanual pick and place.

        Args:
            object_pos: Object position
            object_size: Object dimensions [width, depth, height]
            goal_pos: Goal position

        Returns:
            Trajectory for both arms
        """
        # Grasp points (left and right sides of object)
        left_grasp = object_pos + np.array([-object_size[0]/2, 0, 0])
        right_grasp = object_pos + np.array([object_size[0]/2, 0, 0])

        # Approach from above
        left_approach = left_grasp + np.array([0, 0, 0.1])
        right_approach = right_grasp + np.array([0, 0, 0.1])

        # IK for approach
        left_joints_approach = self.left_ik.solve_ik(left_approach)
        right_joints_approach = self.right_ik.solve_ik(right_approach)

        # IK for grasp
        left_joints_grasp = self.left_ik.solve_ik(left_grasp)
        right_joints_grasp = self.right_ik.solve_ik(right_grasp)

        # IK for lift
        left_lift = left_grasp + np.array([0, 0, 0.2])
        right_lift = right_grasp + np.array([0, 0, 0.2])
        left_joints_lift = self.left_ik.solve_ik(left_lift)
        right_joints_lift = self.right_ik.solve_ik(right_lift)

        # IK for place
        goal_offset = goal_pos - object_pos
        left_place = left_lift + goal_offset
        right_place = right_lift + goal_offset
        left_joints_place = self.left_ik.solve_ik(left_place)
        right_joints_place = self.right_ik.solve_ik(right_place)

        trajectory = {
            'phases': [
                {'name': 'approach', 'left': left_joints_approach, 'right': right_joints_approach},
                {'name': 'grasp', 'left': left_joints_grasp, 'right': right_joints_grasp},
                {'name': 'lift', 'left': left_joints_lift, 'right': right_joints_lift},
                {'name': 'place', 'left': left_joints_place, 'right': right_joints_place},
            ]
        }

        return trajectory

    def collaborative_task(self, task_type):
        """
        Coordinate arms for collaborative tasks.

        Examples: opening a bottle, folding clothes, assembling parts.
        """
        if task_type == 'open_bottle':
            # Left hand holds bottle, right hand twists cap
            left_hold_pos = np.array([0.3, 0.2, 0.5])
            right_twist_pos = np.array([0.3, 0.2, 0.6])

            # Generate coordinated motion
            pass  # Implementation specific to task

# Example
# dual_arm = DualArmController(left_ik, right_ik)
# trajectory = dual_arm.pick_and_place_bimanual(
#     object_pos=np.array([0.5, 0, 0.3]),
#     object_size=np.array([0.3, 0.2, 0.1]),
#     goal_pos=np.array([0.5, 0.5, 0.3])
# )
```

## Real-World Humanoid Platforms

### Tesla Optimus

```python
class OptimusController:
    """
    Controller for Tesla Optimus humanoid robot.

    Specifications:
    - Height: 5'8" (173 cm)
    - Weight: 125 lbs (57 kg)
    - DOF: ~40 (including hands)
    - Hands: 11 DOF each (human-like dexterity)
    - Actuators: Custom electromagnetic actuators
    """

    def __init__(self):
        self.num_joints = 40
        self.hand_dof = 11

    def initialize(self):
        """Initialize Optimus robot."""
        print("Initializing Tesla Optimus...")
        # Connect to robot hardware
        # Load neural network models
        # Calibrate sensors

    def perform_warehouse_task(self):
        """
        Perform warehouse picking task.

        Tasks Optimus is designed for:
        - Picking and placing objects
        - Walking through warehouses
        - Navigating stairs and obstacles
        - Interacting with human workers
        """
        pass
```

### Figure 01

```python
class Figure01Controller:
    """
    Controller for Figure AI's Figure 01 robot.

    Focus: General-purpose humanoid for commercial deployment
    """

    def __init__(self):
        self.num_joints = 38

    def autonomous_navigation(self, goal):
        """Navigate autonomously to goal."""
        # Uses vision + LiDAR for navigation
        # Whole-body control for balance
        # Dynamic obstacle avoidance
        pass
```

## Summary

- Humanoid robots require complex coordination of 30-50 degrees of freedom
- Forward and inverse kinematics solve for end-effector positioning
- Whole-body QP controllers optimize multi-task objectives
- Balance control uses ZMP to maintain stability
- Walking gaits require careful foot trajectory planning
- Dual-arm manipulation enables bimanual tasks
- Modern humanoids (Optimus, Figure 01) target commercial applications

## Exercises

1. Implement forward kinematics for a 6-DOF humanoid arm using DH parameters
2. Solve inverse kinematics to reach a target position using numerical optimization
3. Create a ZMP balance controller and test stability for various COM positions
4. Generate a walking gait with 4 steps and visualize foot trajectories
5. Design a whole-body controller for simultaneous arm reaching and balance

## Next Chapter

In Chapter 12, we'll explore Conversational Robotics and Vision-Language-Action (VLA) models - enabling robots to understand and execute natural language commands using foundation models like RT-2 and OpenVLA.
