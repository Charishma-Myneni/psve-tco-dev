from onefs_sizing.sizing_lib.aws.aws_onefs97_sizer import OneFS97AWSSizer
from onefs_sizing.sizing_lib.aws.aws_onefs96_sizer import OneFS96AWSSizer
from onefs_sizing.sizing_lib.aws.ec2_region_data import EC2RegionData

def SizeSolutionFromPage(onefs_version,
                         region,
                         workload,
                         data_reduction_ratio, 
                         effecitive_capacity_needed,
                         read_tput_needed, 
                         write_tput_needed,
                         cloud_platform = "AWS"):
    # Process Platform
    if cloud_platform != "AWS":
        print("Sizer don't support cloud platforms other than AWS yet.")
        return []
    else:        
        # Process Version.
        if onefs_version == 'OneFS 9.7':
            sizer = OneFS97AWSSizer()
        elif onefs_version == 'OneFS 9.6':
            sizer = OneFS96AWSSizer()
        else:
            print('Invalid OneFS version found.')
            return ["Invalid OneFS version"]

        ec2_region_data = EC2RegionData()
        
        sizing_results= sizer.SizeSequentialWorkload(workload, 
                                                float(data_reduction_ratio), 
                                                float(effecitive_capacity_needed), 
                                                float(read_tput_needed), 
                                                float(write_tput_needed))
    
        filter_region_results = []        
        for record in sizing_results:
            if ec2_region_data.IsInstanceSupportedInRegion(record.ins_type, region):
                filter_region_results.append(record) 
            
        # Generate table for displaying on web page
        results_for_datatable = []
        
        for sizing_record in filter_region_results:                
            if sizing_record.vol_type == 'st1':
                # Set the iops a string.
                record_dict = {'No.': 0,
                            'Instance Type': sizing_record.ins_type,
                            'Nodes': sizing_record.node_count,
                            'VolTyp': sizing_record.vol_type,
                            'VolCnt': sizing_record.vol_count,
                            'VolSize': f"{round(sizing_record.vol_size,1)} TiB",
                            'VolTput': f"{round(sizing_record.vol_config_tput,1)} MB/sec",
                            'VolIOPS': "N/A for st1",
                            'Total Annual Cost': sizing_record.GetPrice(),
                            'Config Info': sizing_record.message}
            else:
                # Set the iops an integer.            
                record_dict = {'No.': 0,
                            'Instance Type': sizing_record.ins_type,
                            'Nodes': sizing_record.node_count,
                            'VolTyp': sizing_record.vol_type,
                            'VolCnt': sizing_record.vol_count,
                            'VolSize': f"{round(sizing_record.vol_size,1)} TiB",
                            'VolTput': f"{round(sizing_record.vol_config_tput,1)} MB/sec",
                            'VolIOPS': int(sizing_record.vol_config_iops),
                            'Total Annual Cost': sizing_record.GetPrice(),
                            'Config Info': sizing_record.message}
            
            results_for_datatable.append(record_dict)
        
        sorted_results_for_datatable = list(sorted(results_for_datatable, key=lambda item:item['Total Annual Cost']))
        
        rcd_index = 0
        for row in sorted_results_for_datatable:
            rcd_index += 1
            row["No."] = rcd_index
            cost_float = row["Total Annual Cost"]
            cost_str = "${:,}".format(int(cost_float))
            row["Total Annual Cost"] = cost_str
            
        return sorted_results_for_datatable
