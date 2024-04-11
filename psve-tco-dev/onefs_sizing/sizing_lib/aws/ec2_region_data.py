import json

class EC2RegionData:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance    
    
    def __init__(self, ec2_region_data_path='tcocal/price/ec2-price.json'):
        # Example value of perf_data_path: 'tcocal/price/ec2-price.json'
        with open(ec2_region_data_path, 'r') as ec2_region_data_file:
            self.ec2_region_data = json.load(ec2_region_data_file)

    # Example of inst_type is "m5dn.12xlarge"
    def IsInstanceSupportedInRegion(self, inst_type, aws_region):
        if inst_type in self.ec2_region_data[aws_region].keys():
            return True
        else:
            return False

# Test if the function IsInstanceSupportedInRegion works.
# Will put this function in unit test later.
def testRegion():        
    ec2_region_data = EC2RegionData()
    m6idn_12x_in_region = ec2_region_data.IsInstanceSupportedInRegion('m6idn.12xlarge', 'me-south-1')
    i3en_12x_in_region = ec2_region_data.IsInstanceSupportedInRegion('i3en.12xlarge', 'me-south-1')

    print(m6idn_12x_in_region)
    print(i3en_12x_in_region)