from rocobrick.utils import *
from bricksim.topology.legolization import legolization_json_to_topology_json
from bricksim.colors import parse_color

class TaskConfig():
    """
    TaskConfig class is responsible for loading and parsing the task configuration from the provided JSON files. 
    It extracts the task topology, pre-placed parts, and to-be-placed parts based on the task type and structure files. 
    It also provides utility functions to access the task information.
    """
    def __init__(self, config):
        self.config = config["Task_Config"]
        self.task_path = None
        self.task_type = None
        self.topology = None
        self.pre_placed_topology = None
        self.to_placed_topology = None
        self.baseplate_pose = None
        self.load_task(self.config)

    def load_task(self, config):
        """
        Load the task configuration from the specified JSON files and parse the task topology, pre-placed parts, and to-be-placed parts.
        """
        self.task_path = config["Task_Path"]
        self.task_type = config["Task_Type"]
        self.baseplate_pose = (config["Base_Plate"]["Position"], 
                               config["Base_Plate"]["Orientation"]) # Position (x,y,z), Orientation (w,x,y,z)
        baseplate_kwargs = {
            "include_base_plate": True,
            "base_plate_size": config["Base_Plate"]["Dimension"],
            "base_plate_color": parse_color(config["Base_Plate"]["Color"])
        }
        
        if(self.task_type == "1"): # Type 1 task
            pre_task_fname = os.path.join(self.task_path, "structure_start.json")
            task_fname = os.path.join(self.task_path, "structure_goal.json")
            
            task_graph_pre = load_json(pre_task_fname)
            topology_pre = legolization_json_to_topology_json(task_graph_pre, 
                                                              color=self.get_colors(task_graph_pre), 
                                                              **baseplate_kwargs)

            task_graph = load_json(task_fname)
            topology = legolization_json_to_topology_json(task_graph, 
                                                          color=self.get_colors(task_graph), 
                                                          **baseplate_kwargs)

            pre_placed_parts_config = self.find_pre_placed(topology_pre, topology)
            
        elif(self.task_type == "2"): # Type 2 task
            task_fname = os.path.join(self.task_path, "structure.json")
            task_graph = load_json(task_fname)
            topology = legolization_json_to_topology_json(task_graph, 
                                                          color=self.get_colors(task_graph), 
                                                          **baseplate_kwargs)
            pre_placed_parts_config = [0] # Always assume the plate is placed
        else:
            raise TypeError(f"Unsupported task type: {self.task_type}")
        
        
        # Pre-placed parts
        pre_placed_topology = deepcopy(topology)
        pre_placed_topology['parts'] = [
            part
            for part in topology['parts']
            if part['id'] in pre_placed_parts_config
        ]
        pre_placed_topology['connections'] = [
            conn
            for conn in topology['connections']
            if conn['stud_id'] in pre_placed_parts_config and conn['hole_id'] in pre_placed_parts_config
        ]
        
        # Unplaced parts
        to_place_topology = deepcopy(topology)
        to_place_topology['parts'] = [
            part
            for part in topology['parts']
            if part['id'] not in pre_placed_parts_config
        ]
        to_place_topology['connections'] = []
        to_place_topology['pose_hints'] = []

        self.topology = topology
        self.pre_placed_topology = pre_placed_topology
        self.to_placed_topology = to_place_topology


    def find_pre_placed(self, topology_pre, topology):
        """
        Find the pre-placed parts by comparing the initial and goal topologies.
        """
        pre_placed_parts = []
        for part in topology['parts']:
            for part_pre in topology_pre['parts']:
                if part['id'] == part_pre['id']:
                    pre_placed_parts.append(part_pre['id'])
                    break
        return pre_placed_parts
    
    def get_colors(self, task_graph):
        """
        Get the colors of the parts in the task graph.
        """
        colors = []
        for i in range(1, len(task_graph)+1):
            colors.append(parse_color(task_graph[str(i)]['color']))
        return colors
    
if __name__ == "__main__":
    user_config = load_json("./config/user_config.json")
    system_config = load_json("./config/system_config.json")
    config = deep_merge(user_config, system_config)

    task_config = TaskConfig(config)
    print(task_config.topology)
    print(task_config.pre_placed_topology)
    print(task_config.to_placed_topology)