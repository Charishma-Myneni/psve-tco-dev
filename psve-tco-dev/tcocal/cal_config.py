import os
import tcocal.utilities as utilities

PRICE_DIR_PATH = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "price"       
        )
SUPPORTED_CLUSTER_CONFIG_PATH = os.path.join(PRICE_DIR_PATH, "supported_cluster_config.json")  
EC2_PRICE_PATH = os.path.join(PRICE_DIR_PATH, "ec2-price.json")  
EBS_PRICE_PATH = os.path.join(PRICE_DIR_PATH, "ebs-price.json")  
ONEFS_LICENSE_PRICE_PATH = os.path.join(PRICE_DIR_PATH, "onefs-license-price.json")  
EFS_PRICE_PATH = os.path.join(PRICE_DIR_PATH, "efs-price.json")  

class CalConfig:
    def __init__(self):
        """
        Initializes the object with the necessary paths and data.

        Parameters:
            None

        Returns:
            None
        """
        self.price_dir_path = PRICE_DIR_PATH
        self.supported_cluster_config_path = SUPPORTED_CLUSTER_CONFIG_PATH
        self.ec2_price_path = EC2_PRICE_PATH
        self.ebs_price_path = EBS_PRICE_PATH
        self.onefs_license_price_path = ONEFS_LICENSE_PRICE_PATH
        self.efs_price_path = EFS_PRICE_PATH
        self.supported_cluster_config = utilities.load_json_data(self.supported_cluster_config_path)
        self.ec2_price = utilities.load_json_data(self.ec2_price_path)
        self.ebs_price = utilities.load_json_data(self.ebs_price_path)
        self.onefs_license_price = utilities.load_json_data(self.onefs_license_price_path)
        self.efs_price = utilities.load_json_data(self.efs_price_path)

    # get supported regions based on supported cluster config json file
    def get_supported_onefs_versions(self):
        """
        Get the supported OneFS versions.

        Returns:
            list: A list of supported OneFS versions.
        """
        supported_onefs_versions = list(self.supported_cluster_config.keys())
        return supported_onefs_versions

    # get supported regions based on supported cluster config json file
    def get_supported_regions(self, onefs_version):
        """
        Get the supported regions for a given OneFS version.

        Parameters:
            onefs_version (str): The version of OneFS.

        Returns:
            list: A list of supported regions.
        """
        # assume the price folder is under same dir with the cal_config.py
        supported_regions =  self.supported_cluster_config[onefs_version]["supported-regions"]
        return supported_regions

    # get supported instance type based on ec2 price json file and supported cluster config json file
    def get_supported_instance_types(self, onefs_version, aws_region):
        # assume the price folder is under same dir with the cal_config.py
        # get the availabel instance types for a specific region in the ec2_price.json file
        region_instance_types = [key for key in self.ec2_price[aws_region]]
        # get the availabel instance types for a onefs version in the supported_cluster_config.json file
        config_instance_types =  self.supported_cluster_config[onefs_version]['supported-instance-type']
        # the final supported instance types listed to users should be the intersection of the two above
        supported_instance_types = list(set(region_instance_types) & set(config_instance_types))
        return supported_instance_types
    
    def get_supported_cluster_node_amount(self, onefs_version):
        supported_cluster_node_amount = self.supported_cluster_config[onefs_version]['cluster-node-amount']
        return supported_cluster_node_amount

    def get_supported_node_disk_amount(self, onefs_version, disk_type):
        supported_node_disk_amount = []
        if disk_type == 'gp3':
            supported_node_disk_amount =  self.supported_cluster_config[onefs_version]['ssd-cluster']['supported-node-disk-amount']
        if disk_type == 'st1':
            supported_node_disk_amount =  self.supported_cluster_config[onefs_version]['hdd-cluster']['supported-node-disk-amount']
        return supported_node_disk_amount

    # get supported node disk size based on supported cluster config json file, including min, max and step
    def get_supported_node_disk_size(self, onefs_version, disk_type):
        if disk_type == 'gp3':
            supported_node_disk_size_min =  self.supported_cluster_config[onefs_version]['ssd-cluster']['supported-node-disk-size-min']
            supported_node_disk_size_max =  self.supported_cluster_config[onefs_version]['ssd-cluster']['supported-node-disk-size-max']
            supported_node_disk_size_step =  self.supported_cluster_config[onefs_version]['ssd-cluster']['supported-node-disk-size-step']
        if disk_type == 'st1':
            supported_node_disk_size_min =  self.supported_cluster_config[onefs_version]['hdd-cluster']['supported-node-disk-size-min']
            supported_node_disk_size_max =  self.supported_cluster_config[onefs_version]['hdd-cluster']['supported-node-disk-size-max']
            supported_node_disk_size_step =  self.supported_cluster_config[onefs_version]['hdd-cluster']['supported-node-disk-size-step']
        supported_node_disk_size = [supported_node_disk_size_min, supported_node_disk_size_max, supported_node_disk_size_step]
        return supported_node_disk_size

cal_config = CalConfig()


