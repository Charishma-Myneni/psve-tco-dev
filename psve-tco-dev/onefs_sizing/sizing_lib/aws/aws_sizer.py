from onefs_sizing.sizing_lib.common.cloud_sizer import CloudSizer
from onefs_sizing.sizing_lib.aws.aws_supported_config import AwsSupportedConfig
from onefs_sizing.sizing_lib.aws.aws_perf_data import AwsPerfData
from onefs_sizing.sizing_lib.aws.aws_sizing_record import AwsSizingRecord
from onefs_sizing.sizing_lib.common.logger_utils import logger

from typing import List
import re
import math

class AWSSizer(CloudSizer):
    def __init__(self, supported_config: AwsSupportedConfig, perf_data: AwsPerfData):
        self.perf_data = perf_data
        self.supported_config = supported_config

    # Core sizing logic is implemented here.
    def SizeSequentialWorkload(self, workload, drr_ratio, data_app_capacity, read_tput_requirement, write_tput_requirement):
                       
        # Calculate the Usable Capacity, aka 'Preprotected Physical'
        usable_size = data_app_capacity / drr_ratio

        # Determine volume type based on workload
        if workload == "Archive":
            # vol_type = "st1"
            valid_sizing_records = self.SizeSt1Solutions(usable_size, read_tput_requirement, write_tput_requirement)
        elif workload == "General":
            # vol_type = "gp3"
            valid_sizing_records = self.SizeGp3Solutions(usable_size, read_tput_requirement, write_tput_requirement)

        return valid_sizing_records
    
    
    def SizeGp3VolumePerfConfig(self, inst_type, vol_count):
        """
        Calculates the performance configuration for a GP3 volume based on the instance type and volume count.

        Parameters:
            inst_type (str): The instance type.
            vol_count (int): The number of volumes.

        Returns:
            dict: A dictionary containing the throughput and IOPS configuration for the volume.
        """
        # Per node read perf should be smaller than EBS limit
        per_node_read_perf = self.perf_data.GetInstanceReadPerf("gp3", inst_type)
        vol_perf_config_by_ebs = self.supported_config.GetInstanceEBSLimit(inst_type)
        
        if per_node_read_perf > vol_perf_config_by_ebs:
            logger.debug("Per node read throughput in test result should not be higher than EBS bandwidth limit.")
        
        per_vol_tput_by_test = math.ceil(per_node_read_perf / vol_count)
        
        if per_vol_tput_by_test <= 125:
            per_vol_tput_by_test = 125
        elif per_vol_tput_by_test > 1000:
            logger.debug("AWS does not support gp3 volumes with 1000+ MB/sec/volume.")
            return None

        volume_perf_config = {}
        volume_perf_config["tput"] = per_vol_tput_by_test

        # AWS saied: "The maximum ratio of provisioned throughput to provisioned IOPS is .25 MiB/s per IOPS"
        # That is: iops * 0.25 = tput
        ebs_vol_iops = per_vol_tput_by_test / 0.25
        if ebs_vol_iops < 3000:
            ebs_vol_iops = 3000
        
        volume_perf_config["iops"] = ebs_vol_iops

        return volume_perf_config

    def SizeGp3Solutions(self, usable_size, read_tput_requirement, write_tput_requirement):        
        # Sizing result list
        valid_sizing_records: List[AwsSizingRecord] = []
        
        # Iterate all supported instance families
        for family, inst_list in self.supported_config.instance_families.items():
            # Iterate all supported instance types
            for inst_type in inst_list:
                # Get the per-node instance type read and write performance number
                per_node_read_perf = self.perf_data.GetInstanceReadPerf("gp3", inst_type)
                per_node_write_perf = self.perf_data.GetInstanceWritePerf("gp3", inst_type)

                # Iterate all supported node count
                for node_count in self.supported_config.node_count:
                    # See if read perf works for this volume-type, instance-type, node-count
                    if per_node_read_perf * node_count >= read_tput_requirement:
                        sastify_read = True
                    else:
                        sastify_read = False

                    # See if write perf works for this volume-type, instance-type, node-count
                    if per_node_write_perf * node_count >= write_tput_requirement:
                        sastify_write = True
                    else:
                        sastify_write = False
                    
                    if sastify_read and sastify_write:                
                        # Get the efficiency of this node count of "+2n"
                        efficiency = self.supported_config.efficiency[str(node_count)]
                        raw_capacity = usable_size / efficiency
                        per_node_capacity = raw_capacity / node_count

                        vol_min_capacity = self.supported_config.volume_types["gp3"]["volume-min-size-tib"]
                        vol_max_capacity = self.supported_config.volume_types["gp3"]["volume-max-size-tib"]
                        
                        # Get the per volume capacity of every supported per-node volume count
                        volume_count_list = self.supported_config.GetSupportedVolumeCount("gp3")

                        for vol_count in volume_count_list:
                            vol_size = per_node_capacity / vol_count
                            if vol_size >= vol_min_capacity and vol_size <= vol_max_capacity:
                                #Determine the performance config of each gp3 volume
                                vol_perf_config = self.SizeGp3VolumePerfConfig(inst_type, vol_count)
                                if vol_perf_config is not None:
                                    # Set the config ability message.
                                    message = "Read up to: {:d} MB/s, Write up to: {:d} MB/s, Raw capacity: {:d} TB".format(
                                        int(per_node_read_perf * node_count), 
                                        int(per_node_write_perf * node_count), 
                                        int(vol_size * vol_count * node_count))
                                    
                                    sizing_record = AwsSizingRecord(inst_type, 
                                                                node_count, 
                                                                "gp3", 
                                                                vol_count, 
                                                                vol_size,
                                                                message,
                                                                vol_perf_config["tput"],
                                                                vol_perf_config["iops"])
                                    valid_sizing_records.append(sizing_record)
                                else:
                                    continue
                            elif vol_size < vol_min_capacity and vol_count == min(volume_count_list):
                                # Even the smallest volume count still leads to capacity smaller than 1 TiB, use 1 TiB instead.
                                logger.debug("Warning: capacity requirement is too small. Will use the minimal valid sizing record.")
                                
                                message = "Read up to: {:d} MB/s, Write up to: {:d} MB/s, Raw capacity: {:d} TB".format(
                                int(per_node_read_perf * node_count), 
                                int(per_node_write_perf * node_count), 
                                int(vol_min_capacity * vol_count * node_count))
                                
                                vol_perf_config = self.SizeGp3VolumePerfConfig(inst_type, vol_count)
                                if vol_perf_config is not None:
                                    sizing_record = AwsSizingRecord(inst_type, 
                                                                node_count, 
                                                                "gp3", 
                                                                vol_count, 
                                                                vol_min_capacity,
                                                                message,
                                                                vol_perf_config["tput"],
                                                                vol_perf_config["iops"])
                                    valid_sizing_records.append(sizing_record)
                            elif vol_size > vol_max_capacity and vol_count == max(volume_count_list):
                                logger.debug("Warning: capacity requirment is too large. Can't support it.")
                    else:
                        # read or write performance requirement not sastified by this instance type and node count
                        continue
        
        return valid_sizing_records    
    
    def SizeSt1Solutions(self, usable_size, read_tput_requirement, write_tput_requirement):
        # Sizing result list
        valid_sizing_records: List[AwsSizingRecord] = [] 
        for family, inst_list in self.supported_config.instance_families.items():
            # Iterate all supported st1 disk count and disk capacity configs
            for config in ["5d4t", "6d4t", "5d10t", "6d10t"]:
                pattern_cfg = r'(\d+)d(\d+)t'
                match = re.match(pattern_cfg, config)
                if match:
                    vol_count = int(match.group(1))
                    vol_size = int(match.group(2))
                else:
                    print("Wrong supported st1 disk count and capacity config:", config)
                
                # Iterate all supported instance types
                for inst_type in inst_list:
                    # Get the per-node instance type read and write performance number
                    per_node_read_perf = self.perf_data.GetInstanceReadPerf("st1", inst_type, config)
                    per_node_write_perf = self.perf_data.GetInstanceWritePerf("st1", inst_type, config)

                    # Skipping the instance types that are not appropriate for st1 cluster
                    if per_node_read_perf is None or per_node_write_perf is None:
                        continue

                    # Iterate all supported node count
                    for node_count in self.supported_config.node_count:
                        # See if read perf works for this volume-type, instance-type, node-count
                        if per_node_read_perf * node_count >= read_tput_requirement:
                            sastify_read = True
                        else:
                            sastify_read = False

                        # See if write perf works for this volume-type, instance-type, node-count
                        if per_node_write_perf * node_count >= write_tput_requirement:
                            sastify_write = True
                        else:
                            sastify_write = False
                        
                        if sastify_read and sastify_write:                
                            # Get the efficiency of this node count of "+2n"
                            efficiency = self.supported_config.efficiency[str(node_count)]
                            raw_capacity = usable_size / efficiency
                            per_node_capacity = raw_capacity / node_count                            
                            
                            if per_node_capacity > vol_count * vol_size:
                                # Not enough capacity to meet the requirement
                                logger.debug("Warning: capacity requirement is too large. Can't support it.")
                                continue
                            else:                                
                                message = "Read up to: {:d} MB/s, Write up to: {:d} MB/s, Raw capacity: {:d} TB".format(
                                int(per_node_read_perf * node_count), 
                                int(per_node_write_perf * node_count), 
                                int(vol_size * vol_count * node_count))
                                
                                # Instance Type, node count, disk type, disk count, disk capacity all settled
                                sizing_record = AwsSizingRecord(inst_type, 
                                                            node_count, 
                                                            "st1", 
                                                            vol_count, 
                                                            vol_size,
                                                            message)
                                valid_sizing_records.append(sizing_record)
                                    
        return valid_sizing_records
