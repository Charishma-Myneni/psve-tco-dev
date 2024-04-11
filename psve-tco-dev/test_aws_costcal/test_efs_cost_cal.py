import pytest
from tcocal.costcal import EfsStorage

def test_cal_efs_monthly_cost_valid_unit():
    
    efs= EfsStorage("us-east-1","one_zone_storage", 1000)
    efs_price_data = {"us-east-1": {
    "one_zone_storage": {
      "price": 0.16,
      "unit": "GB-Mo",
      "description": "$0.16 per GB-Mo for One Zone Storage in US East (N. Virginia)",
      "storage_class": "One Zone-General Purpose",
      "location": "US East (N. Virginia)"
    }}}
    assert efs.cal_efs_monthly_cost(efs_price_data) == 160 #Result from AWS Pricing calculator . 100% frequently used data.

def test_cal_efs_monthly_cost_invalid_unit():
    
    efs= EfsStorage("us-east-1","one_zone_storage", 1000)
    efs_price_data = {"us-east-1": {
    "one_zone_storage": {
      "price": 0.16,
      "unit": "TB-Mo",
      "description": "$0.16 per GB-Mo for One Zone Storage in US East (N. Virginia)",
      "storage_class": "One Zone-General Purpose",
      "location": "US East (N. Virginia)"
    }}}
    try:
        efs.cal_efs_monthly_cost(efs_price_data)
    except Exception as e:
        assert str(e) == "Wrong EFS price unit for us-east-1 region in the efs price json file. Ensure your EFS size unit is GB-Mo."



