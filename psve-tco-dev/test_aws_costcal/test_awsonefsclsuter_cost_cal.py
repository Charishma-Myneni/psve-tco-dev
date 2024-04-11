import pytest
from tcocal.costcal import Ec2Instance
from tcocal.costcal import EbsVolume
from tcocal.costcal import AwsOnefsNode
from tcocal.costcal import AwsOnefsCluster

def test_cal_cluster_raw_capacity():

    ec2 = Ec2Instance( "m5dn.8xlarge","us-east-1","on-demand")
    ebs= EbsVolume("gp3","us-east-1",500,3000,700)
    afsnode= AwsOnefsNode("OneFS 9.6",ec2,ebs,20)
    afscluster = AwsOnefsCluster("us-east-1","1-year",83,afsnode,6,1.6,"2n")
    assert afscluster.cal_cluster_raw_capacity() == 6*500*20    # 6 nodes;500 volume_size;20 disks

def test_cal_cluster_usable_capacity_invalid_protectionlevel():
    
    ec2 = Ec2Instance( "m5dn.8xlarge","us-east-1","on-demand")
    ebs= EbsVolume("gp3","us-east-1",500,3000,700)
    afsnode= AwsOnefsNode("OneFS 9.6",ec2,ebs,20)
    afscluster = AwsOnefsCluster("us-east-1","1-year",83,afsnode,6,1.6,"3n")
    try:
        afscluster.cal_cluster_usable_capacity
    except Exception as E:
     assert str(E) == "Wrong OneFS protection level. Currently only support 2n protection level."



def test_cal_cluster_usable_capacity_valid_6node():
    
    ec2 = Ec2Instance( "m5dn.8xlarge","us-east-1","on-demand")
    ebs= EbsVolume("gp3","us-east-1",500,3000,700)
    afsnode= AwsOnefsNode("OneFS 9.6",ec2,ebs,20)
    afscluster = AwsOnefsCluster("us-east-1","1-year",83,afsnode,6,1.6,"2n")

    assert afscluster.cal_cluster_usable_capacity() == 6* 10000 * (1-(2/6))  #usable_capacity = self.node_amount * self.node.cal_node_raw_capacity() * (1 - protection_overhead)

def test_cal_cluster_usable_capacity_valid_5node():
    
    ec2 = Ec2Instance( "m5dn.8xlarge","us-east-1","on-demand")
    ebs= EbsVolume("gp3","us-east-1",500,3000,700)
    afsnode= AwsOnefsNode("OneFS 9.6",ec2,ebs,20)
    afscluster = AwsOnefsCluster("us-east-1","1-year",83,afsnode,5,1.6,"2n")

    assert afscluster.cal_cluster_usable_capacity() == 5*10000 * (1-(2/5)) #usable_capacity = self.node_amount * self.node.cal_node_raw_capacity() * (1 - protection_overhead)

def test_cal_cluster_usable_capacity_valid_4node():
    
    ec2 = Ec2Instance( "m5dn.8xlarge","us-east-1","on-demand")
    ebs= EbsVolume("gp3","us-east-1",500,3000,700)
    afsnode= AwsOnefsNode("OneFS 9.6",ec2,ebs,20)
    afscluster = AwsOnefsCluster("us-east-1","1-year",83,afsnode,4,1.6,"2n")

    assert afscluster.cal_cluster_usable_capacity() == 4*10000 * (1-(2/4)) #usable_capacity = self.node_amount * self.node.cal_node_raw_capacity() * (1 - protection_overhead)

def test_cal_cluster_effective_capacity_invalid_protectionlevel():
    
    ec2 = Ec2Instance( "m5dn.8xlarge","us-east-1","on-demand")
    ebs= EbsVolume("gp3","us-east-1",500,3000,700)
    afsnode= AwsOnefsNode("OneFS 9.6",ec2,ebs,20)
    afscluster = AwsOnefsCluster("us-east-1","1-year",83,afsnode,6,1.6,"3n")
    try:
        afscluster.cal_cluster_effective_capacity
    except Exception as E:
     assert str(E) == "Wrong OneFS protection level. Currently only support 2n protection level."

def test_cal_cluster_effective_capacity_valid_6node():
    
    ec2 = Ec2Instance( "m5dn.8xlarge","us-east-1","on-demand")
    ebs= EbsVolume("gp3","us-east-1",500,3000,700)
    afsnode= AwsOnefsNode("OneFS 9.6",ec2,ebs,20)
    afscluster = AwsOnefsCluster("us-east-1","1-year",83,afsnode,6,1.6,"2n")

    assert afscluster.cal_cluster_effective_capacity() == 6* 10000 * (1-(2/6))*1.6  #effective_capacity = self.node_amount * self.node.cal_node_raw_capacity() * (1 - protection_overhead) * self.drr_ratio

