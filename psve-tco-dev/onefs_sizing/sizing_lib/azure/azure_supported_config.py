import json

class AzureSupportedConfig:
    def __init__(self, config_path):
        with open(config_path, 'r') as supported_config_file:
            config_data = json.load(supported_config_file)
            self.instance_families = config_data["instance-families"]
            self.node_count = config_data["node-count"]
            self.protection_level = config_data["protection-level"]
            self.efficiency = config_data["efficiency"]
            self.volume_types = config_data["volumn-types"]
            self.data_disk_counts = config_data["volumn-count-per-node"]
            self.data_disk_counts.sort()
            self.minimum_cluster_size_tib = config_data["minimum-cluster-size-tib"]
            
    def ValidDataDiskType(self, disk_family, disk_type, raw_capacity, protection_level):
        cluster_min_capacity = self.volume_types[disk_family][disk_type]["min-cluster-size-tib"]
        cluster_max_2d1n = self.volume_types[disk_family][disk_type]["max-cluster-size-2d1n-tib"]
        cluster_max_2n = self.volume_types[disk_family][disk_type]["max-cluster-size-2n-tib"]
        
        if protection_level == "+2d:1n":
            if raw_capacity >= cluster_min_capacity and raw_capacity <= cluster_max_2d1n:
                return True
            else:
                return False
        elif protection_level == "+2n":
            if raw_capacity >= cluster_min_capacity and raw_capacity <= cluster_max_2n:
                return True
            else:
                return False
        else:
            print("Invalid protection level.")
            return False
    
    def RawCapacitySmallerThanSupportedDiskType(self, disk_family, raw_capacity):
        disk_family_minimum_cluster_capacity = self.minimum_cluster_size_tib[disk_family]
        if raw_capacity < disk_family_minimum_cluster_capacity:
            return True
        else:
            return False
        
    def FindClosestSupportedDiskCount(self, disk_family, disk_type, per_node_disk_count):
        if per_node_disk_count > self.data_disk_counts[-1]:
            print(f"Require at least {per_node_disk_count} disks. More than {self.data_disk_counts[-1]} disks is not supported.")
            return -1
        for dc in self.data_disk_counts:
            if dc < per_node_disk_count:
                continue
            else:
                return dc
        