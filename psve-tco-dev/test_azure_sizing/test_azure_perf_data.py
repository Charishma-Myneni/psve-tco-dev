import pytest
from onefs_sizing.sizing_lib.azure.azure_perf_data import AzurePerfData

o2 = AzurePerfData('psve-tco/onefs_sizing/raw_data/azure/azure_perf_source_onefs9.8.json')

def test_GetReadPerf():

 assert o2.GetReadPerf("edsv5","Standard_E32ds_v5","8") == 960.0
 assert o2.GetReadPerf("edsv5","Standard_E32ds_v5","12") == 939.1
 assert o2.GetReadPerf("ddsv5","Standard_D48ds_v5","12") == 1408.7

def test_GetWritePerf():
 
  assert o2.GetWritePerf("edsv5","Standard_E32ds_v5","8","+2n") == 575.7
  assert o2.GetWritePerf("edsv5","Standard_E32ds_v5","12","+2d:1n") == 503.4
  assert o2.GetWritePerf("ddsv5","Standard_D48ds_v5","8","+2n") == 838