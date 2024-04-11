import pytest
from tcocal.costcal import Ec2Instance
from tcocal.costcal import EbsVolume
from tcocal.costcal import AwsOnefsNode

def test_cal_node_raw_capacity():

    ec2 = Ec2Instance( "m5dn.8xlarge","us-east-1","on-demand")
    ebs= EbsVolume("gp3","us-east-1",500,3000,700)
    afsnode= AwsOnefsNode("OneFS 9.6",ec2,ebs,20)

    assert afsnode.cal_node_raw_capacity() == 10000   # 20 (disks) *500 (volume size)

def test_cal_node_ec2_hourly_cost():

    ec2 = Ec2Instance( "m5dn.8xlarge","us-east-1","on-demand")
    ebs= EbsVolume("gp3","us-east-1",500,3000,700)
    afsnode= AwsOnefsNode("OneFS 9.6",ec2,ebs,20)
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
    assert afsnode.cal_node_ec2_hourly_cost(ec2_price_data) == 2.176

def test_cal_node_ebs_monthly_cost():
     
     ec2 = Ec2Instance( "m5dn.8xlarge","us-east-1","on-demand")
     ebs= EbsVolume("gp3","us-east-1",500,3000,700)
     afsnode= AwsOnefsNode("OneFS 9.6",ec2,ebs,20)

     ebs_price_data = {
      "us-east-1": {
    "gp3": {
      "capacity_price_hourly": 0.000109589041096,
      "thpt_price_hourly": 0.056109589,
      "iops_price_hourly": 6.849315068493151e-06,
      "capacity_price_per_unit": 0.08,
      "thpt_price_per_unit": 40.96,
      "iops_price_per_unit": 0.005,
      "currency": "USD",
      "capacity_price_unit": "GB-Mo",
      "thpt_price_unit": "GiBps-mo",
      "iops_price_unit": "IOPS-Mo",
      "capacity_price_description": "$0.08 per GB-month of General Purpose (gp3) provisioned storage - US East (N. Virginia)",
      "location": "US East (N. Virginia)"
    }  
      }
       }
     
     assert afsnode.cal_node_ebs_monthly_cost(ebs_price_data) == 63*20 # 63 is  Ebs price for each disk (from AWS pricing calculator)

