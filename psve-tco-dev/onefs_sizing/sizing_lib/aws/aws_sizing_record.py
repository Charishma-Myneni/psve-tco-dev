from onefs_sizing.sizing_lib.aws.aws_perf_data import AwsPerfData
from onefs_sizing.sizing_lib.aws.utilities import GetAwsTotalSolutionAnnualPrice

# This is a class represent one sizing result.
# It contains: instance type, cluster node count, volume type, volume count per node, volume size, volume perf config.
class AwsSizingRecord:
    def __init__(self, ins_type, node_count, vol_type, vol_count, vol_size, max_perf_message, vol_config_tput=125, vol_config_iops=3000):
        self.ins_type = ins_type
        self.node_count = node_count
        self.vol_type = vol_type
        self.vol_count = vol_count
        self.vol_size = vol_size
        
        if vol_type == "st1":
            self.vol_config_tput = vol_size * 40
            self.vol_config_iops = -1
        elif vol_type == "gp3":
            self.vol_config_tput = vol_config_tput
            self.vol_config_iops = vol_config_iops
        else:
            raise ValueError("Unsupported volume type: " + vol_type)

        self.message = max_perf_message

        self.aggregated_ebs_bandwidth = self.vol_config_tput * self.vol_count
        self.__price = -1

    def __lt__(self, other):
        return self.GetPrice() < other.GetPrice()

    def GetClusterReadThroughput(self, perf_data: AwsPerfData):                  
        per_node_read = perf_data.GetInstanceReadPerf(self.vol_type, self.ins_type)
        return per_node_read * self.node_count

    def GetClusterWriteThroughput(self, perf_data: AwsPerfData):
        per_node_write = perf_data.GetInstanceWritePerf(self.vol_type, self.ins_type)
        return per_node_write * self.node_count
      
    def SetPrice(self, region, payment_option):
        self.__price = GetAwsTotalSolutionAnnualPrice(region, self.ins_type, self.vol_type,
                                                  self.node_count, self.vol_count, self.vol_size,
                                                  payment_option, self.vol_config_iops, 
                                                  self.vol_config_tput)
    
    def GetPrice(self, region="us-east-1", payment_option="on-demand"):
        if self.__price == -1:
            self.SetPrice(region, payment_option)
        return self.__price
    
    