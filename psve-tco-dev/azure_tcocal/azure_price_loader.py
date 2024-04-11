import requests
import json
import re
from tabulate import tabulate 

# Azure Retail Prices API
# https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices
API_URL = "https://prices.azure.com/api/retail/prices?api-version=2023-01-01-preview"

def query_azure_vm_price(query_params: str):
    vm_price = []
    response = requests.get(API_URL, params={'$filter': query_params})
    json_data = json.loads(response.text)
    for item in json_data['Items']: 
        vm_price.append(item)
    nextPage = json_data['NextPageLink']
    
    while(nextPage):
        response = requests.get(nextPage)
        json_data = json.loads(response.text)
        nextPage = json_data['NextPageLink']
        for item in json_data['Items']: 
            vm_price.append(item)

    return vm_price

def query_azure_managed_disk_price(query_params: str):
    disk_price = []
    response = requests.get(API_URL, params={'$filter': query_params})
    json_data = json.loads(response.text)
    for item in json_data['Items']: 
        disk_price.append(item)
    nextPage = json_data['NextPageLink']
    
    while(nextPage):
        response = requests.get(nextPage)
        json_data = json.loads(response.text)
        nextPage = json_data['NextPageLink']
        for item in json_data['Items']: 
            disk_price.append(item)

    return disk_price


def query_anf_price(query_params: str):
    anf_price = []
    response = requests.get(API_URL, params={'$filter': query_params})
    json_data = json.loads(response.text)
    for item in json_data['Items']: 
        anf_price.append(item)
    nextPage = json_data['NextPageLink']
    
    while(nextPage):
        response = requests.get(nextPage)
        json_data = json.loads(response.text)
        nextPage = json_data['NextPageLink']
        for item in json_data['Items']: 
            anf_price.append(item)

    return anf_price

def query_azure_files_price(query_params: str):
    azure_files_price = []
    response = requests.get(API_URL, params={'$filter': query_params})
    json_data = json.loads(response.text)
    for item in json_data['Items']: 
        azure_files_price.append(item)
    nextPage = json_data['NextPageLink']
    
    while(nextPage):
        response = requests.get(nextPage)
        json_data = json.loads(response.text)
        nextPage = json_data['NextPageLink']
        for item in json_data['Items']: 
            azure_files_price.append(item)

    return azure_files_price

