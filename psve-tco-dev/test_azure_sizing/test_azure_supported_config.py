import pytest
from onefs_sizing.sizing_lib.azure.azure_supported_config import AzureSupportedConfig

o1 = AzureSupportedConfig('psve-tco/onefs_sizing/raw_data/azure/azure_supported_config_onefs9.8.json')

def test_ValidDataDiskType():
  
    assert o1.ValidDataDiskType("premium-ssd","p20",1000,"+5n") == False   
    assert o1.ValidDataDiskType("premium-ssd","p20",5000,"+2n") == False
    assert o1.ValidDataDiskType("premium-ssd","p20",1000,"+2n") == True
    assert o1.ValidDataDiskType("premium-ssd","p20",850,"+2d:1n") == False
    assert o1.ValidDataDiskType("premium-ssd","p20",840,"+2d:1n") == True


def test_RawCapacitySmallerThanSupportedDiskType():
  assert o1.RawCapacitySmallerThanSupportedDiskType("premium-ssd",10) == False
  assert o1.RawCapacitySmallerThanSupportedDiskType("premium-ssd",9) == True
  assert o1.RawCapacitySmallerThanSupportedDiskType("premium-ssd",11) == False

def test_FindClosestSupportedDiskCount():
   assert o1.FindClosestSupportedDiskCount("premium-ssd","p20",40) == -1
   assert o1.FindClosestSupportedDiskCount("premium-ssd","p20",18) == 18
   