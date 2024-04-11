import re, math
from azure_tcocal.azure_cal_config import azure_cal_config

HOURS_PER_MONTH = 730

class AzureFiles:

    # Azure Files supports premium_ssd and standard_ssd. But the tool will only support premium ssd, just to keep the tier option for future use. and only support LRS Redundancy.
    # capacit size is GiB, minimum is 100 GiB
    def __init__(self, region: str, capacity_gib: int, tier: str = "premium_ssd_LRS"):
        self.region = region
        self.capacity_gib = capacity_gib # GiB
        self.tier = tier 

    def validate_azure_files(self):
        if self.tier not in ["premium_ssd_LRS"]:
            raise Exception(f"Wrong/unsupported Azure Files tier {self.tier} in {self.region} region. Only support premium_ssd_LRS in this tool.")
        if self.capacity_gib < 100:
            raise Exception(f"Wrong/unsupported Azure Files capacity {self.capacity_gib} in {self.region} region. Minimum capacity is 100 GiB.")
        

    # Reserve capacity helps you lower your data storage cost by committing to one year or three years of Azure Files. 
    # Reserve capacity can be purchased in increments of 10 TiB and 100 TiB for 1-year and 3-year commitment durations. 
    # For more information, please see understanding capacity reservations (https://docs.microsoft.com/en-us/azure/storage/files/understanding-billing/).
    # e.g. if your estimate of 112600 GiB can be covered by 1 10-TiB increments and 1 100-TiB increments.
    def cal_azure_files_monthly_cost_reservation(self, reservation_term: str):
        if reservation_term in ["1 Year", "3 Years"]:
            capacity_tib = round(self.capacity_gib / 1024, 2)
            print(capacity_tib)
            increment_100tib = capacity_tib // 100
            increment_10tib = math.ceil(capacity_tib % 100 / 10)
            print(increment_100tib)
            print(increment_10tib)

            azure_files_price = azure_cal_config.azure_files_price
            azure_files_cost_reservation = 0
            for reservation in azure_files_price[self.region][self.tier]["reservation"][reservation_term]:
                if reservation["armSkuName"] == "Premium_LRS_Provisioned_10 TB":
                    increment_10tib_cost = reservation["retailPrice"] * increment_10tib
                    azure_files_cost_reservation += increment_10tib_cost
                elif reservation["armSkuName"] == "Premium_LRS_Provisioned_100 TB":
                    increment_100tib_cost = reservation["retailPrice"] * increment_100tib
                    azure_files_cost_reservation += increment_100tib_cost
            azure_files_monthly_cost_reservation = azure_files_cost_reservation / 12 / int(reservation_term.split(" ")[0])
        else:
            raise Exception(f"Wrong reservation term {reservation_term} provided for {self.region} region. Ensure your reservation term is 1 Year or 3 Years.")
        return azure_files_monthly_cost_reservation

class AzureNetappFiles:

    # Azure NetApp Files supports Ultra, Premium, Standard. This tool use Single encryption
    # capacity size is TiB, minimum is 2TiB
    def __init__(self, region: str, capacity_tib: int, tier: str = "Ultra"):
        self.region = region
        self.capacity_tib = capacity_tib # TiB
        self.tier = tier 

    def validate_azure_files(self):
        if self.tier not in ["Ultra", "Premium", "Standard"]:
            raise Exception(f"Wrong/unsupported Azure NetApp Files tier {self.tier} in {self.region} region. Only support premium_ssd_LRS in this tool.")
        if self.capacity_tib < 2:
            raise Exception(f"Wrong/unsupported Azure NetApp Files capacity {self.capacity_tib} TiB in {self.region} region. Minimum capacity is 2 TiB.")
        

    # https://azure.microsoft.com/en-us/pricing/details/netapp/#pricing
    # https://bluexp.netapp.com/azure-netapp-files/sizer
    def cal_azure_netapp_files_monthly_cost(self):

        if azure_cal_config.azure_netapp_files_price[self.region]["pay-as-you-go"][self.tier]["unitOfMeasure"] == "1 GiB/Hour":
            hourly_price = azure_cal_config.azure_netapp_files_price[self.region]["pay-as-you-go"][self.tier]["retailPrice"]
        else:
            raise Exception(f"Wrong Azure NetApp Files unit in {self.region} region in your price json file. Ensure it is 1 GiB/Hour.")
        
        azure_files_monthly_cost = self.capacity_tib * 1024 * hourly_price * HOURS_PER_MONTH

        return azure_files_monthly_cost
    
    # https://azure.github.io/azure-netapp-files/calc/advanced/ the Maximum throughput is 4,500 MiB/s and only apply to Ultra and Premium storage
    def cal_azure_netapp_files_throughput(self):
        base_perf_str = azure_cal_config.azure_netapp_files_price[self.region]["performance"][self.tier]["base_perf"]
        match = re.search(r'\d+', base_perf_str)
        base_perf_number = int(match.group())
        base_perf_unit = base_perf_str[match.end():]
        if base_perf_unit == "MiB/s per TiB" and self.tier in ["Ultra", "Premium"]:
            
            if self.capacity_tib * base_perf_number > 4500:
                azure_netapp_files_throughput = 4500 * 1024 * 1024 / 1000 / 1000 / 1000
            else:
                azure_netapp_files_throughput = self.capacity_tib * base_perf_number * 1024 * 1024 / 1000 / 1000 / 1000
        else:
            raise Exception(f"Wrong Azure NetApp Files base_perf unit in {self.region} region in your price json file. Ensure it is MiB/s per TiB.")
        return azure_netapp_files_throughput # GB/s
        

