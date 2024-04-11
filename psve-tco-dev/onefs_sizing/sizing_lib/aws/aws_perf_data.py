import json

class AwsPerfData:
    def __init__(self, perf_data_path):
        # Example value of perf_data_path: 'onefs_sizing/raw_data/aws_perf_source_onefs9.7.json'
        with open(perf_data_path, 'r') as perf_data_file:
            self.perf_data = json.load(perf_data_file)

    # Example of inst_type is "m5dn.12xlarge"
    def GetInstanceReadPerf(self, vol_type, inst_type, config=None):
        if vol_type == "gp3":        
            familly_instype_strs = inst_type.split(".")
            family = familly_instype_strs[0]
            for ins_result in self.perf_data[vol_type][family]:
                if ins_result["name"] == inst_type:
                    return ins_result["per-node-read-perf"]
        elif vol_type == "st1":
            if not self.ValidSt1Config(config):
                return None
            familly_instype_strs = inst_type.split(".")
            family = familly_instype_strs[0]
            if family not in self.perf_data[vol_type][config].keys():
                return None
            else:
                for ins_result in self.perf_data[vol_type][config][family]:
                    if ins_result["name"] == inst_type:
                        return ins_result["per-node-read-perf"]
        else:
            raise ValueError("Unsupported volume type: " + vol_type)

    def GetInstanceWritePerf(self, vol_type, inst_type, config=None):
        if vol_type == "gp3":
            familly_instype_strs = inst_type.split(".")
            family = familly_instype_strs[0]
            for ins_result in self.perf_data[vol_type][family]:
                if ins_result["name"] == inst_type:
                    return ins_result["per-node-write-perf"]
        elif vol_type == "st1":
            if not self.ValidSt1Config(config):
                return None
            familly_instype_strs = inst_type.split(".")
            family = familly_instype_strs[0]
            if family not in self.perf_data[vol_type][config].keys():
                return None
            else:
                for ins_result in self.perf_data[vol_type][config][family]:
                    if ins_result["name"] == inst_type:
                        return ins_result["per-node-write-perf"]
        else:
            raise ValueError("Unsupported volume type: " + vol_type)

    def ValidSt1Config(self, config):
        valid_configs = ["5d4t", "6d4t", "5d10t", "6d10t"]
        if config not in valid_configs:
            raise ValueError("Invalid st1 config: " + config)
        return True