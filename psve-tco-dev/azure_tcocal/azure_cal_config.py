import os
import azure_tcocal.utilities as utilities

PRICE_DIR_PATH = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "price", "processed_data"       
        )
AZURE_SUPPORTED_CLUSTER_CONFIG_PATH = os.path.join(PRICE_DIR_PATH, "azure_supported_cluster_config.json")  
VM_PRICE_PATH = os.path.join(PRICE_DIR_PATH, "azure-vm-price.json")  
MANAGED_DISK_PRICE_PATH = os.path.join(PRICE_DIR_PATH, "azure-managed-disk-price.json")  
ONEFS_LICENSE_PRICE_PATH = os.path.join(PRICE_DIR_PATH, "onefs-license-price.json")  
AZURE_FILES_PRICE_PATH = os.path.join(PRICE_DIR_PATH, "azure-files-price.json")  
AZURE_NETAPP_FILES_PRICE_PATH = os.path.join(PRICE_DIR_PATH, "azure-netapp-files-price.json") 

class AzureCalConfig:
    def __init__(self):
        self.price_dir_path = PRICE_DIR_PATH
        self.azure_supported_cluster_config_path = AZURE_SUPPORTED_CLUSTER_CONFIG_PATH
        self.vm_price_path = VM_PRICE_PATH
        self.managed_disk_price_path = MANAGED_DISK_PRICE_PATH
        self.onefs_license_price_path = ONEFS_LICENSE_PRICE_PATH
        self.azure_files_price_path = AZURE_FILES_PRICE_PATH
        self.azure_netapp_files_price_path = AZURE_NETAPP_FILES_PRICE_PATH
        self.azure_supported_cluster_config = utilities.load_json_data(self.azure_supported_cluster_config_path)
        self.vm_price = utilities.load_json_data(self.vm_price_path)
        self.managed_disk_price = utilities.load_json_data(self.managed_disk_price_path)
        self.onefs_license_price = utilities.load_json_data(self.onefs_license_price_path)
        self.azure_files_price = utilities.load_json_data(self.azure_files_price_path)
        self.azure_netapp_files_price = utilities.load_json_data(self.azure_netapp_files_price_path)

    # get supported regions based on supported cluster config json file
    def get_supported_onefs_versions(self):
        supported_onefs_versions = list(self.azure_supported_cluster_config.keys())
        return supported_onefs_versions

    # get supported regions based on supported cluster config json file
    def get_supported_regions(self, onefs_version):
        # assume the price folder is under same dir with the azure_cal_config.py
        supported_regions =  self.azure_supported_cluster_config[onefs_version]["supported-regions"]
        return supported_regions

    # get supported vm sizes based on vm price json file and supported cluster config json file
    def get_supported_vm_sizes(self, onefs_version, azure_region):
        # assume the price folder is under same dir with the azure_cal_config.py
        # get the availabel vm sizes for a specific region in the azure-vm-price.json file
        region_vm_sizes = [key for key in self.vm_price[azure_region]]
        # get the availabel vm sizes for a onefs version in the azure_supported_cluster_config.json file
        config_instance_types =  self.azure_supported_cluster_config[onefs_version]['supported-vm-size']
        # the final supported vm sizes listed to users should be the intersection of the two above
        supported_instance_types = list(set(region_vm_sizes) & set(config_instance_types))
        return supported_instance_types
    
    def get_supported_cluster_node_amount(self, onefs_version):
        supported_cluster_node_amount = self.azure_supported_cluster_config[onefs_version]['cluster-node-amount']
        return supported_cluster_node_amount

    def get_supported_node_disk_amount(self, onefs_version):
        supported_node_disk_amount = self.azure_supported_cluster_config[onefs_version]['supported-node-disk-amount']
        return supported_node_disk_amount
    
    def get_supported_onefs_license_term(self):
        return list(self.onefs_license_price.keys())

azure_cal_config = AzureCalConfig()




