from onefs_sizing.sizing_lib.azure.azure_sizer import AzureSizer
from onefs_sizing.sizing_lib.azure.azure_supported_config import AzureSupportedConfig
from onefs_sizing.sizing_lib.azure.azure_perf_data import AzurePerfData

class OneFS98AzureSizer(AzureSizer):

    def __init__(self):
        onefs_supported_config_path = 'onefs_sizing/raw_data/azure/azure_supported_config_onefs9.8.json'
        supported_config = AzureSupportedConfig(onefs_supported_config_path)

        onefs_perf_data_path = 'onefs_sizing/raw_data/azure/azure_perf_source_onefs9.8.json'
        perf_data = AzurePerfData(onefs_perf_data_path)
        
        super().__init__(supported_config, perf_data)