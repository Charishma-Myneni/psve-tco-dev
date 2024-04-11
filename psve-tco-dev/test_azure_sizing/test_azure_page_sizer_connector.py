import pytest
from onefs_sizing.sizing_lib.azure.azure_page_sizer_connector import SizeSolutionFromPage
from onefs_sizing.sizing_lib.azure.azure_sizer import AzureSizer
from onefs_sizing.sizing_lib.azure.azure_supported_config import AzureSupportedConfig
from onefs_sizing.sizing_lib.azure.azure_perf_data import AzurePerfData
from onefs_sizing.sizing_lib.azure.azure_onefs98_sizer import OneFS98AzureSizer

def test_SizeSolutionFromPage1():

    assert SizeSolutionFromPage("OneFS 9.8","us-east-1","Archive",1.0,180,"+2d:1n",3000,1000,"AWS") == []

def test_SizeSolutionFromPage2():

    assert SizeSolutionFromPage("OneFS 9.9","us-east-1","Archive",1.0,180,"+2d:1n",3000,1000,"Azure") == [{'Message': 1, 'Detail': 'OneFS version is not supported by sizing tool yet.'}]

def test_SizeSolutionFromPage3():
 
  assert SizeSolutionFromPage("OneFS 9.8","us-east-1","Archive",1.0,180,"+2d:1n",3000,1000,"Azure") == [{'Message': 1, 'Detail': 'Sizing for Archive workload is not supported by sizing tool yet.'}]