import sys
import os

# Check the system path of python, make sure it contains the project root directory.
current_path = os.getcwd()

if current_path not in sys.path:
    sys.path.insert(0, current_path)

from onefs_sizing.sizing_lib.aws.aws_onefs97_sizer import OneFS97AWSSizer
from onefs_sizing.sizing_lib.aws.ec2_region_data import EC2RegionData
from onefs_sizing.sizing_lib.aws.aws_sizing_record import AwsSizingRecord

def test_aws_sizing():
    # Init OneFS 9.7 sizer object
    onefs97_sizer = OneFS97AWSSizer()

    # User input fields
    workload = "Archive"
    data_reduction_ratio = 1.0
    effecitive_capacity_needed = 180 # TiB
    read_tput_needed = 3000 # MB/sec
    write_tput_needed = 1000 # MB/sec
    
    # Example of other options: us-east-1, us-west-2, eu-west-1, ap-northeast-1, etc.
    region = "me-south-1"
    
    ec2_region_data = EC2RegionData()

    sizing_results= onefs97_sizer.SizeSequentialWorkload(workload, 
                                                data_reduction_ratio, 
                                                effecitive_capacity_needed, 
                                                read_tput_needed, 
                                                write_tput_needed)
    
    filter_region_results = []        
    for record in sizing_results:
        if ec2_region_data.IsInstanceSupportedInRegion(record.ins_type, region):
            filter_region_results.append(record) 
         
    # Generate table for displaying on web page
    results_for_datatable = []
    
    for sizing_record in filter_region_results:                
        record_dict = {'No.': 0,
                       'Instance Type': sizing_record.ins_type,
                       'Node': sizing_record.node_count,
                       'Vol.Type': sizing_record.vol_type,
                       'Vol.Count': sizing_record.vol_count,
                       'Vol.Size': f"{round(sizing_record.vol_size,1)} TiB",
                       'Vol.Tput': f"{round(sizing_record.vol_config_tput,1)} MB/sec",
                       'Volume IOPS': int(sizing_record.vol_config_iops),
                       'Annual Cost': f"{round(sizing_record.GetPrice(),1)} $/year",
                       'More Info': sizing_record.message
                        }
        
        results_for_datatable.append(record_dict)
    
    sorted_results_for_datatable = list(sorted(results_for_datatable, key=lambda item:item['Annual Cost']))
    
    rcd_index = 0
    for row in sorted_results_for_datatable:
        rcd_index += 1
        row["No."] = rcd_index
        
    return sorted_results_for_datatable

print(test_aws_sizing())

def test_aws_sizing_record_cost():
    sizing_record = AwsSizingRecord("m6idn.8xlarge", 
                                    4,
                                    "gp3",
                                    12,
                                    2.1 * 1024,
                                    "Test message",
                                    125,
                                    3000)
    price = sizing_record.GetPrice()
    print(price)
    
#test_aws_sizing_record_cost()