def get_azure_vm_price():
    vm_sizes = [
        "Standard_D32d_v5", "Standard_D48d_v5", "Standard_D64d_v5", "Standard_D96d_v5", 
        "Standard_D32ds_v5", "Standard_D48ds_v5", "Standard_D64ds_v5", "Standard_D96ds_v5", 
        "Standard_E32d_v5", "Standard_E48d_v5", "Standard_E64d_v5", "Standard_E96d_v5", "Standard_E104id_v5",
        "Standard_E32ds_v5", "Standard_E48ds_v5", "Standard_E64ds_v5", "Standard_E96ds_v5", "Standard_E104ids_v5"
    ]
    vm_price_temp = {
        "Standard_D32d_v5": {
            "pay-as-you-go": {
                
            },
            "reservation": {
                "1 Year": "",
                "3 Years": ""
            }
        },
        "Standard_D48d_v5": {
            "pay-as-you-go": {
                
            },
            "reservation": {
                "1 Year": "",
                "3 Years": ""
            }
        },
        "Standard_D64d_v5": {
            "pay-as-you-go": {
                
            },
            "reservation": {
                "1 Year": "",
                "3 Years": ""
            }
        },
        "Standard_D96d_v5": {
            "pay-as-you-go": {
                
            },
            "reservation": {
                "1 Year": "",
                "3 Years": ""
            }
        },
        "Standard_D32ds_v5": {
            "pay-as-you-go": {
                
            },
            "reservation": {
                "1 Year": "",
                "3 Years": ""
            }
        },
        "Standard_D48ds_v5": {
            "pay-as-you-go": {
                
            },
            "reservation": {
                "1 Year": "",
                "3 Years": ""
            }
        },
        "Standard_D64ds_v5": {
            "pay-as-you-go": {
                
            },
            "reservation": {
                "1 Year": "",
                "3 Years": ""
            }
        },
        "Standard_D96ds_v5": {
            "pay-as-you-go": {
                
            },
            "reservation": {
                "1 Year": "",
                "3 Years": ""
            }
        },
        "Standard_E32d_v5": {
            "pay-as-you-go": {
                
            },
            "reservation": {
                "1 Year": "",
                "3 Years": ""
            }
        },
        "Standard_E48d_v5": {
            "pay-as-you-go": {
                
            },
            "reservation": {
                "1 Year": "",
                "3 Years": ""
            }
        },
        "Standard_E64d_v5": {
            "pay-as-you-go": {
                
            },
            "reservation": {
                "1 Year": "",
                "3 Years": ""
            }
        },
        "Standard_E96d_v5": {
            "pay-as-you-go": {
                
            },
            "reservation": {
                "1 Year": "",
                "3 Years": ""
            }
        },
        "Standard_E104id_v5": {
            "pay-as-you-go": {
                
            },
            "reservation": {
                "1 Year": "",
                "3 Years": ""
            }
        },
        "Standard_E32ds_v5": {
            "pay-as-you-go": {
                
            },
            "reservation": {
                "1 Year": "",
                "3 Years": ""
            }
        },
        "Standard_E48ds_v5": {
            "pay-as-you-go": {
                
            },
            "reservation": {
                "1 Year": "",
                "3 Years": ""
            }
        },
        "Standard_E64ds_v5": {
            "pay-as-you-go": {
                
            },
            "reservation": {
                "1 Year": "",
                "3 Years": ""
            }
        },
        "Standard_E96ds_v5": {
            "pay-as-you-go": {
                
            },
            "reservation": {
                "1 Year": "",
                "3 Years": ""
            }
        },
        "Standard_E104ids_v5": {
            "pay-as-you-go": {
                
            },
            "reservation": {
                "1 Year": "",
                "3 Years": ""
            }
        }
    }

    for vm_size in vm_sizes:
        # get vm series by replacing the the number in the vm size, e.g. Standard_D32d_v5 -> D32dv5, Standard_E104id_v5 -> Edv5
        vm_series = re.sub(r'\d+i?', '', vm_size.split("_")[1]) + vm_size.split("_")[2]
        meter_name = vm_size.split("_")[1] + " " + vm_size.split("_")[2]
        vm_price_query = f"currencyCode eq 'USD' and armRegionName eq 'southcentralus' and serviceName eq 'Virtual Machines' and serviceFamily eq 'Compute' and armSkuName eq '{vm_size}' and productName eq 'Virtual Machines {vm_series} Series' and meterName eq '{meter_name}'"
        vm_prices = query_azure_managed_disk_price(vm_price_query)
        if len(vm_prices) == 0:
            raise Exception(f"VM prices not found {vm_size}")
        elif len(vm_prices) == 1 or len(vm_prices) == 2:
            raise Exception("VM prices is not sufficient. {}".format(vm_prices))
        elif len(vm_prices) == 3:
            for vm_price in vm_prices:
                if vm_price['type'] == "Reservation" and vm_price['reservationTerm'] == "1 Year":
                    vm_price_temp[vm_size]["reservation"]["1 Year"] = vm_price
                elif vm_price['type'] == "Reservation" and vm_price['reservationTerm'] == "3 Years":
                    vm_price_temp[vm_size]["reservation"]["3 Years"] = vm_price
                else:
                    vm_price_temp[vm_size]["pay-as-you-go"] = vm_price
        else:
            raise Exception("VM prices is too much. {}".format(vm_prices))

    return vm_price_temp

