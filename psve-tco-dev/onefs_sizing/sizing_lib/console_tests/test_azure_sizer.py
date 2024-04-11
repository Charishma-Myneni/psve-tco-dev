import sys
import os

# Check the system path of python, make sure it contains the project root directory.
current_path = os.getcwd()

if current_path not in sys.path:
    sys.path.insert(0, current_path)

from onefs_sizing.sizing_lib.azure.azure_onefs98_sizer import OneFS98AzureSizer

def test_azure_sizing():
    onefs98_sizer = OneFS98AzureSizer()
    
    # User input fields
    workload = "Random or Steady Sequential" # "Archive" or "General Sequential" or "Random or Steady Sequential"
    data_reduction_ratio = 1.0
    effecitive_capacity_needed = 180 # TiB
    read_tput_needed = 3000 # MB/sec
    write_tput_needed = 1000 # MB/sec
    protection_level = "+2d:1n" # Or "+2n"
    
    sizing_results= onefs98_sizer.SizeSequentialWorkload(workload, 
                                                data_reduction_ratio, 
                                                effecitive_capacity_needed, 
                                                protection_level,
                                                read_tput_needed, 
                                                write_tput_needed)
    
    # Generate table for displaying on web page
    results_for_datatable = []

    for sizing_record in sizing_results:    
        annual_cost = round(sizing_record.GetPrice(),1)
        record_dict = {
            'Instance Type': sizing_record.ins_type,
            'Node': sizing_record.node_count,
            'Vol.Family': sizing_record.vol_family,
            'Vol.Type': sizing_record.vol_type,
            'Vol.Count': sizing_record.vol_count,
            'Annual Cost': annual_cost,
            'Config Info': sizing_record.config_message,
            'Burst Info': sizing_record.burst_message
            }
        
        results_for_datatable.append(record_dict)
        
        sorted_results_for_datatable = list(sorted(results_for_datatable, key=lambda item:item['Annual Cost']))
    
    for record in sorted_results_for_datatable:
        record['Annual Cost'] = "$" + str(record['Annual Cost'])
        
    return sorted_results_for_datatable

sizing_results = test_azure_sizing()
sr_index = 1
for sizing_result in sizing_results:
    print("=============")
    print(f"No.{sr_index}, {sizing_result['Instance Type']}, ", end="")
    print(f"{sizing_result['Node']} nodes, {sizing_result['Vol.Family']}, ", end="")
    print(f"{sizing_result['Vol.Type']}, {sizing_result['Vol.Count']} disks, ", end="")
    print(f"{sizing_result['Annual Cost']}.")
    print(f"{sizing_result['Config Info']}")
    print(f"{sizing_result['Burst Info']}")
    sr_index += 1