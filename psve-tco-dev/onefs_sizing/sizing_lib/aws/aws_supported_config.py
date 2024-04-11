import json
from onefs_sizing.sizing_lib.aws.utilities import QueryAllSupporedInstanceEbsLimit

class AwsSupportedConfig:
    def __init__(self, config_path):
        with open(config_path, 'r') as supported_config_file:
            config_data = json.load(supported_config_file)
            self.instance_families = config_data["instance-families"]
            self.node_count = config_data["node-count"]
            self.protection_level = config_data["protection-level"]
            self.efficiency = config_data["efficiency"]
            self.volume_types = config_data["volumn-types"]
            
            self.supported_inst_type_list = []
            for instances in self.instance_families.values():
                self.supported_inst_type_list += instances
            
            self.inst_type_ebs_limits = QueryAllSupporedInstanceEbsLimit(self.supported_inst_type_list)

    def ShowDetailConfig(self):
        # Show supported instance types.
        family_names = list(self.instance_families.keys())
        print("Supported AWS EC2 instance families:", family_names)
        for inst_family in family_names:
            print(f"EC2 family {inst_family}: {self.instance_families[inst_family]}")

        # Show supported cluster size.
        print(f"Cluster node count: {self.node_count}")

        # Show supported protection level.
        print(f"Protection level is: {self.protection_level}")

        # Show supported EBS Volume types.
        volume_types = list(self.volume_types.keys())
        print(f"Support EBS volume types: {volume_types}")
        for vol_type in volume_types:
            print(f"Volume type {vol_type} details: {self.volume_types[vol_type]}")

    def GetSupportedVolumeCount(self, volume_type):
        volume_count_list = self.volume_types[volume_type]['volumn-count-per-node']
        return volume_count_list
    
    def GetInstanceEBSLimit(self, inst_type: str):
        return self.inst_type_ebs_limits[inst_type]