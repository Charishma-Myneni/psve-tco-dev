from onefs_sizing.sizing_lib.common.logger_utils import logger
import json
from tcocal.costcal import cal_onefs_aws_cost_monthly
from onefs_sizing.sizing_lib.aws.ec2_region_data import EC2RegionData

# Size the gp3 volume setting of tput and iops according to instance type EBS bandwidth limit
def GetGp3PerfConfigByEbsLimit(inst_type, vol_count, ebs_limit_data):
    ebs_limit = ebs_limit_data[inst_type]    
    ebs_vol_tput = ebs_limit / vol_count
    if ebs_vol_tput <= 125:
        ebs_vol_tput = 125
    elif ebs_vol_tput > 1000:
        logger.debug(f"Instance type: {inst_type}, EBS limit: {ebs_limit} MB/sec, Volume count is {vol_count}, AWS does not support gp3 volumes with 1000+ MB/sec/volume.")
        return None

    volume_perf_config = {}
    volume_perf_config["tput"] = ebs_vol_tput

    # AWS saied: "The maximum ratio of provisioned throughput to provisioned IOPS is .25 MiB/s per IOPS"
    # That is: iops * 0.25 = tput
    ebs_vol_iops = ebs_vol_tput / 0.25
    if ebs_vol_iops < 3000:
        ebs_vol_iops = 3000
    
    volume_perf_config["iops"] = ebs_vol_iops

    return volume_perf_config

# Get EBS bandwidth limit of this instance type
# Will update this method to use AWS API to query info in later version
def QueryAllSupporedInstanceEbsLimit(inst_types: list):
    inst_type_ebs_limits = {}
    # This is a temp solution, treat this dict as AWS data source
    ebs_limit_path = 'onefs_sizing/raw_data/aws/instance_ebs_limit_2024_jan.json'
    with open(ebs_limit_path, 'r') as ebs_limit_file:
        ebs_limit_data_from_file = json.load(ebs_limit_file)
    
    # Load limit for each instance type
    for inst_type in inst_types:
        ebs_limit = ebs_limit_data_from_file[inst_type]
        inst_type_ebs_limits[inst_type] = ebs_limit
        
    return inst_type_ebs_limits

# Call TcoCalculator's method to calculate the price for each solution config
def GetAwsSolutionMonthlyPrice(aws_region, instance_type, disk_type, 
                               node_amount, node_disk_amount, node_disk_size, 
                               ec2_payment_option, gp3_iops, gp3_thpt):
    monthly_cost = cal_onefs_aws_cost_monthly(aws_region, instance_type, disk_type, 
                                      node_amount, node_disk_amount, node_disk_size * 1024, 
                                      ec2_payment_option, gp3_iops, gp3_thpt)
    return monthly_cost

def GetAwsTotalSolutionAnnualPrice(aws_region, instance_type, disk_type, 
                               node_amount, node_disk_amount, node_disk_size, 
                               ec2_payment_option, gp3_iops, gp3_thpt):
    annual_cost = 12 * GetAwsSolutionMonthlyPrice(aws_region, instance_type, disk_type, 
                                      node_amount, node_disk_amount, node_disk_size, 
                                      ec2_payment_option, gp3_iops, gp3_thpt)
    return annual_cost

def FilterOutAwsSizingRecordOnRegion(sizing_records, aws_region):  
    ec2_region_data = EC2RegionData()
    filter_region_results = []        
    for record in sizing_records:
        if ec2_region_data.IsInstanceSupportedInRegion(record.ins_type, aws_region):
            filter_region_results.append(record)    
    return filter_region_results
