import requests, os
import boto3
import json


def load_json_data(path):
    f = open(path)
    data = json.load(f)
    f.close()
    return data

# query a specific instance type price info for all regions of on-demand
def query_instance_type_price_list_on_demand(instance_type):
    client = boto3.client('pricing')
    ec2_price_list = {
        "PriceList": []
    }

    response = client.get_products(
        ServiceCode='AmazonEC2', 
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
            {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
            {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
            #{'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': 'us-east-1'},
            {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},         
        ],
        MaxResults=100,
    )
   
    for price_list in response['PriceList']:
        price_list_json = json.loads(price_list)
        if "instancesku" in price_list_json["product"]["attributes"]:
            #print(price_list_json["product"]["attributes"]["instancesku"])
            #print(price_list_json["product"]["sku"])
            continue
        else:
            #print("found on demand instance price")
            # print(price_list_json["product"]["attributes"]["regionCode"])
            # print(price_list_json["product"]["attributes"]["location"])
            #print(price_list_json["product"]["sku"])
            ec2_price_list["PriceList"].append(price_list_json)

    return ec2_price_list

# Save a set of instance types price info to a json file
# used for saving supported instance types original price info
def generate_supported_ec2_price_json_file(instance_types):
    ec2_price_json_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/supported-instance-types-on-demand-price.json"
    #ec2_price_json_path = r"C:\vscode\psve-tco\tcocal" + "/price/supported-instance-types-on-demand-price.json"
    ec2_price_list = {
        "PriceList": []
    }
    for instance_type in instance_types:
        instance_type_price_list = query_instance_type_price_list_on_demand(instance_type)
        ec2_price_list["PriceList"] = ec2_price_list["PriceList"] + instance_type_price_list["PriceList"]
    
    print(len(ec2_price_list["PriceList"]))
    #print(ec2_price_list)
    f = open(ec2_price_json_path, 'w')
    json.dump(ec2_price_list, f, indent=2)
    f.close()
    return ec2_price_json_path


# query a specific instance type price info for all regions of savings plans
def query_instance_type_price_list_savings_plans(instance_type):
    client = boto3.client('savingsplans')
    ec2_price_list = {
        "PriceList": []
    }

    response = client.describe_savings_plans_offering_rates(
        savingsPlanTypes=['EC2Instance'], # specify the correct savings plan type it can be "EC2Instance" or "Compute"
        savingsPlanPaymentOptions=['No Upfront'],
        products=['EC2'],
        serviceCodes=['AmazonEC2'],
        filters=[
            {'name': 'instanceType', 'values': [instance_type]},
            #{'name': 'region', 'values': ['us-east-1']},
            {'name': 'tenancy', 'values': ['shared']},
            {'name': 'productDescription', 'values': ['Linux/UNIX']}
        ],
        #nextToken="11111115011Soo2GMQp6Yssf8an6ky1bcQgqAMccj265CAdFky8DkEUaGwdeoXiwiBvWJocrpwGVCCyp4FEemrvsneiVHXH7yeGKghbJFouJSCo",
        maxResults=100
    )
    next_token = response["nextToken"]
    ec2_price_list["PriceList"]+=response['searchResults']
    
    while 'nextToken' in response and response['nextToken'] != '':  
        ec2_price_list["PriceList"] += response['searchResults']
        next_token = response["nextToken"]
        #print(next_token)
        response = client.describe_savings_plans_offering_rates(
            savingsPlanTypes=['EC2Instance'], # specify the correct savings plan type it can be "EC2Instance" or "Compute"
            savingsPlanPaymentOptions=['No Upfront'],
            products=['EC2'],
            serviceCodes=['AmazonEC2'],
            filters=[
                {'name': 'instanceType', 'values': [instance_type]},
                #{'name': 'region', 'values': ['us-east-1']},
                {'name': 'tenancy', 'values': ['shared']},
                {'name': 'productDescription', 'values': ['Linux/UNIX']}
            ],
            nextToken=next_token,
            maxResults=100
        )
        next_token = response["nextToken"]
        ec2_price_list["PriceList"]+=response['searchResults']

    return ec2_price_list

# Save a set of instance types savings plans price info to a json file
# used for saving supported instance types original price info
def generate_supported_ec2_savings_plans_price_json_file(instance_types):
    ec2_price_json_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/supported-instance-types-savings-plans-price.json"
    #ec2_price_json_path = r"C:\vscode\psve-tco\tcocal" + "/price/supported-instance-types-savings-plans-price.json"
    ec2_price_list = {
        "PriceList": []
    }
    for instance_type in instance_types:
        instance_type_price_list = query_instance_type_price_list_savings_plans(instance_type)
        ec2_price_list["PriceList"] = ec2_price_list["PriceList"] + instance_type_price_list["PriceList"]
    print(len(ec2_price_list["PriceList"]))
    #print(ec2_price_list)
    f = open(ec2_price_json_path, 'w')
    json.dump(ec2_price_list, f, indent=2)
    f.close()
    return ec2_price_json_path

# query a specific ebs type price info for all regions, not include IOPS/throughput price
# product_family = 'Storage' for capacity price
# product_family = 'System Operation' for IOPS and product_family = 'Provisioned Throughput' for throughput price, at least for gp3, not validate for others
def query_ebs_price_list(volume_api_name, product_family):
    client = boto3.client('pricing')
    ebs_price_list = {
        "PriceList": []
    }
    response = client.get_products(
        ServiceCode='AmazonEC2', 
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'volumeApiName', 'Value': volume_api_name},
            #{'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': 'us-west-2'},
            {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': product_family},  
            #{'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'System Operation'}, 
        ],
        MaxResults=100,
    )
    for price_list in response['PriceList']:  
        ebs_price_list["PriceList"].append(json.loads(price_list))
    while ("NextToken" in response.keys()):
        next_token = response["NextToken"]
        response = client.get_products(
            ServiceCode='AmazonEC2', 
            Filters=[
                {'Type': 'TERM_MATCH', 'Field': 'volumeApiName', 'Value': volume_api_name},
                #{'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': 'us-west-2'},
                {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': product_family},  
                #{'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'System Operation'},  
            ],
            MaxResults=100,
            NextToken=next_token,
        )
        for price_list in response['PriceList']:  
            ebs_price_list["PriceList"].append(json.loads(price_list))
    print(len(ebs_price_list["PriceList"]))    
    return ebs_price_list

# Save a set of EBS volume price info to a json file
# used for saving supported EBS types original price info
def generate_supported_ebs_price_json_file(volume_api_names, product_family):
    #ebs_price_json_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/{}-on-demand-price.json".format(instance_type)
    #ebs_price_json_path = r"C:\vscode\psve-tco\tcocal" + "/price/{}-on-demand-price.json".format(instance_type)
    if product_family == "Storage":
        ebs_price_json_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/supported-ebs-capacity-price.json"
        #ebs_price_json_path = r"C:\vscode\psve-tco\tcocal" + "/price/supported-ebs-capacity-price.json"
    elif product_family == "System Operation":
        ebs_price_json_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/supported-ebs-perf-iops-price.json"
        #ebs_price_json_path = r"C:\vscode\psve-tco\tcocal" + "/price/supported-ebs-perf-iops-price.json"
    elif product_family == "Provisioned Throughput":
        ebs_price_json_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/supported-ebs-perf-thpt-price.json"
        #ebs_price_json_path = r"C:\vscode\psve-tco\tcocal" + "/price/supported-ebs-perf-thpt-price.json"
    else:
        raise Exception("The product_family should be Storage for capacity price or System Operation/Provisioned Throughput for EBS perf price")
    ebs_price_list = {
        "PriceList": []
    }
    for volume_api_name in volume_api_names:
        volume_api_name_price_list = query_ebs_price_list(volume_api_name, product_family)
        ebs_price_list["PriceList"] = ebs_price_list["PriceList"] + volume_api_name_price_list["PriceList"]
    
    print(len(ebs_price_list["PriceList"]))
    #print(ebs_price_list)
    f = open(ebs_price_json_path, 'w')
    json.dump(ebs_price_list, f, indent=2)
    f.close()
    return ebs_price_json_path

# Query AWS EFS service price list, including all regions and provisioned throughput
def query_efs_price_list():
    client = boto3.client('pricing')
    efs_price_list = {
        "PriceList": []
    }
    response = client.get_products(
        ServiceCode='AmazonEFS', 
        Filters=[
            #{'Type': 'TERM_MATCH', 'Field': 'volumeApiName', 'Value': volume_api_name},
            #{'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': 'us-west-2'},
            #{'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': product_family},  
            #{'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'System Operation'}, 
        ],
        MaxResults=100,
    )
    for price_list in response['PriceList']:  
        efs_price_list["PriceList"].append(json.loads(price_list))
    while ("NextToken" in response.keys()):
        next_token = response["NextToken"]
        response = client.get_products(
            ServiceCode='AmazonEFS', 
            Filters=[
                #{'Type': 'TERM_MATCH', 'Field': 'volumeApiName', 'Value': volume_api_name},
                #{'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': 'us-west-2'},
                #{'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': product_family},  
                #{'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'System Operation'},  
            ],
            MaxResults=100,
            NextToken=next_token,
        )
        for price_list in response['PriceList']:  
            efs_price_list["PriceList"].append(json.loads(price_list))
    print(len(efs_price_list["PriceList"]))    
    return efs_price_list

# Save AWS EFS original price info to a json file
def generate_efs_price_json_file():
    efs_price_json_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/efs-price-original.json"
    # efs_price_json_path = r"C:\vscode\psve-tco\tcocal" + "/price/efs-price-original.json"    
    efs_price_list = query_efs_price_list()
    
    print(len(efs_price_list["PriceList"]))
    #print(ebs_price_list)
    f = open(efs_price_json_path, 'w')
    json.dump(efs_price_list, f, indent=2)
    f.close()
    return efs_price_json_path



# get supported instance types for all OneFS versions to get all price info
def get_supported_instance_types_all_onefs():
    supported_cluster_config_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/supported_cluster_config.json"
    config_data = load_json_data(supported_cluster_config_path)
    supported_instance_types = []
    for key in config_data.keys():
        for instance_type in config_data[key]['supported-instance-type']:
            if instance_type not in supported_instance_types:
                supported_instance_types.append(instance_type)
    return supported_instance_types


# get supported regions based on supported cluster config json file for all OneFS versions 
def get_supported_regions():
    supported_cluster_config_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/supported_cluster_config.json"
    config_data = load_json_data(supported_cluster_config_path)
    supported_regions = []
    for key in config_data.keys():
        for region in config_data[key]["supported-regions"]:
            if region not in supported_regions:
                supported_regions.append(region)
    return supported_regions


def update_ec2_price_json(supported_instance_types, supported_regions, supported_ec2_price_path_ori, supported_ec2_savings_plans_price_path_ori):
    ec2_price_json_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/ec2-price.json"
    ec2_price_on_demand = load_json_data(supported_ec2_price_path_ori)
    ec2_price_savings_plans = load_json_data(supported_ec2_savings_plans_price_path_ori)
    ec2_price_json = {}
    for supported_region in supported_regions:
        ec2_price_json[supported_region] = {}
        for supported_instance_type in supported_instance_types:
            #ec2_price_json[supported_region][supported_instance_type] = {}
            filtered_ec2_price_list = []
            filtered_sp_price_list = []
            filtered_sp_price_list_rate = []
            for price_list in ec2_price_on_demand["PriceList"]:
                if price_list["product"]["attributes"]["regionCode"] == supported_region and price_list["product"]["attributes"]["instanceType"] == supported_instance_type:
                  if len(price_list["terms"]["OnDemand"].keys()) == 1:                   
                      key = list(price_list["terms"]["OnDemand"].keys())[0]
                      tenancy = price_list["product"]["attributes"]["tenancy"]
                      location = price_list["product"]["attributes"]["location"]
                      if len(price_list["terms"]["OnDemand"][key]["priceDimensions"].keys()) == 1:
                          price_dimensions_key = list(price_list["terms"]["OnDemand"][key]["priceDimensions"].keys())[0]
                          unit = price_list["terms"]["OnDemand"][key]["priceDimensions"][price_dimensions_key]["unit"]
                          description = price_list["terms"]["OnDemand"][key]["priceDimensions"][price_dimensions_key]["description"]
                          price_per_unit = round(float(price_list["terms"]["OnDemand"][key]["priceDimensions"][price_dimensions_key]["pricePerUnit"]["USD"]), 15)
                      else:
                         raise Exception("More than one priceDimensions may exist: {}".format(str(price_list["terms"]["OnDemand"][key]["priceDimensions"].keys()))) 
                  else:
                    raise Exception("More than one offerTermCode may exist: {}".format(str(price_list["terms"]["OnDemand"].keys())))
                  ec2_price_json[supported_region][supported_instance_type] = {
                    "on-demand": price_per_unit,
                    "on-demand-description": description,
                    "unit": unit,
                    "ec2-saving-plan-3-years-no-upfront": 0,
                    "currency": "USD",
                    "tenancy": tenancy,
                    "location": location
                  }
                  filtered_ec2_price_list.append(price_list)
            if len(filtered_ec2_price_list) == 0:
                print(("Cannot find {0} on demand price info in region {1}".format(supported_instance_type, supported_region)) )                 
            for sp_price_list in ec2_price_savings_plans["PriceList"]:    
                if sp_price_list["savingsPlanOffering"]["paymentOption"] == "No Upfront" and sp_price_list["savingsPlanOffering"]["planType"] == "EC2Instance" \
                and sp_price_list["savingsPlanOffering"]["durationSeconds"] == 94608000 and sp_price_list["properties"][4]["value"] == supported_region and \
                sp_price_list["properties"][2]["value"] == supported_instance_type:
                    filtered_sp_price_list_rate.append(sp_price_list["rate"])
                    filtered_sp_price_list.append(sp_price_list)
            if len(filtered_sp_price_list) > 0 and len(set(filtered_sp_price_list_rate)) == 1:
                # In theory, the instance not availbale with on-demand, it should alos not available with savings plans, but I found m5dn is not the case in ap-south-1 and ap-northeast-2
                # so I add an condition to workaround this, need to investigate further
                if supported_instance_type in ec2_price_json[supported_region].keys():
                    ec2_price_json[supported_region][supported_instance_type]["ec2-saving-plan-3-years-no-upfront"] = round(float(filtered_sp_price_list[0]["rate"]), 15)
            elif len(filtered_sp_price_list) == 0: 
                #raise Exception("Cannot find {0} savings plans price info in region {1}".format(supported_instance_type, supported_region)) 
                print(("Cannot find {0} savings plans price info in region {1}".format(supported_instance_type, supported_region)) )
            else:
                print(filtered_sp_price_list)
                raise Exception("Cannot tell the correct {0} savings plans price info in region {1} with different usagetype".format(supported_instance_type, supported_region))    
    f = open(ec2_price_json_path, 'w')
    json.dump(ec2_price_json, f, indent=2)
    f.close()

    

def update_ebs_price_json(supported_ebs_types, supported_regions, supported_ebs_capacity_price_path_ori, supported_ebs_perf_iops_price_path_ori, supported_ebs_perf_thpt_price_path_ori):
    ebs_price_json_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/ebs-price.json"
    ebs_cap_price = load_json_data(supported_ebs_capacity_price_path_ori)
    ebs_perf_iops_price = load_json_data(supported_ebs_perf_iops_price_path_ori)
    ebs_perf_thpt_price = load_json_data(supported_ebs_perf_thpt_price_path_ori)
    ebs_price_json = {}
    for supported_region in supported_regions:
        ebs_price_json[supported_region] = {}
        for supported_ebs_type in supported_ebs_types:
            #ec2_price_json[supported_region][supported_instance_type] = {}
            filtered_ebs_cap_price_list = []
            filtered_ebs_iops_price_list = []
            filtered_ebs_thpt_price_list = []
            if supported_ebs_type == "gp3":
                for price_list in ebs_cap_price["PriceList"]:
                    if price_list["product"]["attributes"]["regionCode"] == supported_region and price_list["product"]["attributes"]["volumeApiName"] == supported_ebs_type:
                        if len(price_list["terms"]["OnDemand"].keys()) == 1:                   
                            key = list(price_list["terms"]["OnDemand"].keys())[0]
                            location = price_list["product"]["attributes"]["location"]
                            if len(price_list["terms"]["OnDemand"][key]["priceDimensions"].keys()) == 1:
                                price_dimensions_key = list(price_list["terms"]["OnDemand"][key]["priceDimensions"].keys())[0]
                                unit = price_list["terms"]["OnDemand"][key]["priceDimensions"][price_dimensions_key]["unit"]
                                description = price_list["terms"]["OnDemand"][key]["priceDimensions"][price_dimensions_key]["description"]
                                price_per_unit = round(float(price_list["terms"]["OnDemand"][key]["priceDimensions"][price_dimensions_key]["pricePerUnit"]["USD"]), 15)
                                capacity_price_hourly = round(float(price_per_unit)/730, 15)
                            else:
                                raise Exception("More than one priceDimensions may exist: {}".format(str(price_list["terms"]["OnDemand"][key]["priceDimensions"].keys()))) 
                        else:
                            raise Exception("More than one offerTermCode may exist: {}".format(str(price_list["terms"]["OnDemand"].keys())))
                        ebs_price_json[supported_region][supported_ebs_type] = {
                            "capacity_price_hourly": capacity_price_hourly,
                            "thpt_price_hourly": 0,
                            "iops_price_hourly": 0,
                            "capacity_price_per_unit": price_per_unit,
                            "thpt_price_per_unit": 0,
                            "iops_price_per_unit": 0,
                            "currency": "USD",
                            "capacity_price_unit": unit,
                            "thpt_price_unit": "",
                            "iops_price_unit": "",
                            "capacity_price_description": description,
                            "location": location
                        }
                        filtered_ebs_cap_price_list.append(price_list)
                if len(filtered_ebs_cap_price_list) == 0:
                    print(("Cannot find {0} capacity price info in region {1}".format(supported_ebs_type, supported_region)) )       
                for price_list in ebs_perf_iops_price["PriceList"]:
                    if price_list["product"]["attributes"]["regionCode"] == supported_region and price_list["product"]["attributes"]["volumeApiName"] == supported_ebs_type and price_list["product"]["attributes"]["group"] == "EBS IOPS":
                        if len(price_list["terms"]["OnDemand"].keys()) == 1:                   
                            key = list(price_list["terms"]["OnDemand"].keys())[0]
                            if len(price_list["terms"]["OnDemand"][key]["priceDimensions"].keys()) == 1:
                                price_dimensions_key = list(price_list["terms"]["OnDemand"][key]["priceDimensions"].keys())[0]
                                iops_price_unit = price_list["terms"]["OnDemand"][key]["priceDimensions"][price_dimensions_key]["unit"]
                                #iops_price_description = price_list["terms"]["OnDemand"][key]["priceDimensions"][price_dimensions_key]["description"]
                                iops_price_per_unit = round(float(price_list["terms"]["OnDemand"][key]["priceDimensions"][price_dimensions_key]["pricePerUnit"]["USD"]), 30)
                                iops_price_hourly = round(float(iops_price_per_unit)/730, 30)
                            else:
                                raise Exception("More than one priceDimensions may exist: {}".format(str(price_list["terms"]["OnDemand"][key]["priceDimensions"].keys()))) 
                        else:
                            raise Exception("More than one offerTermCode may exist: {}".format(str(price_list["terms"]["OnDemand"].keys())))
                        ebs_price_json[supported_region][supported_ebs_type]["iops_price_hourly"] = iops_price_hourly
                        ebs_price_json[supported_region][supported_ebs_type]["iops_price_per_unit"] = iops_price_per_unit
                        ebs_price_json[supported_region][supported_ebs_type]["iops_price_unit"] = iops_price_unit
                        filtered_ebs_iops_price_list.append(price_list)   
                if len(filtered_ebs_iops_price_list) == 0:
                    print(("Cannot find {0} IOPS price info in region {1}".format(supported_ebs_type, supported_region)) )
                for price_list in ebs_perf_thpt_price["PriceList"]:
                    if price_list["product"]["attributes"]["regionCode"] == supported_region and price_list["product"]["attributes"]["volumeApiName"] == supported_ebs_type and price_list["product"]["attributes"]["group"] == "EBS Throughput":
                        if len(price_list["terms"]["OnDemand"].keys()) == 1:                   
                            key = list(price_list["terms"]["OnDemand"].keys())[0]
                            if len(price_list["terms"]["OnDemand"][key]["priceDimensions"].keys()) == 1:
                                price_dimensions_key = list(price_list["terms"]["OnDemand"][key]["priceDimensions"].keys())[0]
                                thpt_price_unit = price_list["terms"]["OnDemand"][key]["priceDimensions"][price_dimensions_key]["unit"]
                                thpt_price_per_unit = round(float(price_list["terms"]["OnDemand"][key]["priceDimensions"][price_dimensions_key]["pricePerUnit"]["USD"]), 30)
                                thpt_price_hourly = round(float(thpt_price_per_unit)/730, 10)
                            else:
                                raise Exception("More than one priceDimensions may exist: {}".format(str(price_list["terms"]["OnDemand"][key]["priceDimensions"].keys()))) 
                        else:
                            raise Exception("More than one offerTermCode may exist: {}".format(str(price_list["terms"]["OnDemand"].keys())))
                        ebs_price_json[supported_region][supported_ebs_type]["thpt_price_hourly"] = thpt_price_hourly
                        ebs_price_json[supported_region][supported_ebs_type]["thpt_price_per_unit"] = thpt_price_per_unit
                        ebs_price_json[supported_region][supported_ebs_type]["thpt_price_unit"] = thpt_price_unit
                        filtered_ebs_thpt_price_list.append(price_list)   
                if len(filtered_ebs_thpt_price_list) == 0:
                    print(("Cannot find {0} throughput price info in region {1}".format(supported_ebs_type, supported_region)) )    
            elif supported_ebs_type == "st1":
                for price_list in ebs_cap_price["PriceList"]:
                    if price_list["product"]["attributes"]["regionCode"] == supported_region and price_list["product"]["attributes"]["volumeApiName"] == supported_ebs_type:
                        if len(price_list["terms"]["OnDemand"].keys()) == 1:                   
                            key = list(price_list["terms"]["OnDemand"].keys())[0]
                            location = price_list["product"]["attributes"]["location"]
                            if len(price_list["terms"]["OnDemand"][key]["priceDimensions"].keys()) == 1:
                                price_dimensions_key = list(price_list["terms"]["OnDemand"][key]["priceDimensions"].keys())[0]
                                unit = price_list["terms"]["OnDemand"][key]["priceDimensions"][price_dimensions_key]["unit"]
                                description = price_list["terms"]["OnDemand"][key]["priceDimensions"][price_dimensions_key]["description"]
                                price_per_unit = round(float(price_list["terms"]["OnDemand"][key]["priceDimensions"][price_dimensions_key]["pricePerUnit"]["USD"]), 15)
                                capacity_price_hourly = round(float(price_per_unit)/730, 15)
                            else:
                                raise Exception("More than one priceDimensions may exist: {}".format(str(price_list["terms"]["OnDemand"][key]["priceDimensions"].keys()))) 
                        else:
                            raise Exception("More than one offerTermCode may exist: {}".format(str(price_list["terms"]["OnDemand"].keys())))
                        ebs_price_json[supported_region][supported_ebs_type] = {
                            "capacity_price_hourly": capacity_price_hourly,
                            "capacity_price_per_unit": price_per_unit,
                            "currency": "USD",
                            "capacity_price_unit": unit,
                            "capacity_price_description": description,
                            "location": location
                        }
                        filtered_ebs_cap_price_list.append(price_list)
                if len(filtered_ebs_cap_price_list) == 0:
                    print(("Cannot find {0} capacity price info in region {1}".format(supported_ebs_type, supported_region)) )       
            else:
                raise Exception("Unsupported EBS type: {}".format(supported_ebs_type))
    f = open(ebs_price_json_path, 'w')
    json.dump(ebs_price_json, f, indent=2)
    f.close()

def update_efs_price_json(supported_regions, efs_price_path_ori):
    # EFS has two product family: 'Storage' and 'Provisioned Throughput' in the origianl price file
    # the "Storage" product family contains storageClass: ['Infrequent Access', 'EFS Storage', 'General Purpose', 'Archive', 'One Zone-Infrequent Access', 'One Zone-General Purpose', 'Infrequent Access-ET']
    # the 'Provisioned Throughput' product family contains throughputClass: ['Included', 'Provisioned']
    # current tco estimator only considers 'Storage' productmily with 'General Purpose' and 'One Zone-General Purpose' storageClass with Elastic Throughput mode
    # need to consider the read/write price in 'EFS Storage' storageClass, and throughput price in 'Provisioned Throughput' product family
    # the regions that not have One Zone-General Purpose capacity price: ap-south-2, ap-southeast-3, ap-southeast-4, eu-south-2, eu-central-2, me-central-1, il-central-1

    efs_price_json_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/efs-price.json"
    efs_price = load_json_data(efs_price_path_ori)
    efs_price_json = {}
    for supported_region in supported_regions:
        efs_price_json[supported_region] = {}
        filtered_efs_price_list = []
        filtered_efs_one_zone_price_list = []
        for price_list in efs_price["PriceList"]:
            if price_list["product"]["attributes"]["regionCode"] == supported_region and price_list["product"]["productFamily"] == "Storage":
                if price_list["product"]["attributes"]["storageClass"] == "General Purpose":
                    if len(price_list["terms"]["OnDemand"].keys()) == 1:                   
                        key = list(price_list["terms"]["OnDemand"].keys())[0]
                        storage_class = price_list["product"]["attributes"]["storageClass"]
                        location = price_list["product"]["attributes"]["location"]
                        if len(price_list["terms"]["OnDemand"][key]["priceDimensions"].keys()) == 1:
                            price_dimensions_key = list(price_list["terms"]["OnDemand"][key]["priceDimensions"].keys())[0]
                            unit = price_list["terms"]["OnDemand"][key]["priceDimensions"][price_dimensions_key]["unit"]
                            description = price_list["terms"]["OnDemand"][key]["priceDimensions"][price_dimensions_key]["description"]
                            price_per_unit = round(float(price_list["terms"]["OnDemand"][key]["priceDimensions"][price_dimensions_key]["pricePerUnit"]["USD"]), 15)
                        else:
                            raise Exception("More than one priceDimensions may exist: {}".format(str(price_list["terms"]["OnDemand"][key]["priceDimensions"].keys()))) 
                    else:
                        raise Exception("More than one offerTermCode may exist: {}".format(str(price_list["terms"]["OnDemand"].keys())))
                    efs_price_json[supported_region]["standard_storage"] = {
                        "price": price_per_unit,
                        "unit": unit,
                        "description": description,
                        "storage_class": storage_class,
                        "currency": "USD",
                        "location": location
                    }
                    filtered_efs_price_list.append(price_list)
                elif price_list["product"]["attributes"]["storageClass"] == "One Zone-General Purpose":
                    if len(price_list["terms"]["OnDemand"].keys()) == 1:                   
                        key = list(price_list["terms"]["OnDemand"].keys())[0]
                        storage_class = price_list["product"]["attributes"]["storageClass"]
                        location = price_list["product"]["attributes"]["location"]
                        if len(price_list["terms"]["OnDemand"][key]["priceDimensions"].keys()) == 1:
                            price_dimensions_key = list(price_list["terms"]["OnDemand"][key]["priceDimensions"].keys())[0]
                            unit = price_list["terms"]["OnDemand"][key]["priceDimensions"][price_dimensions_key]["unit"]
                            description = price_list["terms"]["OnDemand"][key]["priceDimensions"][price_dimensions_key]["description"]
                            price_per_unit = round(float(price_list["terms"]["OnDemand"][key]["priceDimensions"][price_dimensions_key]["pricePerUnit"]["USD"]), 15)
                        else:
                            raise Exception("More than one priceDimensions may exist: {}".format(str(price_list["terms"]["OnDemand"][key]["priceDimensions"].keys()))) 
                    else:
                        raise Exception("More than one offerTermCode may exist: {}".format(str(price_list["terms"]["OnDemand"].keys())))
                    efs_price_json[supported_region]["one_zone_storage"] = {
                        "price": price_per_unit,
                        "unit": unit,
                        "description": description,
                        "storage_class": storage_class,
                        "location": location
                    }
                    filtered_efs_one_zone_price_list.append(price_list)
        if len(filtered_efs_price_list) != 1 or len(filtered_efs_one_zone_price_list) != 1:
            print(("Somthing wrong on the EFS price info in region {0}, standard {1}, one zone standard {2}".format(supported_region, str(filtered_efs_price_list), str(filtered_efs_one_zone_price_list))) )    
    f = open(efs_price_json_path, 'w')
    json.dump(efs_price_json, f, indent=2)
    f.close()

'''
if __name__ == '__main__':
    supported_instance_types = get_supported_instance_types_all_onefs()
    supported_ebs_types = ["gp3", "st1"]
    supported_regions = get_supported_regions()
    supported_ec2_price_path_ori= generate_supported_ec2_price_json_file(supported_instance_types)
    supported_ec2_savings_plans_price_path_ori = generate_supported_ec2_savings_plans_price_json_file(supported_instance_types)
    # hard coded ebs type since we only have gp3 and st1 supported
    supported_ebs_capacity_price_path_ori = generate_supported_ebs_price_json_file(["gp3", "st1"], "Storage")
    supported_ebs_perf_iops_price_path_ori = generate_supported_ebs_price_json_file(["gp3"], "System Operation")
    supported_ebs_perf_thpt_price_path_ori = generate_supported_ebs_price_json_file(["gp3"], "Provisioned Throughput")
    efs_price_path_ori = generate_efs_price_json_file()
    # supported_ec2_price_path_ori= r"C:\vscode\psve-tco\tcocal\price\supported-instance-types-on-demand-price.json"
    # supported_ec2_savings_plans_price_path_ori = r"C:\vscode\psve-tco\tcocal\price\supported-instance-types-savings-plans-price.json"
    # supported_ebs_capacity_price_path_ori = r"C:\vscode\psve-tco\tcocal\price\supported-ebs-capacity-price.json"
    # supported_ebs_perf_iops_price_path_ori = r"C:\vscode\psve-tco\tcocal\price\supported-ebs-perf-iops-price.json"
    # supported_ebs_perf_thpt_price_path_ori = r"C:\vscode\psve-tco\tcocal\price\supported-ebs-perf-thpt-price.json"
    # efs_price_path_ori = r"C:\vscode\psve-tco\tcocal\price\efs-price-original.json"
    update_ec2_price_json(supported_instance_types, supported_regions, supported_ec2_price_path_ori, supported_ec2_savings_plans_price_path_ori)
    update_ebs_price_json(supported_ebs_types, supported_regions, supported_ebs_capacity_price_path_ori, supported_ebs_perf_iops_price_path_ori, supported_ebs_perf_thpt_price_path_ori)
    update_efs_price_json(supported_regions, efs_price_path_ori)
'''

# the below code was initially used for get price info locally
'''
def load_json_file(path):
    f = open(path)
    data = json.load(f)
    f.close()
    return data

# https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/fetching-price-list-manually-step-1.html
# Finding available AWS services, needed service code: AmazonEC2, AmazonEFS, and AmazonFSx
def download_aws_service_index():
    aws_service_index_url = 'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json'
    aws_service_index_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/service_index.json" 
    is_downloaded = False
    response = requests.get(aws_service_index_url)

    if response.status_code == 200:
        with open(aws_service_index_path, 'wb') as file:
            file.write(response.content)
        is_downloaded = True
        print(f"Downloaded '{aws_service_index_url}' to '{aws_service_index_path}'")
    else:
        print(f"Failed to download '{aws_service_index_url}'. Status code: {response.status_code}")
    return is_downloaded

def filter_aws_service_index_json(aws_service_index_path, filter):

    filtered_aws_service_index_json = {
        "formatVersion" : "",
        "disclaimer" : "",
        "publicationDate" : "",
        "offers" : {}
    }

    aws_service_index_json = load_json_file(aws_service_index_path)
    filtered_aws_service_index_json["formatVersion"] = aws_service_index_json["formatVersion"]
    filtered_aws_service_index_json["disclaimer"] = aws_service_index_json["disclaimer"]
    filtered_aws_service_index_json["publicationDate"] = aws_service_index_json["publicationDate"]
    for key in aws_service_index_json["offers"].keys():
        if key in filter:
           filtered_aws_service_index_json["offers"][key] = aws_service_index_json["offers"][key]
    
    return json.dumps(filtered_aws_service_index_json)

def get_service_current_version_index_url(aws_service_index_path, offer_code):
    aws_service_index_json = load_json_file(aws_service_index_path)
    service_current_version_index_url = aws_service_index_json["offers"][offer_code]["currentVersionUrl"]
    return service_current_version_index_url

# for service that has saving plan available, e.g. AmamzonEC2
def get_service_current_savingsplan_index_url(aws_service_index_path, offer_code):
    aws_service_index_json = load_json_file(aws_service_index_path)
    service_current_savingsplan_index_url = aws_service_index_json["offers"][offer_code]["currentSavingsPlanIndexUrl"]
    return service_current_savingsplan_index_url
    
# Download a specific service index json file for all regions
# Please notet that this index json file may 5GiB+
def download_service_current_version_index(aws_service_index_path, offer_code):
    pricing_endpoint = "https://pricing.us-east-1.amazonaws.com"
    service_current_version_index_url = pricing_endpoint + get_service_current_version_index_url(aws_service_index_path, offer_code)
    service_current_version_index_path = os.path.dirname(os.path.abspath(__file__)) + r"/price/" + offer_code + "_current_version_index.json"
    #service_current_version_index_path = r"C:\vscode\psve-tco\tcocal" + r"/price/" + offer_code + "_current_version_index.json"
    is_downloaded = False
    response = requests.get(service_current_version_index_url)

    if response.status_code == 200:
        with open(service_current_version_index_path, 'wb') as file:
            file.write(response.content)
        is_downloaded = True
        print(f"Downloaded '{service_current_version_index_path}' to '{service_current_version_index_path}'")
    else:
        print(f"Failed to download '{service_current_version_index_path}'. Status code: {response.status_code}")
    return is_downloaded


def filter_ec2_service_json(service_current_version_index_path, filter):
    return 1
'''