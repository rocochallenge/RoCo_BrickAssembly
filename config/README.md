# RoCo-BrickAssembly Configuration Guide

### 1. `lego_library.json`
Defines the physical dimensions of the available bricks. Maps a unique `brick_id` to its corresponding `width` and `height` properties (e.g., a `brick_id` of `"2"` defines a 2x4 brick).

### 2. `system_config.json`
⚠️ **Do not modify this file.**
This establishes the default configuration for the BrickSim environment.
### 3. `user_config.json`
✅ **Modify this configuration as you see fit.**
This file contains the customizable variables for your specific assembly task, robotic hardware, and spatial environment. 

#### Task Configuration (`Task_Config`)
Defines the objectives and foundational setup of the current assembly task.
* **`Task_Path`**: File path pointing to the specific task folder.
* **`Task_Type`**: Classifies the task as Type-1 or Type-2. (See [Task Descriptions](../tasks/README.md) for detailed definitions).
* **`Base_Plate`**: Properties of the baseplate, including its `Dimension` (e.g., [32, 32]), `Position`, `Orientation`, and `Color`.

#### Robot Configuration (`Robot_Config`)
Defines the robotic asset, its initial state, kinematic properties, and sensory payload.
* **Asset Paths**:
    * `Robot_Package_Dir`: Directory containing the robot's models and meshes.
    * `Robot_URDF_Path`: Path to the robot's URDF file.
    * `Robot_USD_Path`: Path to the robot's USD file.
* **Positioning & State**:
    * `Robot_Base_Frame`: The spawn `Position` and `Orientation` for the robot's base.
    * `Joint_Home_Position`: A 23-dimensional array establishing the robot's initial resting pose. 
        * *Array Format:* `[Lift, torso_flip, L_arm_j1 to L_arm_j7, L_gripper_joint, Unused, R_arm_j1 to R_arm_j7, R_gripper_joint, Unused, head_j1, head_j2, head_j3]`
* **Physics & Hardware**:
    * `Joints_Physics`: Allows localized overrides for joint dynamics.
        * *Format:* `"joint_name": {"Max_Force": float, "Damping": float, "Stiffness": float}`
    * `Camera_Config`: Defines the vision sensors attached to the robot. (Note: These cameras must be pre-allocated in the robot's USD file).
        * *Format:* `"camera_name": {"FPS": int, "Resolution": [width, height], "Prim_Path": "prim_name_in_usd"}`
    * `Gripper_Config`: Configures the physical interaction properties of the end-effectors. Specifies a custom `Material` (`Static_Friction`, `Dynamic_Friction`, `Restitution`) and an array of `Link_Instance_Names` to dictate which structural links inherit these properties.

#### Environment Configuration (`Env_Config`)
Defines the surrounding spatial setup and external objects.
* **`Storage_Config`**: Configures the staging area where unassembled bricks are spawned before manipulation. It is defined as a bounding cuboid with specific `Size`, `Position` (centroid), and `Orientation` variables.