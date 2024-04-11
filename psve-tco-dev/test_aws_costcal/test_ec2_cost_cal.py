import pytest
from tcocal.costcal import Ec2Instance

def test_cal_hourly_cost_valid_unit():

    ec2= Ec2Instance( "m5dn.8xlarge","us-east-1","on-demand")
   
    ec2_price_data = {
        "us-east-1": {
    "m5dn.8xlarge": {
      "on-demand": 2.176,
      "on-demand-description": "$2.176 per On Demand Linux m5dn.8xlarge Instance Hour",
      "unit": "Hrs",
      "ec2-saving-plan-3-years-no-upfront": 0.846,
      "currency": "USD",
      "tenancy": "Shared",
      "location": "US East (N. Virginia)"
    }
        }
    }

    hourly_cost = ec2.cal_hourly_cost(ec2_price_data)
    assert hourly_cost == 2.176 

def test_cal_hourly_cost_invalid_unit():

    ec2= Ec2Instance( "m5dn.8xlarge","us-east-1","on-demand")
   
    ec2_price_data = {
        "us-east-1": {
    "m5dn.8xlarge": {
      "on-demand": 2.176,
      "on-demand-description": "$2.176 per On Demand Linux m5dn.8xlarge Instance Hour",
      "unit": "monthly",
      "ec2-saving-plan-3-years-no-upfront": 0.846,
      "currency": "USD",
      "tenancy": "Shared",
      "location": "US East (N. Virginia)"
    }
        }
    }
    try:
     ec2.cal_hourly_cost(ec2_price_data)
    except Exception as e:
     assert str(e) == "Wrong EC2 m5dn.8xlarge price unit for us-east-1 region in the ec2 price json file. Ensure your EC2 price unit is Hrs."