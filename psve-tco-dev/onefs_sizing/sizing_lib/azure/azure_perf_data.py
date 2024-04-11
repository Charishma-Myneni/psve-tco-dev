import json

class AzurePerfData:
    def __init__(self, perf_data_path):
        # Example value of perf_data_path: 'onefs_sizing/raw_data/azure/azure_perf_source_onefs9.8.json'
        with open(perf_data_path, 'r') as perf_data_file:
            self.perf_data = json.load(perf_data_file)
    
    def GetReadPerf(self, ins_family, inst_type, node_count):
        return self.perf_data[ins_family][inst_type]["per-node-read-perf"][str(node_count)]
    
    def GetWritePerf(self, ins_family, inst_type, node_count, protection_level):
        return self.perf_data[ins_family][inst_type]["per-node-write-perf"][protection_level][str(node_count)]