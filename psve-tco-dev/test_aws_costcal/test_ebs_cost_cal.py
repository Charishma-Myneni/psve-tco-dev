import pytest
from tcocal.costcal import EbsVolume

def test_validate_iops_thpt_valid():
   
   ebs= EbsVolume("gp3","us-east-1",100,None,None)
   ebs.validate_iops_thpt()
   assert ebs.volume_iops == 3000
   assert ebs.volume_thpt == 125


   ebs= EbsVolume("gp3","us-east-1",100,5000,500)
   ebs.validate_iops_thpt()
   assert ebs.volume_iops == 5000
   assert ebs.volume_thpt == 500

def test_validate_iops_thpt_invalid_iops():
   
    with pytest.raises(Exception) as ex:
     ebs= EbsVolume("gp3","us-east-1",100,25000,500)
    assert str(ex.value) == "Wrong EBS gp3 iops for us-east-1 region. Ensure your EBS gp3 iops is 3000 <= iops <= 16000."

def test_validate_iops_thpt_invalid_thpt():
   
   with pytest.raises(Exception) as ex:
      ebs= EbsVolume("gp3","us-east-1",100,5000,5000)
   assert str(ex.value) == "Wrong EBS gp3 thpt for us-east-1 region. Ensure your EBS gp3 thpt is 125 <= thpt <= 1000."

def test_validate_iops_thpt_invalid_thptiopsrelation():
     
   try:
      ebs= EbsVolume("gp3","us-east-1",100,3000,700)
   except Exception as E:
      assert str(E) == "Wrong EBS gp3 thpt and iops for us-east-1 region. Ensure your EBS gp3 thpt is 0.25 * iops <= thpt <= 1000."
   
def test_cal_perf_monthly_cost():
   ebs= EbsVolume("gp3","us-east-1",100,4000,900)
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
   expected_perf_monthly_cost = 36 # Result from AWS pricing calculator
   assert expected_perf_monthly_cost == ebs.cal_perf_monthly_cost(ebs_price_data)

def test_cal_perf_monthly_cost_wrong_iopsunit():
   ebs= EbsVolume("gp3","us-east-1",100,4000,900)
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
      "iops_price_unit": "IOoPS-Mo",
      "capacity_price_description": "$0.08 per GB-month of General Purpose (gp3) provisioned storage - US East (N. Virginia)",
      "location": "US East (N. Virginia)"
    }
   }
   }
   try:
      ebs.cal_perf_monthly_cost(ebs_price_data)
   except Exception as E:
      assert str(E) == "Wrong EBS gp3 iops price unit for us-east-1 region. Ensure your EBS gp3 iops price unit is IOPS-Mo."

def test_cal_perf_monthly_cost_wrong_thptunit():
   ebs= EbsVolume("gp3","us-east-1",100,4000,900)
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
      "thpt_price_unit": "GieBps-mo",
      "iops_price_unit": "IOPS-Mo",
      "capacity_price_description": "$0.08 per GB-month of General Purpose (gp3) provisioned storage - US East (N. Virginia)",
      "location": "US East (N. Virginia)"
    }
   }
   }
   try:
      ebs.cal_perf_monthly_cost(ebs_price_data)
   except Exception as E:
      assert str(E) == "Wrong EBS gp3 thpt price unit for us-east-1 region. Ensure your EBS gp3 thpt price unit is GiBps-mo."

def test_cal_perf_monthly_cost_notgp3():
   ebs= EbsVolume("st1","us-east-1",100,4000,900)
   ebs_price_data = {
      "us-east-1": {
    "st1": {
      "capacity_price_hourly": 6.1643835616e-05,
      "capacity_price_per_unit": 0.045,
      "currency": "USD",
      "capacity_price_unit": "GB-Mo",
      "capacity_price_description": "$0.045 per GB-month of Throughput Optimized HDD (st1) provisioned storage - US East (Northern Virginia)",
      "location": "US East (N. Virginia)"
    }
    }
   }
   try:
      ebs.cal_perf_monthly_cost(ebs_price_data)
   except Exception as E:
      assert str(E) == "EBS performance cost calculation for st1 in us-east-1 region is not supported."

def test_cal_capacity_monthly_cost_valid_unit():
 
 ebs= EbsVolume("gp3","us-east-1",100,4000,900)
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
 expected_capacity_monthly_cost = 8 # Result from AWS pricing calculator
 assert ebs.cal_capacity_monthly_cost(ebs_price_data) == expected_capacity_monthly_cost

def test_cal_capacity_monthly_cost_invalid_unit():
 
  ebs= EbsVolume("gp3","us-east-1",100,4000,900)
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
      "capacity_price_unit": "TB-Mo",
      "thpt_price_unit": "GiBps-mo",
      "iops_price_unit": "IOPS-Mo",
      "capacity_price_description": "$0.08 per GB-month of General Purpose (gp3) provisioned storage - US East (N. Virginia)",
      "location": "US East (N. Virginia)"
    }  
      }
 }
  try:
    ebs.cal_capacity_monthly_cost(ebs_price_data)
  except Exception as e:
    assert str(e) == "Wrong EBS gp3 price unit for us-east-1 region in the ebs price json file. Ensure your EBS price unit is GB-Mo."

def test_cal_monthly_cost_gp3():
   ebs= EbsVolume("gp3","us-east-1",500,3000,700)
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
   assert ebs.cal_monthly_cost(ebs_price_data) == 63 # Result from AWS pricing calculator

def test_cal_monthly_cost_nongp3():
   ebs= EbsVolume("st1","us-east-1",500,3000,700)
   ebs_price_data = {
      "us-east-1": {
      "st1":{
      "capacity_price_hourly": 6.1643835616e-05,
      "capacity_price_per_unit": 0.045,
      "currency": "USD",
      "capacity_price_unit": "GB-Mo",
      "capacity_price_description": "$0.045 per GB-month of Throughput Optimized HDD (st1) provisioned storage - US East (Northern Virginia)",
      "location": "US East (N. Virginia)"
    }
  }
   }
   assert ebs.cal_monthly_cost(ebs_price_data) == 22.50 # Result from AWS pricing calculator
   
   