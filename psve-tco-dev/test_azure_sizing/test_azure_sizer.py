import pytest
from onefs_sizing.sizing_lib.azure.azure_sizer import AzureSizer
from onefs_sizing.sizing_lib.azure.azure_supported_config import AzureSupportedConfig
from onefs_sizing.sizing_lib.azure.azure_perf_data import AzurePerfData
from onefs_sizing.sizing_lib.azure.utilities import AzureUtility


def test_SizeSequentialWorkload_Invalid():

    assert AzureSizer.SizeSequentialWorkload(AzureSizer,"Workload",1,180,"+2n",3000,1000) == None

def test_GetBurstMessage():

    assert AzureSizer.GetBurstMessage(AzureSizer,"Standard_E32ds_v5",5,3000) == "Burst time can last more than 24 hours. No burst impact for this configuration."