class AzureOnefsNode:
    def __init__(self, region: str, onefs_version: str, vm_size: str, data_disk_tier: str, data_disk_amount: int):
        self.region = region
        self.onefs_version = onefs_version
        self.vm_size = vm_size
        self.data_disk_tier = data_disk_tier.upper()
        self.data_disk_amount = data_disk_amount
        self.disk_size = self.disk_tier_to_size()

    def disk_tier_to_size(self):
        # defines the mapping between managed disk tier and disk size in TiB unit
        size_to_tier = [
            (0.5, "P20", "E20"),
            (1, "P30", "E30"),
            (2, "P40", "E40", "S40"),
            (4, "P50", "E50", "S50"),
            (8, "P60", "E60", "S60"),
            (16, "P70", "E70", "S70")
        ]
        for disk_size, *tiers in size_to_tier:
            if self.data_disk_tier in tiers:
                return disk_size
        raise Exception(f"Wrong/unsupported data disk tier {self.data_disk_tier} in {self.region} region.")
        

    def cal_node_raw_capacity(self):
        raw_capcity = self.data_disk_amount * self.disk_size # TiB
        return raw_capcity

    def cal_node_vm_monthly_cost_pay_as_you_go(self):
        if azure_cal_config.vm_price[self.region][self.vm_size]["pay-as-you-go"]["unitOfMeasure"] == "1 Hour":
            hourly_price = azure_cal_config.vm_price[self.region][self.vm_size]["pay-as-you-go"]["retailPrice"]
        else:
            raise Exception(f"Wrong VM price unit for {self.region} region in the vm price json file. Ensure your VM price unit is 1 Hour.")
        return hourly_price * HOURS_PER_MONTH # 730 hours in a month
    
    # saving_plan_term is 1 Year or 3 Years
    def cal_node_vm_monthly_cost_savings_plan(self, saving_plan_term: str):
        if azure_cal_config.vm_price[self.region][self.vm_size]["pay-as-you-go"]["unitOfMeasure"] == "1 Hour" and saving_plan_term in ["1 Year", "3 Years"]:
            for savings_plans in azure_cal_config.vm_price[self.region][self.vm_size]["pay-as-you-go"]["savingsPlan"]:
                if savings_plans["term"] == saving_plan_term:
                    hourly_price = savings_plans["retailPrice"]
                    break
        else:
            raise Exception(f"Wrong VM price unit for {self.region} region in the vm price json file. Ensure your VM price unit is 1 Hour. Or you passed a wrong saving plan term {saving_plan_term}. Currently only support 1 Year and 3 Years saving_plan_term")
        return hourly_price * HOURS_PER_MONTH # 730 hours in a month

    # reservation_term is 1 Year or 3 Years
    def cal_node_vm_monthly_cost_reservation(self, reservation_term: str):
        if azure_cal_config.vm_price[self.region][self.vm_size]["reservation"][reservation_term]["unitOfMeasure"] == "1 Hour" and reservation_term in ["1 Year", "3 Years"]:
            term_price = azure_cal_config.vm_price[self.region][self.vm_size]["reservation"][reservation_term]["retailPrice"] # this is the total price for the whole reservation term
        else:
            raise Exception(f"Wrong VM price unit for {self.region} region in the vm price json file. Ensure your VM price unit is 1 Hour. Or you passed a wrong reservation term {reservation_term}. Currently only support 1 Year and 3 Years reservation_term")
        term_month = int(reservation_term.split(" ")[0]) * 12
        return term_price/term_month 

    # the transaction parameter is only used by standard SSD and standard HDD with price messure in unit of 10000, for example, transaction = 100 means 1,000,000 transactions
    # transaction set to 0 which means will not consider the transaction price during calculation
    def cal_node_disk_monthly_cost_pay_as_you_go(self, transactions: int = 0):
        if self.data_disk_tier in ["P20", "P30", "P40", "P50", "P60", "P70"]:
            disk_type = "premium_ssd_LRS"
            monthly_price = azure_cal_config.managed_disk_price[self.region][disk_type][self.data_disk_tier]["pay-as-you-go"]["retailPrice"]
            monthly_cost = monthly_price * self.data_disk_amount
        elif self.data_disk_tier in ["E20", "E30", "E40", "E50", "E60", "E70"]:
            disk_type = "standard_ssd_LRS"
            capacity_monthly_price = azure_cal_config.managed_disk_price[self.region][disk_type][self.data_disk_tier]["capacity"]["retailPrice"]
            transactions_monthly_price = azure_cal_config.managed_disk_price[self.region][disk_type][self.data_disk_tier]["transaction"]["retailPrice"]
            monthly_cost = (capacity_monthly_price + transactions_monthly_price * transactions) * self.data_disk_amount 
        elif self.data_disk_tier in ["S40", "S50", "S60", "S70"]:
            pass
        else:
            raise Exception(f"Wrong/unsupported data disk tier {self.data_disk_tier} in {self.region} region.")
       
        return monthly_cost

    # this is for premium SSD P30 and above only, reservation_term is 1 Year only
    # https://learn.microsoft.com/en-us/azure/virtual-machines/disks-reserved-capacity
    def cal_node_disk_monthly_cost_reservation(self):
        reservation_term = "1 Year"
        if self.data_disk_tier in ["P30", "P40", "P50", "P60", "P70"]:
            disk_type = "premium_ssd_LRS"
            if azure_cal_config.managed_disk_price[self.region][disk_type][self.data_disk_tier]["reservation"]["reservationTerm"] == reservation_term:
                term_price = azure_cal_config.managed_disk_price[self.region][disk_type][self.data_disk_tier]["pay-as-you-go"]["retailPrice"]
                monthly_cost = term_price * self.data_disk_amount / 12
            else:
                raise Exception(f"reservation term mismatch for {self.region} region in the managed disk price json file. Ensure your managed disk price is for {reservation_term} term.")
        else:
            raise Exception(f"Wrong/unsupported data disk tier {self.data_disk_tier} in {self.region} region for using reservation disks.")
       
        return monthly_cost

