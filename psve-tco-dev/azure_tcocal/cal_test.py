from azure_costcal import AzureFiles, AzureOnefsNode, AzureOnefsCluster

onefs_version = "OneFS 9.8"
region = "southcentralus"
vm_size = "Standard_D32ds_v5"
node_amount = 6
data_disk_tier = "P30"
data_disk_amount = 5
application_size = 1000
dataset_drr_ration = 1.0
license_contract_term = '3 Years' 
license_discount = 83
protection_level = "2n"
azure_onefs_node = AzureOnefsNode(region, onefs_version, vm_size, data_disk_tier, data_disk_amount)
azure_onefs_cluster = AzureOnefsCluster(license_contract_term=license_contract_term, license_discount=license_discount, node=azure_onefs_node, node_amount=node_amount, drr_ratio=dataset_drr_ration, protection_level=protection_level)
cluster_vm_monthly_cost = azure_onefs_cluster.cal_cluster_vm_monthly_cost_pay_as_you_go()
cluster_disk_monthly_cost = azure_onefs_cluster.cal_cluster_disk_monthly_cost_pay_as_you_go()
cluster_vm_monthly_cost_savings_plan = azure_onefs_cluster.cal_cluster_vm_monthly_cost_savings_plan(saving_plan_term=license_contract_term)
cluster_onefs_license_cost = azure_onefs_cluster.cal_cluster_onefs_license_monthly_cost()
cluster_monthly_cost = azure_onefs_cluster.cal_cluster_vm_monthly_cost_pay_as_you_go() + azure_onefs_cluster.cal_cluster_disk_monthly_cost_pay_as_you_go()
print(cluster_vm_monthly_cost_savings_plan)
print(cluster_onefs_license_cost)
print(cluster_vm_monthly_cost)
print(cluster_disk_monthly_cost)
print(cluster_monthly_cost)


cluster_effective_capacity = azure_onefs_cluster.cal_cluster_effective_capacity() * 1024 # GiB
azure_files = AzureFiles(region=region, capacity_gib=cluster_effective_capacity, tier = "premium_ssd_LRS")
print(azure_files.capacity_gib/1024)
print(azure_files.cal_azure_files_monthly_cost_reservation(reservation_term=license_contract_term))

