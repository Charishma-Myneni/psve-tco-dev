from onefs_sizing.sizing_lib.aws.aws_supported_config import AwsSupportedConfig
from onefs_sizing.sizing_lib.aws.aws_perf_data import AwsPerfData
from onefs_sizing.sizing_lib.aws.aws_sizer import AWSSizer

class OneFS96AWSSizer(AWSSizer):

    def __init__(self):
        onefs_supported_config_path = 'onefs_sizing/raw_data/aws/aws_supported_config_onefs9.6.json'
        supported_config = AwsSupportedConfig(onefs_supported_config_path)

        onefs_perf_data_path = 'onefs_sizing/raw_data/aws/aws_perf_source_onefs9.6.json'
        perf_data = AwsPerfData(onefs_perf_data_path)
        
        super().__init__(supported_config, perf_data)