def get_premium_ssd_price():
    premium_ssd = ["P20", "P30", "P40", "P50", "P60", "P70"]
    premium_ssd_temp = {
      "P20":{
          "pay-as-you-go": "", 
          "reservation": ""
      },
      "P30":{
          "pay-as-you-go": "", 
          "reservation": ""
      },
      "P40":{
          "pay-as-you-go": "", 
          "reservation": ""
      },
      "P50":{
            "pay-as-you-go": "", 
            "reservation": ""
      },
      "P60":{
          "pay-as-you-go": "", 
          "reservation": ""
      },
      "P70":{
          "pay-as-you-go": "", 
          "reservation": ""
      }
    }

    for ssd in premium_ssd:
        disk_price_query = "currencyCode eq 'USD' and armRegionName eq 'southcentralus' and serviceName eq 'Storage' and serviceFamily eq 'Storage' and meterName eq '{} LRS Disk' and contains(productName, 'SSD Managed Disks')".format(ssd)
        disk_prices = query_azure_managed_disk_price(disk_price_query)
        if len(disk_prices) == 0:
            raise Exception("Disk prices not found")
        elif len(disk_prices) == 1:
            if ssd == "P20":
                premium_ssd_temp[ssd]["pay-as-you-go"] = disk_prices[0]
            else:
                raise Exception("Disk prices is not sufficient. {}".format(disk_prices))
        elif len(disk_prices) == 2:
            for disk_price in disk_prices:
                if disk_price['type'] == "Reservation":
                    premium_ssd_temp[ssd]["reservation"] = disk_price
                else:
                    premium_ssd_temp[ssd]["pay-as-you-go"] = disk_price
        else:
            raise Exception("Disk prices is too much. {}".format(disk_prices))

    return premium_ssd_temp

def get_standard_ssd_price():
    standard_ssd = ["E20", "E30", "E40", "E50", "E60", "E70"]
    standard_ssd_temp = {
      "E20": {
        "capacity": "",
        "transaction": ""
      },
      "E30": {
        "capacity": "",
        "transaction": ""
      },
      "E40": {
        "capacity": "",
        "transaction": ""
      },
      "E50": {
        "capacity": "",
        "transaction": ""
      },
      "E60": {
        "capacity": "",
        "transaction": ""
      },
      "E70": {
        "capacity": "",
        "transaction": ""
      }
    }

    for ssd in standard_ssd:
        disk_price_query = "currencyCode eq 'USD' and armRegionName eq 'southcentralus' and serviceName eq 'Storage' and serviceFamily eq 'Storage' and contains(meterName, '{} LRS Disk') and contains(productName, 'SSD Managed Disks')".format(ssd)
        disk_prices = query_azure_managed_disk_price(disk_price_query)
        if len(disk_prices) == 0:
            raise Exception("Disk prices not found")
        elif len(disk_prices) == 1:
            raise Exception("Disk prices is not sufficient. {}".format(disk_prices))
        elif len(disk_prices) == 3:
            for disk_price in disk_prices:
                if disk_price['meterName'] == "{} LRS Disk".format(ssd):
                    standard_ssd_temp[ssd]["capacity"] = disk_price
                elif disk_price['meterName'] == "{} LRS Disk Operations".format(ssd):
                    standard_ssd_temp[ssd]["transaction"] = disk_price
                elif disk_price['meterName'] == "{} LRS Disk Mount".format(ssd):
                    pass
                else:
                    raise Exception("Unexpected meterName {} was found".format(disk_price['meterName']))
        else:
            raise Exception("Disk prices is too much than expected 3. {}".format(disk_prices))

    return standard_ssd_temp

# get Azure NetApp Files price, anf_tier includes Ultra, Premium, Standard
def get_anf_price():
    anf_tiers = ["Ultra", "Premium", "Standard"]
    standard_ssd_temp = {
        "Ultra": {
        }, 
        "Premium": {
        }, 
        "Standard": {
        }
      }
    for anf_tier in anf_tiers:
        anf_price_query = f"armRegionName eq 'southcentralus' and serviceName eq 'Azure NetApp Files' and meterName eq '{anf_tier} Capacity' and productName eq 'Azure NetApp Files'"
        anf_prices = query_anf_price(anf_price_query)
        if len(anf_prices) == 0:
            raise Exception("Azure NetApp Files prices not found")
        elif len(anf_prices) == 1:
            standard_ssd_temp[anf_tier] = anf_prices[0]
        else:
            raise Exception("Disk prices is too much than expected 1. {}".format(anf_prices))

    return standard_ssd_temp

def build_pricing_table(json_data, table_data):
    for item in json_data['Items']:
        meter = item['meterName']
        # table_data.append([item['armSkuName'], item['reservationTerm'], item['retailPrice'], item['unitOfMeasure'], item['armRegionName'], meter, item['productName']])
        table_data.append([item['armSkuName'], item['retailPrice'], item['unitOfMeasure'], item['armRegionName'], item['location'], meter, item['productName']])

