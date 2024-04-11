
class AzureSizingRecord:
    def __init__(self, ins_type, node_count, vol_family, vol_type, vol_count, config_msg, burst_msg):
        self.ins_type = ins_type
        self.node_count = node_count
        self.vol_family = vol_family
        self.vol_type = vol_type
        self.vol_count = vol_count
        
        self.config_message = config_msg
        self.burst_message = burst_msg
        self.__price = -1
        
    def SetPrice(self, monthly_cost):        
        self.__price = monthly_cost
    
    def GetPrice(self):
        if self.__price == -1:
            print("Price not initilized.")
        return self.__price