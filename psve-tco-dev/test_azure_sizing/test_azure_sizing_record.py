import pytest
from onefs_sizing.sizing_lib.azure.azure_sizing_record import AzureSizingRecord



def test_GetPrice():

 o3= AzureSizingRecord("Standard_D48d_v5",5,"premium-ssd","p40",12,"Read upto: 5.0 GB/s, Write upto: 3.1 GB/s, Raw Capacity: 100 TiB.","No burst impact for this configuration.")
 assert o3.GetPrice()== -1
 
def test_SetPriceGetPrice():
 
 o3= AzureSizingRecord("Standard_D48d_v5",5,"premium-ssd","p40",12,"Read upto: 5.0 GB/s, Write upto: 3.1 GB/s, Raw Capacity: 100 TiB.","No burst impact for this configuration.")
 
 o3.SetPrice(1000)

 assert o3.GetPrice() == 1000
 