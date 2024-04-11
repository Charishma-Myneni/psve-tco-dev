from onefs_sizing.sizing_lib.common.cloud_sizer import CloudSizer
from onefs_sizing.sizing_lib.azure.azure_supported_config import AzureSupportedConfig
from onefs_sizing.sizing_lib.azure.azure_perf_data import AzurePerfData
from onefs_sizing.sizing_lib.azure.utilities import AzureUtility
from onefs_sizing.sizing_lib.azure.azure_sizing_record import AzureSizingRecord

import math

class AzureSizer(CloudSizer):
    def __init__(self, supported_config: AzureSupportedConfig, perf_data: AzurePerfData):
        self.perf_data = perf_data
        self.supported_config = supported_config
        self.sizer_utility = AzureUtility()
    
    def SizeSequentialWorkload(self, cluster_disk_type, drr_ratio, data_app_capacity, protection_level, read_tput_requirement, write_tput_requirement):
        # Calculate the Usable Capacity, aka 'Preprotected Physical'
        usable_size = data_app_capacity / drr_ratio

        # Determine volume type based on workload
        if cluster_disk_type == "Standard HDD":
            # vol_type = "Standard_HDD"
            # inst_type = ddv5 or edv5
            valid_sizing_records = self.SizeStdHddSolutions(usable_size, protection_level, read_tput_requirement, write_tput_requirement)
        elif cluster_disk_type == "Standard SSD":
            # vol_type = "Standard_SSD"
            # inst_type = ddsv5
            valid_sizing_records = self.SizeStdSsdSolutions(usable_size, protection_level, read_tput_requirement, write_tput_requirement)
        elif cluster_disk_type == "Premium SSD":
            # vol_type = "Premium_SSD"
            # inst_type = edsv5
            valid_sizing_records = self.SizePremSsdSolutions(usable_size, protection_level, read_tput_requirement, write_tput_requirement)
        else:
            print("Invalid workload")
            return None

        return valid_sizing_records
    
    def SizePremSsdSolutions(self, usable_size, protection_level, read_tput_requirement, write_tput_requirement):
        sizing_records = []
        instance_types = self.supported_config.instance_families["edsv5"]
        data_disk_types = self.supported_config.volume_types["premium-ssd"]
        supported_disk_counts = self.supported_config.data_disk_counts
        node_counts = self.supported_config.node_count
        
        for inst_type in instance_types:
            for nc in node_counts:
                # Size the seq read/write performance
                read_perf_per_node = self.perf_data.GetReadPerf("edsv5", inst_type, nc)
                write_perf_per_node = self.perf_data.GetWritePerf("edsv5", inst_type, nc, protection_level)
                cluster_read_tput = read_perf_per_node * int(nc)
                cluster_write_tput = write_perf_per_node * int(nc)
                
                if cluster_read_tput < read_tput_requirement or cluster_write_tput < write_tput_requirement:
                    # Read or Write performance requirement not met, try next node count
                    continue
                else:
                    # Performance requirement met, size the capacity next
                    efficiency = self.supported_config.efficiency[protection_level][str(nc)]
                    raw_capacity = usable_size / efficiency
                    
                    # If the input capacity is too small for the lowest disk type, use the minimum capacity
                    raw_too_small = self.supported_config.RawCapacitySmallerThanSupportedDiskType("premium-ssd", raw_capacity)
                    if raw_too_small:
                        raw_capacity = self.supported_config.minimum_cluster_size_tib["premium-ssd"]
                    
                    for dt in data_disk_types:                        
                        # Find all the disk count can sastify the capacity requirement.
                        disk_size_config = self.sizer_utility.GetDiskSize("premium-ssd", dt)
                        per_node_disk_count = math.ceil(raw_capacity / int(nc) / disk_size_config)
                        
                        if per_node_disk_count > supported_disk_counts[-1]:
                            # Requires more disk count of this disk type than supported, try next disk type
                            continue
                        for i_dc in supported_disk_counts:
                            if i_dc < per_node_disk_count:
                                # Not enough disks to sastify the capacity requirement, try next disk count
                                continue
                            else:
                                # Capacity is sastified, confirm the aggretated disk throughput is larger than the instance read tput limit
                                aggregated_disk_tput = self.sizer_utility.GetPremSsdDiskTput(dt) * i_dc
                                if aggregated_disk_tput < read_perf_per_node:
                                    # Disk count is not enough to make aggregated disk throughput bigger than read tput limit
                                    # Try next supported disk count
                                    continue
                                else:   
                                    # Here, we've found a combination of disk type and disk count
                                    # Next, we need to check if the total capacity fall within the supported config of "protection level + capacity"
                                    disk_size = self.sizer_utility.GetDiskSize("premium-ssd", dt)
                                    cluster_total_capacity = disk_size * i_dc * int(nc)
                                    dt_valid = self.supported_config.ValidDataDiskType("premium-ssd", dt, cluster_total_capacity, protection_level)                                    
                                    if not dt_valid:
                                        # Raw capacity too small or too large for this disk type, try next data disk count
                                        continue
                                    else:                                         
                                        # Finally, we have a valid configuration:
                                        # 1. User input Read and write performance requirement met
                                        # 2. Aggregated disk throughput is larger than the instance read tput limit (bottleneck not on data disks)
                                        # 3. User input capacity requirement met
                                        # 3. The total capacity is within the supported config of "protection level + capacity"
                                        burst_msg = self.GetBurstMessage(inst_type, nc, read_perf_per_node)
                                        
                                        config_msg = "Read up to: {:.1f} GB/s, Write up to: {:.1f} GB/s, Raw Capacity: {:d} TiB.".format(
                                            read_perf_per_node * int(nc) / 1000, 
                                            write_perf_per_node * int(nc) / 1000, 
                                            int(cluster_total_capacity))                        
                                    
                                        sr = AzureSizingRecord(inst_type, nc, "premium-ssd", dt, i_dc, config_msg, burst_msg)                                        
                                        sizing_records.append(sr)
        
        return sizing_records
    
    def SizeStdSsdSolutions(self, usable_size, protection_level, read_tput_requirement, write_tput_requirement):
        sizing_records = []
        instance_types = self.supported_config.instance_families["ddsv5"]
        data_disk_types = self.supported_config.volume_types["standard-ssd"]
        supported_disk_counts = self.supported_config.data_disk_counts
        node_counts = self.supported_config.node_count
        
        for inst_type in instance_types:
            for nc in node_counts:
                # Size the seq read/write performance
                read_perf_per_node = self.perf_data.GetReadPerf("ddsv5", inst_type, nc)
                write_perf_per_node = self.perf_data.GetWritePerf("ddsv5", inst_type, nc, protection_level)
                cluster_read_tput = read_perf_per_node * int(nc)
                cluster_write_tput = write_perf_per_node * int(nc)
                
                if cluster_read_tput < read_tput_requirement or cluster_write_tput < write_tput_requirement:
                    # Read or Write performance requirement not met, try next node count
                    continue
                else:
                    # Performance requirement met, size the capacity next
                    efficiency = self.supported_config.efficiency[protection_level][str(nc)]
                    raw_capacity = usable_size / efficiency
                    
                    # If the input capacity is too small for the lowest disk type, use the minimum capacity
                    raw_too_small = self.supported_config.RawCapacitySmallerThanSupportedDiskType("standard-ssd", raw_capacity)
                    if raw_too_small:
                        raw_capacity = self.supported_config.minimum_cluster_size_tib["standard-ssd"]
                    
                    for dt in data_disk_types:                        
                        # Find all the disk count can sastify the capacity requirement.
                        disk_size_config = self.sizer_utility.GetDiskSize("standard-ssd", dt)
                        per_node_disk_count = math.ceil(raw_capacity / int(nc) / disk_size_config)
                        
                        if per_node_disk_count > supported_disk_counts[-1]:
                            # Requires more disk count of this disk type than supported, try next disk type
                            continue
                        for i_dc in supported_disk_counts:
                            if i_dc < per_node_disk_count:
                                # Not enough disks to sastify the capacity requirement, try next disk count
                                continue
                            else:
                                # Capacity is sastified, confirm the aggretated disk throughput is larger than the instance read tput limit
                                aggregated_disk_tput = self.sizer_utility.GetStdSsdDiskTput(dt) * i_dc
                                if aggregated_disk_tput < read_perf_per_node:
                                    # Disk count is not enough to make aggregated disk throughput bigger than read tput limit
                                    # Try next supported disk count
                                    continue
                                else:   
                                    # Here, we've found a combination of disk type and disk count
                                    # Next, we need to check if the total capacity fall within the supported config of "protection level + capacity"
                                    disk_size = self.sizer_utility.GetDiskSize("standard-ssd", dt)
                                    cluster_total_capacity = disk_size * i_dc * int(nc)
                                    dt_valid = self.supported_config.ValidDataDiskType("standard-ssd", dt, cluster_total_capacity, protection_level)                                    
                                    if not dt_valid:
                                        # Raw capacity too small or too large for this disk type, try next data disk count
                                        continue
                                    else:                                         
                                        # Finally, we have a valid configuration:
                                        # 1. User input Read and write performance requirement met
                                        # 2. Aggregated disk throughput is larger than the instance read tput limit (bottleneck not on data disks)
                                        # 3. User input capacity requirement met
                                        # 3. The total capacity is within the supported config of "protection level + capacity"
                                        burst_msg = self.GetBurstMessage(inst_type, nc, read_perf_per_node)
                                        
                                        config_msg = "Read up to: {:.1f} GB/s, Write up to: {:.1f} GB/s, Raw Capacity: {:d} TiB.".format(
                                            read_perf_per_node * int(nc) / 1000, 
                                            write_perf_per_node * int(nc) / 1000, 
                                            int(disk_size * i_dc * int(nc)))                        
                                    
                                        sr = AzureSizingRecord(inst_type, nc, "standard-ssd", dt, i_dc, config_msg, burst_msg)                                        
                                        sizing_records.append(sr)
        
        return sizing_records
    
    def SizeStdHddSolutions(self, usable_size, protection_level, read_tput_requirement, write_tput_requirement):
        instance_types = self.supported_config.instance_families["ddv5"]
        instance_types.extend(self.supported_config.instance_families["edv5"])
        data_disk_types = self.supported_config.volume_types["standard-hdd"]
        
        return None
    
    def GetBurstMessage(self, inst_type, node_count, read_tput):
        
        base_bw = self.sizer_utility.GetInstanceTypeBaseBwLimits(inst_type)
        burst_bw = self.sizer_utility.GetInstanceTypeBurstLimits(inst_type)
        
        if burst_bw == base_bw or burst_bw < read_tput or read_tput < base_bw:
            return "No burst impact for this configuration."
        
        # Burst credit is the data amount of max burst throughput keep running for 30 minutes, unit is MB
        total_burst_credit = (burst_bw - base_bw) * 30 * 60
        
        # Calculate the max burst credit burning speed, unit is MB/minute
        burst_credit_deplete_per_minute = (read_tput - base_bw) * 60
        
        # Total time that the burst credit is burning at the max throughput, unit is minute
        burst_time_last = total_burst_credit / burst_credit_deplete_per_minute
        
        if burst_time_last > 24 * 60:
            return "Burst time can last more than 24 hours. No burst impact for this configuration."
        
        cluster_burst_tput = read_tput * int(node_count)
        cluster_no_burst_tput = base_bw * int(node_count)
        
        if burst_time_last < 0:
            raise ValueError("Burst time should not be less than 0.")
        
        return "Max burst: {:.1f} hours; Max bursting perf: {:.1f} GB/s; No burst: {:.1f} GB/s".format(
            burst_time_last/60, 
            cluster_burst_tput/1000,
            cluster_no_burst_tput/1000)
