import json

class AzureUtility:
    def __init__(self):        
        azure_ebs_disk_info_path = 'onefs_sizing/raw_data/azure/azure_ebs_disk_info_2024_march.json'        
        with open(azure_ebs_disk_info_path, 'r') as disk_info_file:
            self.disk_info_data_from_file = json.load(disk_info_file)
        
        azure_ebs_network_limit_path = 'onefs_sizing/raw_data/azure/azure_ebs_network_limit_2024_march.json'
        with open(azure_ebs_network_limit_path, 'r') as inst_type_info_file:
            self.instype_info_data_from_file = json.load(inst_type_info_file)
            
        azure_pricing_info_path = 'onefs_sizing/raw_data/azure/azure_pricing_2024_march.json'
        with open(azure_pricing_info_path, 'r') as pricing_info_file:
            self.pricing_info_data_from_file = json.load(pricing_info_file)
        
                    
    def GetDiskSize(self, disk_family, disk_type):
        return self.disk_info_data_from_file[disk_family][disk_type]["volume-size-fixed-tib"]
    
    def GetPremSsdDiskTput(self, disk_type):
        return self.disk_info_data_from_file["premium-ssd"][disk_type]["volume-base-tput-mb-per-sec"]
    
    def GetStdSsdDiskTput(self, disk_type):
        return self.disk_info_data_from_file["standard-ssd"][disk_type]["volume-base-tput-mb-per-sec-upto"]
    
    def GetStdHddDiskTput(self, disk_type):
        return self.disk_info_data_from_file["standard-hdd"][disk_type]["volume-base-tput-mb-per-sec-upto"]
    
    def GetInstanceTypeBurstLimits(self, inst_type):
        return self.instype_info_data_from_file[inst_type]["burst-ebs-bw-limit-mbps"]
    
    def GetInstanceTypeBaseBwLimits(self, inst_type):
        return self.instype_info_data_from_file[inst_type]["base-ebs-bw-limit-mbps"]
    
    def GetInstanceHardCodedTypeHourlyCost(self, inst_family, inst_type):
        return self.pricing_info_data_from_file["vm-hourly-cost"][inst_family][inst_type]
    
    def GetDataDiskHardCodedHourlyCost(self, vol_family, vol_type):
        return self.pricing_info_data_from_file["volume-hourly-cost"][vol_family][vol_type]
