from onefs_sizing.sizing_lib.azure.azure_onefs98_sizer import OneFS98AzureSizer
from azure_tcocal.azure_costcal import AzureOnefsNode, AzureOnefsCluster

def SizeSolutionFromPage(onefs_version,
                         region,
                         cluster_disk_type,
                         data_reduction_ratio, 
                         effecitive_capacity_needed,
                         protection_level,
                         onefs_license_term,
                         vm_payment_option,
                         read_tput_needed, 
                         write_tput_needed,
                         cloud_platform = "Azure"):
    # Process Platform
    if cloud_platform != "Azure":
        print("This page is for Azure sizing only.")
        return []
    else:        
        # Process Version.
        if onefs_version == 'OneFS 9.8':
            sizer = OneFS98AzureSizer()
        else:
            print('Invalid OneFS version.')
            result_row = {'Message': 1, 'Detail': 'OneFS version is not supported by sizing tool yet.'}
            return [result_row]

        if cluster_disk_type == "Standard HDD (not supported yet)":
            result_row = {'Message': 1, 'Detail': 'Sizing for Standard HDD cluster is not supported by sizing tool yet.'}
            return [result_row]
        
        sizing_results= sizer.SizeSequentialWorkload(cluster_disk_type, 
                                                float(data_reduction_ratio), 
                                                float(effecitive_capacity_needed), 
                                                protection_level,
                                                float(read_tput_needed)*1000, 
                                                float(write_tput_needed)*1000)
        
        # Generate table for displaying on web page
        results_for_datatable = []
        
        for sizing_record in sizing_results:
            # Calculate cost for each sizing record
            azure_node = AzureOnefsNode(region, onefs_version, sizing_record.ins_type, sizing_record.vol_type, sizing_record.vol_count)
            azure_cluster = AzureOnefsCluster(onefs_license_term, 
                                              83, 
                                              azure_node, 
                                              sizing_record.node_count, 
                                              data_reduction_ratio,
                                              protection_level
                                              )
            if vm_payment_option.lower() == "pay as you go":
                cluster_vm_monthly_cost = azure_cluster.cal_cluster_vm_monthly_cost_pay_as_you_go()
            elif vm_payment_option.lower() == "savings plan":
                cluster_vm_monthly_cost = azure_cluster.cal_cluster_vm_monthly_cost_savings_plan(saving_plan_term=onefs_license_term)
                
            cluster_disk_monthly_cost = azure_cluster.cal_cluster_disk_monthly_cost_pay_as_you_go()
            cluster_onefs_license_cost = azure_cluster.cal_cluster_onefs_license_monthly_cost()
            cluster_monthly_cost = cluster_vm_monthly_cost + cluster_disk_monthly_cost + cluster_onefs_license_cost
            sizing_record.SetPrice(cluster_monthly_cost)
            
            effecitive_capacity = azure_cluster.cal_cluster_effective_capacity()
            effecitive_capacity_monthly_cost = round(cluster_monthly_cost / effecitive_capacity)
            
            record_dict = {'Node Instance Type': sizing_record.ins_type,
                        'Cluster Node Count': sizing_record.node_count,
                        'Volumn Type': sizing_record.vol_type,
                        'Volumn Count Per Node': sizing_record.vol_count,
                        'Total Monthly Cost (USD)': int(sizing_record.GetPrice()),
                        'Usable Capacity Monthly Cost(USD/TiB)': effecitive_capacity_monthly_cost,
                        'Config Info': sizing_record.config_message,
                        'Burst Info (every 24 hours)': sizing_record.burst_message}            
            results_for_datatable.append(record_dict)    
        
        sorted_results_for_datatable = list(sorted(results_for_datatable, key=lambda item:item['Total Monthly Cost (USD)']))
            
        return sorted_results_for_datatable
