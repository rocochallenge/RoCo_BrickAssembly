import omni.kit.app
from isaacsim.core.api.world import World
from isaacsim.core.api.materials import PhysicsMaterial
from isaacsim.core.prims import SingleArticulation, SingleXFormPrim, SingleGeometryPrim
from isaacsim.core.utils.stage import open_stage_async, add_reference_to_stage, get_current_stage
from isaacsim.core.utils.types import ArticulationAction
from isaacsim.core.utils.viewports import set_camera_view
from isaacsim.sensors.camera import Camera
from pxr import Gf, Usd, UsdGeom, Sdf

from bricksim.assets import DEFAULT_STAGE_PATH
from bricksim.core import (
    arrange_parts_in_workspace,
    AssemblyThresholds,
    import_lego,
    set_assembly_thresholds,
)

from rocobrick.utils import *
from rocobrick.robot.Robot import *
from rocobrick.task_config.Task import *

class Env():
    def __init__(self, root_dir, user_config_path, system_config_path):
        self.root_dir = root_dir
        self.user_config_path = os.path.join(self.root_dir, user_config_path)
        self.system_config_path = os.path.join(self.root_dir, system_config_path)
        self.brick_unit_height = 0.0096 # Unit height of a standard lego brick, m.

    async def reset(self):
        """
        Resets the simulation environment by loading the configuration, setting up the simulation, robot, and task, and resetting the world. 
        This should be called at the beginning of each episode.
        """
        # Load configuration json files
        self.config = self.load_config()
        self.cameras = {}

        # Setup simulation, robot, and task
        self.task_config = TaskConfig(self.config)
        self.app, self.world = await self.setup_bricksim(self.config)
        self.robot, self.robot_pin = await self.setup_robot(self.config, self.world)
        self.topology, self.pre_placed_parts, self.to_place_placed = self.setup_task(self.task_config)
        await self.world.reset_async()
        self.apply_pose_offset_world("/World/Cube", 0, 0.3)
        await self.step()

    def load_config(self):
        """
        Loads the configuration from JSON files.
        """
        user_config = load_json(self.user_config_path)
        system_config = load_json(self.system_config_path)
        config = deep_merge(user_config, system_config)
        return config
    
    def setup_task(self, task_config):
        """
        Loads the task.
        Setup the task environment by placing the pre-placed parts onto the plate and arranging the to-be-placed parts in the storage area. 
        
        Returns:
            topology: the full structure topology.
            pre_placed_parts: the parts that are already placed on the base plate.
            to_place_placed: the parts that need to be placed in the storage area.
        """
        # Load structure to assemble (including base plate)
        topology = deepcopy(task_config.topology)
        pre_placed_topology = deepcopy(task_config.pre_placed_topology)
        to_place_topology = deepcopy(task_config.to_placed_topology)
        baseplate_pose = task_config.baseplate_pose

        # Place pre-placed parts
        pre_placed_parts, pre_placed_conns = import_lego(
            json=pre_placed_topology,
            env_id=-1,
            ref_pos=baseplate_pose[0],
            ref_rot=baseplate_pose[1],
        )
        parts_not_placed = set(part['id'] for part in pre_placed_topology['parts']) - set(pre_placed_parts.keys())
        conns_not_placed = set(conn['id'] for conn in pre_placed_topology['connections']) - set(pre_placed_conns.keys())
        if len(parts_not_placed) > 0 or len(conns_not_placed) > 0:
            raise RuntimeError(f"Failed to place pre-placed parts/connections; not placed parts: {parts_not_placed}, not placed connections: {conns_not_placed}")

        # Spawn unplaced parts on table for assembly
        to_place_placed, _ = import_lego(
            json=to_place_topology,
            env_id=-1
        )
        to_place_not_placed = set(part['id'] for part in to_place_topology['parts']) - set(to_place_placed.keys())
        if len(to_place_not_placed) > 0:
            raise RuntimeError(f"Failed to place parts for assembly; not placed: {to_place_not_placed}")
        arranged, not_arranged = arrange_parts_in_workspace(
            workspace_path="/World/LegoWorkspace",
            parts_to_arrange=[path for id, path in to_place_placed.items()],
        )
        if len(not_arranged) > 0:
            raise RuntimeError(f"Failed to arrange all parts in workspace; not arranged: {not_arranged}")
        return topology, pre_placed_parts, to_place_placed

    async def setup_bricksim(self, config):
        """
        Sets up the BrickSim simulation environment.
        """
        # Initialize simulation
        app = omni.kit.app.get_app()
        if World._world_initialized:
            World.clear_instance()
        time.sleep(0.5)
        await open_stage_async(str(DEFAULT_STAGE_PATH))
        world: World = World(
            backend="numpy",
            device="cpu",
            physics_prim_path="/physicsScene"
        ) 
        await world.initialize_simulation_context_async()

        # Set simulation fps
        physics_context = world.get_physics_context()
        physics_context.set_physics_dt(1.0 / config["BrickSim_Physics"]["FPS"])

        # Set physics material for tabletop
        table_material = PhysicsMaterial(
            prim_path="/World/PhysicsMaterials/Tabletop",
            static_friction=config["BrickSim_Physics"]["Table_Material"]["Static_Friction"],
            dynamic_friction=config["BrickSim_Physics"]["Table_Material"]["Dynamic_Friction"],
            restitution=config["BrickSim_Physics"]["Table_Material"]["Restitution"],
        )
        SingleGeometryPrim(prim_path="/World/scene/roomScene/colliders/table/tableTopActor").apply_physics_material(table_material)

        # Set assembly thresholds
        thresholds = AssemblyThresholds()
        thresholds.distance_tolerance = config["BrickSim_Physics"]["Assembly_Config"]["Distance_Tolerance"]
        thresholds.max_penetration = config["BrickSim_Physics"]["Assembly_Config"]["Max_Penetration"]
        thresholds.z_angle_tolerance = config["BrickSim_Physics"]["Assembly_Config"]["Z_Angle_Tolerance"] * (math.pi / 180.0)
        thresholds.required_force = config["BrickSim_Physics"]["Assembly_Config"]["Required_Force"]
        thresholds.yaw_tolerance = config["BrickSim_Physics"]["Assembly_Config"]["Yaw_Tolerance"] * (math.pi / 180.0)
        thresholds.position_tolerance = config["BrickSim_Physics"]["Assembly_Config"]["Position_Tolerance"]
        set_assembly_thresholds(thresholds)

        # Setup workspace
        storage_size = config["Env_Config"]["Storage_Config"]["Size"]
        storage_pos = config["Env_Config"]["Storage_Config"]["Position"]
        storage_ori = config["Env_Config"]["Storage_Config"]["Orientation"]
        workspace_prim = get_current_stage().GetPrimAtPath("/World/LegoWorkspace")
        workspace_prim.GetAttribute("xformOp:scale").Set(Gf.Vec3d(storage_size[0], storage_size[1], storage_size[2]))
        workspace_prim.GetAttribute("xformOp:translate").Set(Gf.Vec3d(storage_pos[0], storage_pos[1], storage_pos[2]))
        workspace_prim.GetAttribute("xformOp:orient").Set(Gf.Quatd(storage_ori[0], storage_ori[1], storage_ori[2], storage_ori[3]))
        workspace_prim.GetRelationship("lego:workspace_obstacles").AddTarget("/World/Robot/base")
        
        set_camera_view(
            eye=np.array([-0.40, 1.0, 0.60]),
            target=np.array([0.0, -0.20, 0.30]),
            camera_prim_path="/OmniverseKit_Persp",
        )
        return app, world

    async def setup_robot(self, config, world):
        """
        Sets up the robot in the simulation environment by spawning the robot, setting its base pose, creating its articulation, and configuring its joints and cameras according to the provided configuration.
        """
        # Spawn the robot
        robot_pin = Robot_Pin(os.path.join(self.root_dir, config["Robot_Config"]["Robot_URDF_Path"]), 
                              os.path.join(self.root_dir, config["Robot_Config"]["Robot_Package_Dir"]))
        robot_pin.home_q = np.array(config["Robot_Config"]["Joint_Home_Position"])
        robot_prim_path = "/World/Robot"
        add_reference_to_stage(usd_path=os.path.join(self.root_dir, config["Robot_Config"]["Robot_USD_Path"]), 
                               prim_path=robot_prim_path)

        # Set robot pose
        robot_xf = SingleXFormPrim(prim_path=robot_prim_path, name="Robot")
        robot_xf.set_world_pose(position=config["Robot_Config"]["Robot_Base_Frame"]["Position"],
                                orientation=config["Robot_Config"]["Robot_Base_Frame"]["Orientation"])
        robot_base_T = np.eye(4)
        robot_base_T[:3, 3] = config["Robot_Config"]["Robot_Base_Frame"]["Position"]
        robot_base_T[:3, :3] = R.from_quat(config["Robot_Config"]["Robot_Base_Frame"]["Orientation"][1:] + [config["Robot_Config"]["Robot_Base_Frame"]["Orientation"][0]]).as_matrix()
        robot_pin.BASE_T = robot_base_T

        # Create robot articulation
        robot = SingleArticulation(prim_path=robot_prim_path, name="Robot")
        world.scene.add(robot)

        # Increase position solver iterations for better assembly stability (32 -> 64)
        stage = get_current_stage()
        stage.GetPrimAtPath("/World/Robot").CreateAttribute("physxRigidBody:solverPositionIterationCount", Sdf.ValueTypeNames.Int).Set(64)
        
        # Modify robot joint physics if specified
        if("Joints_Physics" in config["Robot_Config"].keys()):
            for joint_name in config["Robot_Config"]["Joints_Physics"].keys():
                max_force = config["Robot_Config"]["Joints_Physics"][joint_name]["Max_Force"] 
                damping = config["Robot_Config"]["Joints_Physics"][joint_name]["Damping"] 
                stiffness = config["Robot_Config"]["Joints_Physics"][joint_name]["Stiffness"] 
                joint_prim = stage.GetPrimAtPath(joint_name)
                joint_prim.GetAttribute("drive:angular:physics:maxForce").Set(max_force)
                joint_prim.GetAttribute("drive:angular:physics:damping").Set(damping)
                joint_prim.GetAttribute("drive:angular:physics:stiffness").Set(stiffness)

        # Modify gripper properties if specified
        if("Gripper_Config" in config["Robot_Config"].keys()):
            # Apply new physics material for gripper fingertips if specified
            if("Material" in config["Robot_Config"]["Gripper_Config"].keys()):
                pad_material = PhysicsMaterial(prim_path="/World/PhysicsMaterials/FingerPad",
                                               static_friction=config["Robot_Config"]["Gripper_Config"]["Material"]["Static_Friction"],
                                               dynamic_friction=config["Robot_Config"]["Gripper_Config"]["Material"]["Dynamic_Friction"],
                                               restitution=config["Robot_Config"]["Gripper_Config"]["Material"]["Restitution"],)
                
                for finger_prim_name in config["Robot_Config"]["Gripper_Config"]["Material"]["Link_Instance_Names"]:
                    try:    
                        # Unset instanceable
                        stage.GetPrimAtPath(finger_prim_name).SetInstanceable(False)
                        # Set physics material for fingertip pads
                        SingleGeometryPrim(prim_path=finger_prim_name).apply_physics_material(pad_material)
                    except Exception as e:
                        print(e)
                        raise TypeError("Config gripper material failed!")
        
        # Setup Cameras
        if("Camera_Config" in config["Robot_Config"].keys()):
            for cam_name in config["Robot_Config"]["Camera_Config"].keys():
                cam_path = config["Robot_Config"]["Camera_Config"][cam_name]["Prim_Path"]
                prim = stage.GetPrimAtPath(cam_path) if stage else None
                if not prim or not prim.IsValid():
                    print(f"[setup] WARNING: {cam_name} not found at {cam_path!r}. "
                            f"Skipping — check that the robot USD authors it.")

                # Wrap each USD camera as an Isaac Sim Camera sensor. Resolution
                # is the sensor buffer size (not authored on the USD prim).
                cam = Camera(
                    prim_path=cam_path,
                    name=cam_name,
                    resolution=(config["Robot_Config"]["Camera_Config"][cam_name]["Resolution"][0], config["Robot_Config"]["Camera_Config"][cam_name]["Resolution"][1]),
                    frequency=config["Robot_Config"]["Camera_Config"][cam_name]["FPS"],
                )
                cam.initialize()
                cam.add_distance_to_image_plane_to_frame()
                self.cameras[cam_name] = cam

        # Set initial robot joint positions and velocities
        robot.set_joint_positions(robot_pin.home_q)
        robot.set_joint_velocities(np.zeros(robot_pin.nq))
        await self.step()
        return robot, robot_pin
    
    def robot_apply_action(self, q_cmd, input_joint_orders=["Lift", "torso_flip", 
                                                            "L_arm_j1", "L_arm_j2", "L_arm_j3", "L_arm_j4", "L_arm_j5", "L_arm_j6", "L_arm_j7", "L_gripper_joint", "L_gripper_joint_01",
                                                            "R_arm_j1", "R_arm_j2", "R_arm_j3", "R_arm_j4", "R_arm_j5", "R_arm_j6", "R_arm_j7", "R_gripper_joint", "R_gripper_joint_01",
                                                            "head_j1", "head_j2", "head_j3"]):
        """
        Applies the given joint position command to the robot. The input q_cmd is expected to be in the order of input_joint_orders, and will be reordered to match the robot's joint order before being applied.
        """
        # Reorder q_cmd to match the robot's joint order
        q_reordered = np.zeros(self.robot_pin.nq)
        for i, joint_name in enumerate(self.robot.dof_names):
            if joint_name in input_joint_orders:
                idx = input_joint_orders.index(joint_name)
                q_reordered[i] = q_cmd[idx]
        self.robot.apply_action(ArticulationAction(joint_positions=q_reordered))
        
    async def step(self):
        """
        Advances the simulation by one step. 
        This should be called after applying actions to the robot to progress the simulation.
        """
        await self.app.next_update_async()

    async def play(self):
        """
        Starts the simulation. This should be called after reset() to begin the simulation loop.
        """
        await self.world.play_async()
        await self.step()

    async def pause(self):
        """
        Pauses the simulation.
        """
        await self.world.pause_async()

    async def get_robot_ready(self):
        """
        Moves the robot to its home position with a predefined joint configuration. 
        This can be called after play() to set the robot to a known starting state before executing any policies.
        """
        for _ in range(180):
            self.robot_apply_action(np.array([0.2, 0.5, 
                                              0, 1.57, 0, 0, 0, 0, 0, 0, 0,
                                              0, -1.57, 0, 0, 0, 0, 0, 0, 0,
                                              0, 0, 0]))
            await self.step()
        for _ in range(60):
            self.robot_apply_action(self.robot_pin.home_q)
            await self.step()

    def apply_pose_offset_world(self, prim_path, x_offset, y_offset):
        """
        Applies a translation offset in the world frame to the specified prim. 
        The prim is identified by its path in the USD stage, and the offset is given by x_offset and y_offset in meters.
        """
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(prim_path)
        xformable = UsdGeom.Xformable(prim)
        world_tf = xformable.ComputeLocalToWorldTransform(Usd.TimeCode.Default())
        t = world_tf.ExtractTranslation()
        
        t[0] = t[0] + x_offset
        t[1] = t[1] + y_offset
        parent = prim.GetParent()
        if parent:
            parent_xform = UsdGeom.Xformable(parent)
            parent_world = parent_xform.ComputeLocalToWorldTransform(Usd.TimeCode.Default())
            parent_world_inv = parent_world.GetInverse()
            local_t = parent_world_inv.Transform(t)
        else:
            local_t = t

        # --- reuse existing translate op if present ---
        translate_op = None
        for op in xformable.GetOrderedXformOps():
            if op.GetOpType() == UsdGeom.XformOp.TypeTranslate:
                translate_op = op
                break

        if translate_op is None:
            translate_op = xformable.AddTranslateOp()

        translate_op.Set(Gf.Vec3d(float(local_t[0]), float(local_t[1]), float(local_t[2])))

    def get_prim_world_T(self, prim_path):
        """
        Retrieves the world transform of the specified prim as a 4x4 homogeneous transformation matrix. 
        The prim is identified by its path in the USD stage.
        """
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(prim_path)
        xformable = UsdGeom.Xformable(prim)
        local_to_world = xformable.ComputeLocalToWorldTransform(Usd.TimeCode.Default())

        r = local_to_world.ExtractRotationMatrix()
        t = local_to_world.ExtractTranslation()
        T = np.eye(4)
        T[:3, :3] = np.array(r).transpose()
        T[:3, 3] = np.array(t)
        return T

    def get_prim_robot_T(self, prim_path):
        """
        Retrieves the transform of the specified prim in the robot base frame as a 4x4 homogeneous transformation matrix.
        The prim is identified by its path in the USD stage. The robot base frame is defined by the robot's BASE_T.
        """
        world_to_robot_T = self.robot_pin.BASE_T
        T = self.get_prim_world_T(prim_path)
        T = world_T_to_robot_T(T, world_to_robot_T)
        return T
    
    def get_observations(self):
        """
        Retrieves the current observations from the environment, including the robot's joint positions and images from the cameras.
        
        Returns:
            obs: a dictionary containing the robot's joint positions and camera images.
        """
        obs = {}
        obs["joint_positions"] = self.robot.get_joint_positions()
        obs["images"] = {}
        obs["images"]["head_rgb"] = self.cameras["Head_Camera"].get_rgb()
        obs["images"]["head_depth"] = self.cameras["Head_Camera"].get_depth()
        obs["images"]["wrist_right_rgb"] = self.cameras["Wrist_Right_Camera"].get_rgb()
        obs["images"]["wrist_right_depth"] = self.cameras["Wrist_Right_Camera"].get_depth()
        obs["images"]["wrist_left_rgb"] = self.cameras["Wrist_Left_Camera"].get_rgb()
        obs["images"]["wrist_left_depth"] = self.cameras["Wrist_Left_Camera"].get_depth()
        return obs