def price_show_table():
    table_data = []
    # table_data.append(['SKU', 'Retail Price', 'Unit of Measure', 'Region', 'Meter', 'Product Name'])
    # table_data.append(['SKU', 'Reservation Term','Retail Price', 'Unit of Measure', 'Region', 'Meter', 'Product Name'])
    table_data.append(['SKU', 'Retail Price', 'Unit of Measure', 'Region', 'Location', 'Meter', 'Product Name'])
    
    # api_url = "https://prices.azure.com/api/retail/prices"
    api_url = "https://prices.azure.com/api/retail/prices?api-version=2023-01-01-preview"
    # query = "armRegionName eq 'southcentralus' and armSkuName eq 'Standard_NP20s' and priceType eq 'Consumption' and contains(meterName, 'Spot')"
    # query = "armRegionName eq 'southcentralus' and serviceName eq 'Storage' and productName eq 'Files v2'"
    # query = "armRegionName eq 'southcentralus' and serviceName eq 'Storage' and contains(productName, 'Premium') and contains(meterName, 'LRS')"
    # query = "armRegionName eq 'southcentralus' and serviceName eq 'Storage' and contains(productName, 'Premium') and contains(productName, 'Reserved')"
    # query = "armRegionName eq 'southcentralus' and serviceName eq 'Storage' and contains(meterName, 'Provisioned') and contains(productName, 'Premium')"
    # query Azure Files price
    # query = "armRegionName eq 'southcentralus' and serviceName eq 'Storage' and contains(meterName, 'Provisioned') and contains(productName, 'Premium Files Reserved Capacity')"
    # query Azure VM price
    # query = "currencyCode eq 'USD' and armRegionName eq 'southcentralus' and serviceName eq 'Virtual Machines' and serviceFamily eq 'Compute' and armSkuName eq 'Standard_D32ds_v5' and productName eq 'Virtual Machines Ddsv5 Series'"
    # query Azure Managed Disk price
    # query = "currencyCode eq 'USD' and armRegionName eq 'southcentralus' and serviceName eq 'Storage' and serviceFamily eq 'Storage' and armSkuName eq 'Premium_SSD_Managed_Disks_P50' and contains(productName, 'Managed') and contains(meterName, 'LRS')"
    query = "armRegionName eq 'southcentralus' and serviceName eq 'Azure NetApp Files' and meterName eq 'Premium Capacity' and productName eq 'Azure NetApp Files'"
    response = requests.get(api_url, params={'$filter': query})
    json_data = json.loads(response.text)
    print(json_data)
    build_pricing_table(json_data, table_data)
    nextPage = json_data['NextPageLink']
    
    while(nextPage):
        response = requests.get(nextPage)
        json_data = json.loads(response.text)
        nextPage = json_data['NextPageLink']
        build_pricing_table(json_data, table_data)

    print(tabulate(table_data, headers='firstrow', tablefmt='psql'))
    
def main():
    
    vm_price_query = "currencyCode eq 'USD' and armRegionName eq 'southcentralus' and serviceName eq 'Virtual Machines' and serviceFamily eq 'Compute' and armSkuName eq 'Standard_D32ds_v5' and productName eq 'Virtual Machines Ddsv5 Series'"

    # price_show_table()
    # azure_files_price_query = "currencyCode eq 'USD' and armRegionName eq 'southcentralus' and serviceName eq 'Storage' and serviceFamily eq 'Storage' and contains(meterName, 'Provisioned') and contains(productName, 'Premium Files Reserved Capacity')"
    # premium_ssd_temp = get_premium_ssd_price()
    # print(premium_ssd_temp)
    # standard_ssd_temp = get_standard_ssd_price()
    # print(standard_ssd_temp)

    # vm_price_temp = get_azure_vm_price()
    # print(vm_price_temp)

    anf_price_temp = get_anf_price()
    print(anf_price_temp)

    # azure_files_price = query_azure_files_price(azure_files_price_query)

if __name__ == "__main__":
    main()