# this class contains necessary functions for Azure OneFS cluster cost calculation, only support +2n and +2d:1n protection level
class AzureOnefsCluster:
    def __init__(self, license_contract_term : str, license_discount: float, node: AzureOnefsNode, node_amount: int, drr_ratio: float, protection_level: str):
        self.region = node.region
        self.license_contract_term  = license_contract_term
        self.license_discount = 83 if license_discount is None else license_discount
        self.node = node
        self.node_amount = node_amount
        self.drr_ratio = float(drr_ratio) if drr_ratio is not None else drr_ratio
        self.protection_level = protection_level
        self.validate_cluster_config()
        self.protection_overhead_map = {
            "4-nodes": {"2n": 2 / 4, "2d:1n": 2 / 8},
            "5-nodes": {"2n": 2 / 5, "2d:1n": 2 / 10},
            "6-nodes": {"2n": 2 / 6, "2d:1n": 2 / 12},
            "7-nodes": {"2n": 2 / 7, "2d:1n": 2 / 14},
            "8-nodes": {"2n": 2 / 8, "2d:1n": 2 / 16},
            "9-nodes": {"2n": 2 / 9, "2d:1n": 2 / 18},
            "10-nodes": {"2n": 2 / 10, "2d:1n": 2 / 18},
            "11-nodes": {"2n": 2 / 11, "2d:1n": 2 / 18},
            "12-nodes": {"2n": 2 / 12, "2d:1n": 2 / 18},
            "13-nodes": {"2n": 2 / 13, "2d:1n": 2 / 18},
            "14-nodes": {"2n": 2 / 14, "2d:1n": 2 / 18},
            "15-nodes": {"2n": 2 / 15, "2d:1n": 2 / 18},
            "16-nodes": {"2n": 2 / 16, "2d:1n": 2 / 18},
            "17-nodes": {"2n": 2 / 17, "2d:1n": 2 / 18},
            "18-nodes": {"2n": 2 / 18, "2d:1n": 2 / 18}  
        }
      
    
    # cluster config should be a suppoted config
    def validate_cluster_config(self):
        if self.protection_level in ["2n", "2d:1n", "+2n", "+2d:1n"]:
            if self.protection_level.startswith("+"):
                self.protection_level = self.protection_level[1:]
        else:
            raise Exception(f"Wrong OneFS protection level {self.protection_level}. Currently only support 2n and 2d:1n protection level.")

    def cal_cluster_raw_capacity(self):
        raw_capcity = self.node_amount * self.node.cal_node_raw_capacity() # TiB
        return raw_capcity

    # currently only support 2n protection level, need to change in the future
    def cal_cluster_usable_capacity(self):
        protection_overhead = self.protection_overhead_map[str(self.node_amount) + "-nodes"][self.protection_level]
        usable_capacity = self.node_amount * self.node.cal_node_raw_capacity() * (1 - protection_overhead) # TiB       
        return usable_capacity
        
    # calculate the OneFS cluster effective capacity based on protection overhead and drr.
    def cal_cluster_effective_capacity(self):
        protection_overhead = self.protection_overhead_map[str(self.node_amount) + "-nodes"][self.protection_level]
        effective_capacity = self.node_amount * self.node.cal_node_raw_capacity() * (1 - protection_overhead) * self.drr_ratio # TiB   
        return effective_capacity
    

    def cal_cluster_vm_monthly_cost_pay_as_you_go(self):
        cluster_vm_monthly_cost_pay_as_you_go = self.node_amount * self.node.cal_node_vm_monthly_cost_pay_as_you_go()
        return cluster_vm_monthly_cost_pay_as_you_go
    
    # saving_plan_term is 1 Year or 3 Years
    def cal_cluster_vm_monthly_cost_savings_plan(self, saving_plan_term: str):
        cluster_vm_monthly_cost_savings_plan = self.node_amount * self.node.cal_node_vm_monthly_cost_savings_plan(saving_plan_term)
        return cluster_vm_monthly_cost_savings_plan
    
    # reservation_term is 1 Year or 3 Years
    def cal_cluster_vm_monthly_cost_reservation(self, reservation_term: str):
        cluster_vm_monthly_cost_reservation = self.node_amount * self.node.cal_node_vm_monthly_cost_reservation(reservation_term)
        return cluster_vm_monthly_cost_reservation
    
    # the transaction parameter is only used by standard SSD and standard HDD with price messure in unit of 10000, for example, transaction = 100 means 1,000,000 transactions
    # transaction set to 0 which means will not consider the transaction price during calculation
    def cal_cluster_disk_monthly_cost_pay_as_you_go(self, transactions: int = 0):
        cluster_disk_monthly_cost_pay_as_you_go = self.node_amount * self.node.cal_node_disk_monthly_cost_pay_as_you_go(transactions)
        return cluster_disk_monthly_cost_pay_as_you_go

    # this is for premium SSD P30 and above only, reservation_term is 1 Year only
    # https://learn.microsoft.com/en-us/azure/virtual-machines/disks-reserved-capacity
    def cal_cluster_disk_monthly_cost_reservation(self):
        cluster_disk_monthly_cost_reservation = self.node_amount * self.node.cal_node_disk_monthly_cost_reservation()
        return cluster_disk_monthly_cost_reservation


    def cal_cluster_onefs_license_monthly_cost(self):
        onefs_license_price_data = azure_cal_config.onefs_license_price
        license_contract_term = self.license_contract_term
        onefs_license_discount = self.license_discount
        if license_contract_term == '1 Year':
            onefs_monthly_price = onefs_license_price_data[license_contract_term]['price']/12
        elif license_contract_term == '3 Years':
            onefs_monthly_price = onefs_license_price_data[license_contract_term]['price']/36
        cluster_onefs_monthly_cost = onefs_monthly_price * self.cal_cluster_raw_capacity() * 1024 * (1-onefs_license_discount/100)
        return cluster_onefs_monthly_cost
