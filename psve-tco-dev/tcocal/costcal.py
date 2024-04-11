from tcocal.cal_config import cal_config

HOURS_PER_MONTH = 730

class Ec2Instance:
    def __init__(self, instance_type: str, region: str, payment_option: str, **kwargs):   
        """
        Initializes a new instance of the class.

        Args:
            instance_type (str): The type of the instance.
            region (str): The region of the instance.
            payment_option (str): The payment option for the instance.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        self.instance_type = instance_type
        self.region = region
        self.payment_option = payment_option
        for key, value in kwargs.items():
            setattr(self, key, value)

    # This method can be used directly to calculate hourly cost
    def cal_hourly_cost(self, ec2_price_data=cal_config.ec2_price):
        """
        Calculate the hourly cost of running an EC2 instance.

        Parameters:
            ec2_price_data (dict): A dictionary containing the pricing data for EC2 instances.
                Defaults to the `ec2_price` attribute of the `cal_config` module.

        Returns:
            float: The hourly cost of running the EC2 instance.

        Raises:
            Exception: If the EC2 instance price unit is not 'Hrs'.

        """
        # Dash system will auto call this method with self.region and self.instance_type 
        # Therefore, when no region or instance type is provided, return 0
        if self.region is None or self.instance_type is None:
            return 0
        if ec2_price_data[self.region][self.instance_type]["unit"] == "Hrs":
            hourly_cost = float(ec2_price_data[self.region][self.instance_type][self.payment_option])
        else:
            raise Exception(f"Wrong EC2 {self.instance_type} price unit for {self.region} region in the ec2 price json file. Ensure your EC2 price unit is Hrs.")
        return hourly_cost
    
class EbsVolume:

    global cal_config
    # if ebs_type is gp3, then volume_iops and volume_thpt are required. If not provided, will use default values. Assume volume size unit is GiB
    def __init__(self, ebs_type: str, region: str, volume_size: float, volume_iops: int=3000, volume_thpt: float = 125):
        """
        Initializes an instance of the class with the specified EBS type, region, volume size, volume IOPS, and volume throughput.

        Args:
            ebs_type (str): The type of EBS volume.
            region (str): The region where the EBS volume is located.
            volume_size (float): The size of the EBS volume in GiB.
            volume_iops (int, optional): The number of IOPS for the EBS volume. Defaults to 3000.
            volume_thpt (float, optional): The throughput of the EBS volume in MiBps. Defaults to 125.

        Returns:
            None
        """
        self.ebs_type = ebs_type
        self.region = region
        self.volume_size = float(volume_size) # only accept GiB as volume_unit
        if self.ebs_type == "gp3":
            self.volume_iops = volume_iops
            self.volume_thpt = volume_thpt # MiBps
        else:
            self.volume_iops = None
            self.volume_thpt = None # MiBps
        # for key, value in kwargs.items():
        #     if key == "volume_iops":
        #         self.volume_iops = int(value)
        #     elif key == "volume_thpt":
        #         self.volume_thpt = float(value)
        #     else:
        #         setattr(self, key, value)
        self.validate_iops_thpt()

    
    # The reasonable thpt(MiB/s):iops <=0.25, and 1000 >= thpt >= 125, 16000 >= iops >= 3000
    # https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSVolumeTypes.html
    # still need to have further research on capacity and iops,thpt relationship
    def validate_iops_thpt(self):
        """
        Validates the IOPS and THPT values for an EBS volume of type 'gp3'.

        This function checks if the EBS volume type is 'gp3' and performs the following validations:
        - If the volume IOPS is not provided, it is set to 3000.
        - If the volume IOPS is less than 3000 or greater than 16000, an exception is raised with an error message.
        - If the volume THPT is not provided, it is set to 125.
        - If the volume THPT is less than 125 or greater than 1000, an exception is raised with an error message.
        - If the volume THPT is greater than 0.25 times the volume IOPS, an exception is raised with an error message.

        Parameters:
            self (object): The current instance of the class.

        Returns:
            None

        Raises:
            Exception: If any of the validation checks fail.
        """
        if self.ebs_type == "gp3":
            if self.volume_iops is None:
                self.volume_iops = 3000
            elif self.volume_iops > 16000 or self.volume_iops < 3000:
                raise Exception(f"Wrong EBS gp3 iops for {self.region} region. Ensure your EBS gp3 iops is 3000 <= iops <= 16000.")
            else:
                # need to validate the thpt and iops and capacity relationship
                pass
            if self.volume_thpt is None:
                self.volume_thpt = 125
            elif self.volume_thpt > 1000 or self.volume_thpt < 125:
                raise Exception(f"Wrong EBS gp3 thpt for {self.region} region. Ensure your EBS gp3 thpt is 125 <= thpt <= 1000.")
            else:
                # need to validate the thpt and iops and capacity relationship
                pass
            if self.volume_thpt > 0.25 * self.volume_iops:
                raise Exception(f"Wrong EBS gp3 thpt and iops for {self.region} region. Ensure your EBS gp3 thpt is 0.25 * iops <= thpt <= 1000.")
        else:
            if self.volume_iops is not None or self.volume_thpt is not None:
                raise Exception(f"EBS {self.ebs_type} iops and thpt is not supported by this tool. Ensure your EBS {self.ebs_type} iops and thpt is None.")

    def cal_perf_monthly_cost(self, ebs_price_data=cal_config.ebs_price):
        """
        Calculates the monthly cost of EBS performance for a given region and EBS type.
        
        :param ebs_price_data: A dictionary containing EBS price data for different regions and EBS types.
                              Defaults to cal_config.ebs_price.
        :type ebs_price_data: dict
        
        :return: The monthly cost of EBS performance.
        :rtype: float
        
        :raises: Exception if the EBS gp3 iops price unit is not "IOPS-Mo" or the EBS gp3 thpt price unit is not "GiBps-mo".
        """
        if self.region is None:
            return 0
        
        if self.ebs_type == "gp3":
            if ebs_price_data[self.region]["gp3"]['iops_price_unit'] == "IOPS-Mo":
                gp3_iops_price = float(ebs_price_data[self.region]["gp3"]['iops_price_per_unit'])
            else:
                raise Exception(f"Wrong EBS gp3 iops price unit for {self.region} region. Ensure your EBS gp3 iops price unit is IOPS-Mo.")
            if ebs_price_data[self.region]["gp3"]['thpt_price_unit'] == "GiBps-mo":
                gp3_thpt_price = float(ebs_price_data[self.region]["gp3"]['thpt_price_per_unit'])
            else:
                raise Exception(f"Wrong EBS gp3 thpt price unit for {self.region} region. Ensure your EBS gp3 thpt price unit is GiBps-mo.")
            gp3_iops_cost = (self.volume_iops-3000) * gp3_iops_price
            gp3_thpt_cost = (self.volume_thpt-125)/1024 * gp3_thpt_price
            perf_monthly_cost = gp3_iops_cost + gp3_thpt_cost
        else:
            raise Exception(f"EBS performance cost calculation for {self.ebs_type} in {self.region} region is not supported.")
        return perf_monthly_cost

    # the unit collected from AWS is GB-Mo, but we actually think it is GiB-Mo based on AWS doc
    def cal_capacity_monthly_cost(self, ebs_price_data=cal_config.ebs_price):
        if ebs_price_data[self.region][self.ebs_type]["capacity_price_unit"] == "GB-Mo":
            capacity_monthly_cost = self.volume_size * ebs_price_data[self.region][self.ebs_type]["capacity_price_per_unit"]
        else:
            raise Exception(f"Wrong EBS {self.ebs_type} price unit for {self.region} region in the ebs price json file. Ensure your EBS price unit is GB-Mo.")
        return capacity_monthly_cost

    def cal_monthly_cost(self, ebs_price_data=cal_config.ebs_price):
        # currenly only consider gp3 and st1
        if self.ebs_type == "gp3":
            perf_monthly_cost = self.cal_perf_monthly_cost(ebs_price_data)
            capacity_monthly_cost = self.cal_capacity_monthly_cost(ebs_price_data)
        else:
            capacity_monthly_cost = self.cal_capacity_monthly_cost(ebs_price_data)
            perf_monthly_cost = 0
        return capacity_monthly_cost + perf_monthly_cost
        

class EfsStorage:

    global cal_config
    def __init__(self, region: str, storage_type: str, capacity: float):
        self.region = region
        self.storage_type = storage_type # one_zone_storage or standard_storage
        self.capacity = capacity # GiB

    
    # the unit collected from AWS is GB-Mo, but we actually think it is GiB-Mo based on AWS doc
    def cal_efs_monthly_cost(self, efs_price_data=cal_config.efs_price):
        if efs_price_data[self.region][self.storage_type]["unit"] == "GB-Mo":
            price = float(efs_price_data[self.region][self.storage_type]["price"])
            monthly_cost = self.capacity * price 
        else:
            raise Exception(f"Wrong EFS price unit for {self.region} region in the efs price json file. Ensure your EFS size unit is GB-Mo.")
        return monthly_cost

class AwsOnefsNode:
    def __init__(self, onefs_version: str, ec2_instance: Ec2Instance, data_disk: EbsVolume, data_disk_amount: int):
        self.onefs_version = onefs_version
        self.ec2_instance = ec2_instance
        self.data_disk = data_disk
        self.data_disk_amount = data_disk_amount

    def cal_node_raw_capacity(self):
        raw_capcity = self.data_disk_amount * self.data_disk.volume_size # GiB
        return raw_capcity
    
    def cal_node_ec2_hourly_cost(self, ec2_price_data=cal_config.ec2_price):
        node_ec2_hourly_cost = self.ec2_instance.cal_hourly_cost(ec2_price_data)
        return node_ec2_hourly_cost
    
    # EBS vollume size is GiB
    def cal_node_ebs_monthly_cost(self, ec2_price_data=cal_config.ec2_price):
        node_ebs_monthly_cost = self.data_disk_amount * self.data_disk.cal_monthly_cost(ec2_price_data)
        return node_ebs_monthly_cost

# this class contains necessary functions for AWS OneFS cluster cost calculation
class AwsOnefsCluster:
    def __init__(self, region: str, license_contract_term : str, license_discount: float, node: AwsOnefsNode, node_amount: int, drr_ratio: float, protection_level: str):
        self.region = region
        self.license_contract_term  = license_contract_term
        self.license_discount = license_discount
        self.node = node
        self.node_amount = node_amount
        self.drr_ratio = drr_ratio
        self.protection_level = protection_level
        self.validate_cluster_config()
    
    # cluster config should be a suppoted config
    def validate_cluster_config(self):
        pass

    def cal_cluster_raw_capacity(self):
        raw_capcity = self.node_amount * self.node.cal_node_raw_capacity() # GiB
        return raw_capcity

    # currently only support 2n protection level, need to change in the future
    def cal_cluster_usable_capacity(self):
        if self.protection_level == "2n":
            if self.node_amount == 4:
                protection_overhead = 2 / 4
            elif self.node_amount == 5:
                protection_overhead = 2 / 5
            elif self.node_amount == 6:
                protection_overhead = 2 / 6
            usable_capacity = self.node_amount * self.node.cal_node_raw_capacity() * (1 - protection_overhead) # GiB
            return usable_capacity
        else:
            raise Exception("Wrong OneFS protection level. Currently only support 2n protection level.")
        
    # assume the protection level is 2n. 
    # calculate the OneFS cluster usable capacity percentage based on protection overhead.
    # e.g. for a 6 nodes cluster with default 2n protection level, the protection overhead is 33%, thus the available usable capacity is 67% of raw capacity
    def cal_cluster_effective_capacity(self):
        if self.protection_level == "2n":
            if self.node_amount == 4:
                protection_overhead = 2 / 4
            elif self.node_amount == 5:
                protection_overhead = 2 / 5
            elif self.node_amount == 6:
                protection_overhead = 2 / 6
            effective_capacity = self.node_amount * self.node.cal_node_raw_capacity() * (1 - protection_overhead) * self.drr_ratio
        else:
            raise Exception("Wrong OneFS protection level. Currently only support 2n protection level.")
        return effective_capacity
    
    def cal_cluster_ec2_hourly_cost(self, ec2_price_data=cal_config.ec2_price):
        cluster_ec2_hourly_cost = self.node_amount * self.node.cal_node_ec2_hourly_cost(ec2_price_data)
        return cluster_ec2_hourly_cost

    def cal_cluster_ebs_monthly_cost(self, ebs_price_data=cal_config.ebs_price):
        cluster_ebs_monthly_cost = self.node_amount * self.node.data_disk_amount * self.node.data_disk.cal_monthly_cost(ebs_price_data)
        return cluster_ebs_monthly_cost

    def cal_cluster_onefs_monthly_cost(self, onefs_license_price_data=cal_config.onefs_license_price):
        license_contract_term = self.license_contract_term
        onefs_license_discount = self.license_discount
        if license_contract_term == '1-year':
            onefs_monthly_price = onefs_license_price_data[license_contract_term]['price']/12
        elif license_contract_term == '3-years':
            onefs_monthly_price = onefs_license_price_data[license_contract_term]['price']/36
        cluster_onefs_monthly_cost = onefs_monthly_price * self.cal_cluster_raw_capacity() * (1-onefs_license_discount/100)
        return cluster_onefs_monthly_cost
    
    def cal_cluster_solution_monthly_cost(self, ec2_price_data=cal_config.ec2_price, ebs_price_data=cal_config.ebs_price, onefs_license_price_data=cal_config.onefs_license_price):
        cluster_ec2_monthly_cost = self.cal_cluster_ec2_hourly_cost(ec2_price_data) * HOURS_PER_MONTH
        cluster_ebs_monthly_cost = self.cal_cluster_ebs_monthly_cost(ebs_price_data)
        cluster_onefs_monthly_cost = self.cal_cluster_onefs_monthly_cost(onefs_license_price_data)
        cluster_solution_monthly_cost = cluster_ec2_monthly_cost + cluster_ebs_monthly_cost + cluster_onefs_monthly_cost
        return cluster_solution_monthly_cost

# used by AWS sizer, will remove later
def cal_onefs_aws_cost_monthly(aws_region, instance_type, disk_type, node_amount, node_disk_amount, node_disk_size, ec2_payment_option, gp3_iops, gp3_thpt):

    global cal_config
    ec2_instance = Ec2Instance(instance_type, aws_region,ec2_payment_option)
    # remember to convert to GiB for all storage related size
    ebs_volume = EbsVolume(disk_type, aws_region, node_disk_size, volume_iops=gp3_iops, volume_thpt=gp3_thpt)
    single_ec2_instance_hourly_cost = ec2_instance.cal_hourly_cost(cal_config.ec2_price)
    single_ebs_volume_monthly_cost = ebs_volume.cal_monthly_cost(cal_config.ebs_price)
    single_ec2_instance_monthly_cost = HOURS_PER_MONTH * single_ec2_instance_hourly_cost
    onefs_aws_cost_monthly = single_ebs_volume_monthly_cost * node_disk_amount * node_amount + single_ec2_instance_monthly_cost * node_amount
    return onefs_aws_cost_monthly