def test_cal_cluster_effective_capacity_valid_5node():
    
    ec2 = Ec2Instance( "m5dn.8xlarge","us-east-1","on-demand")
    ebs= EbsVolume("gp3","us-east-1",500,3000,700)
    afsnode= AwsOnefsNode("OneFS 9.6",ec2,ebs,20)
    afscluster = AwsOnefsCluster("us-east-1","1-year",83,afsnode,5,1.6,"2n")

    assert afscluster.cal_cluster_effective_capacity() == 5*10000 * (1-(2/5))*1.6 #effective_capacity = self.node_amount * self.node.cal_node_raw_capacity() * (1 - protection_overhead) * self.drr_ratio

def test_cal_cluster_effective_capacity_valid_4node():
    
    ec2 = Ec2Instance( "m5dn.8xlarge","us-east-1","on-demand")
    ebs= EbsVolume("gp3","us-east-1",500,3000,700)
    afsnode= AwsOnefsNode("OneFS 9.6",ec2,ebs,20)
    afscluster = AwsOnefsCluster("us-east-1","1-year",83,afsnode,4,1.6,"2n")

    assert afscluster.cal_cluster_effective_capacity() == 4*10000 * (1-(2/4))*1.6 #effective_capacity = self.node_amount * self.node.cal_node_raw_capacity() * (1 - protection_overhead) * self.drr_ratio


def test_cal_cluster_ec2_hourly_cost():

    ec2 = Ec2Instance( "m5dn.8xlarge","us-east-1","on-demand")
    ebs= EbsVolume("gp3","us-east-1",500,3000,700)
    afsnode= AwsOnefsNode("OneFS 9.6",ec2,ebs,20)
    afscluster = AwsOnefsCluster("us-east-1","1-year",83,afsnode,6,1.6,"2n")

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

    assert afscluster.cal_cluster_ec2_hourly_cost(ec2_price_data) == 6*2.176 # 6 nodes and Ec2 hourly cost

def test_cal_cluster_ebs_monthly_cost():

    ec2 = Ec2Instance( "m5dn.8xlarge","us-east-1","on-demand")
    ebs= EbsVolume("gp3","us-east-1",500,3000,700)
    afsnode= AwsOnefsNode("OneFS 9.6",ec2,ebs,20)
    afscluster = AwsOnefsCluster("us-east-1","1-year",83,afsnode,6,1.6,"2n")

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
    
    assert afscluster.cal_cluster_ebs_monthly_cost(ebs_price_data) == 6*afsnode.data_disk_amount*63 # 6 nodes; 63 is ebs monthly cost per drive from AWS pricing calculator

def test_cal_cluster_onefs_monthly_cost_1year():
    ec2 = Ec2Instance( "m5dn.8xlarge","us-east-1","on-demand")
    ebs= EbsVolume("gp3","us-east-1",500,3000,700)
    afsnode= AwsOnefsNode("OneFS 9.6",ec2,ebs,20)
    afscluster = AwsOnefsCluster("us-east-1","1-year",83,afsnode,6,1.6,"2n")

    onefs_license_price_data = {
     "1-year" : {
        "price" : 2.39,
        "unit" : "GiB(raw)"}}
    
    assert afscluster.cal_cluster_onefs_monthly_cost(onefs_license_price_data) == (2.39/12)*60000*(1-0.83) #cluster_onefs_monthly_cost = onefs_monthly_price * self.cal_cluster_raw_capacity() * (1-onefs_license_discount/100)

def test_cal_cluster_onefs_monthly_cost_3year():
    ec2 = Ec2Instance( "m5dn.8xlarge","us-east-1","on-demand")
    ebs= EbsVolume("gp3","us-east-1",500,3000,700)
    afsnode= AwsOnefsNode("OneFS 9.6",ec2,ebs,20)
    afscluster = AwsOnefsCluster("us-east-1","3-years",83,afsnode,6,1.6,"2n")

    onefs_license_price_data = {
     "3-years" : {
        "price" : 5.87,
        "unit" : "GiB(raw)"
    }}
    
    assert afscluster.cal_cluster_onefs_monthly_cost(onefs_license_price_data) == (5.87/36)*60000*(1-0.83) #cluster_onefs_monthly_cost = onefs_monthly_price * self.cal_cluster_raw_capacity() * (1-onefs_license_discount/100)
