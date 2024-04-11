import dash
from dash import Dash, html, dcc, callback, Output, Input, State, dash_table
import plotly.express as px
import pandas as pd
from tcocal.cal_config import cal_config
from tcocal.costcal import HOURS_PER_MONTH, Ec2Instance, EbsVolume, EfsStorage, AwsOnefsNode, AwsOnefsCluster
from flask import request
import datetime
import git, socket

dash.register_page(__name__, path='/aws-tco')


onefs_versions = cal_config.get_supported_onefs_versions()
default_aws_region = 'us-east-1'
supported_regions = ['us-east-1']
supported_instance_types = ['m5dn.8xlarge']
default_instance_type = 'm5dn.8xlarge'
node_amount_options = [6]
# define some default values
node_disk_amount_options = [12]
node_disk_size_min = 1
node_disk_size_max = 16
node_disk_size_step = 0.1

platforms = [
    'OneFS on AWS Annual Costs - USD', 
    'EFS Standard Storage Annual Costs - USD', 
    'EFS One Zone Storage Annual Costs - USD'
]
annual_aws_ec2_cost = [0, 0, 0]
annual_aws_storage_cost = [0, 0, 0]
annual_license_cost = [0, 0, 0]
wide_df = pd.DataFrame(
    {
        'Platforms': platforms,
        'Annual AWS Storage Cost - USD': annual_aws_storage_cost,
        'Annual AWS EC2 Cost - USD': annual_aws_ec2_cost,
        'Annual License Cost - USD': annual_license_cost
    }
)

fig = px.bar(wide_df, x="Platforms", y=["Annual AWS Storage Cost - USD", "Annual AWS EC2 Cost - USD", "Annual License Cost - USD"], title="Annual Cost Compare to Amazon EFS", text_auto=True)



# Cost breakdown table data
data = {
        'Cost categories': [
            'Annual AWS EC2 Cost - USD', 
            'Annual AWS Storage Cost - USD', 
            'Annual License Cost - USD', 
            'Annual Total Solution Cost - USD', 
            'Total Raw Capacity (TiB)', 
            'Total Effective Capacity to Clients (TiB)', 
            'Annual Effective Capacity Cost (USD/TiB)'
        ],
        'OneFS on AWS': [0, 0, 0, 0, 0, 0, 0],
        'EFS Standard Storage': [0, 0, 0, 0, 'N/A', 0, 0],
        'EFS One Zone Storage': [0, 0, 0, 0, 'N/A', 0, 0]
    }

df = pd.DataFrame(data)

cost_table_columns = [{'name': col, 'id': col} for col in df.columns]
cost_table_data = df.to_dict('records')

# Get the current git branch
branch = git.Repo('.', search_parent_directories=True).active_branch.name
ip_address = socket.gethostbyname(socket.gethostname())

if branch == 'main' and ip_address == '10.246.159.130':
    owa_tracking_js_src = "assets/owa-tracking-main.js"
elif branch == 'dev':
    owa_tracking_js_src = "assets/owa-tracking-dev.js"
else:
    owa_tracking_js_src = ""

layout = html.Div(children=[
    html.H1(children='APEX File Storage for AWS TCO Estimator and Comparison', style={'textAlign':'center'}),
    html.Script(src=owa_tracking_js_src, type="text/javascript"),
    html.Div(children=[
        html.Div(children=[
            html.P('Select a OneFS Version:'),
            dcc.Dropdown(options=onefs_versions, value=onefs_versions[len(onefs_versions)-1], id='onefs-version', style={'width': '300px'}, searchable=False)
        ]),
        html.Div(children=[
            html.P('Select an AWS Region:'),
            dcc.Dropdown(options=supported_regions, value=default_aws_region, id='aws-region', style={'width': '300px'}, searchable=False)
        ]),
        html.Div(children=[
            html.P('Select a OneFS License Contract Term (Includes ProSupport Plus for APEX File Storage for Public Coud):'),
            dcc.Dropdown(['1-year', '3-years'], '3-years', id='onefs-contract-term', style={'width': '300px'}, searchable=False)
        ]),
        html.Div(children=[
            html.P('Enter a OneFS License Discount Percentage:'),
            dcc.Input(min=0, max=100, step=1, value=83, id='onefs-license-discount', type='number', style={'width': '300px'})
        ]),
        html.Div(children=[
            html.P('Select an instance type:'),
            dcc.Dropdown(options=supported_instance_types, value=default_instance_type, id='instance-type', style={'width': '300px'}, searchable=False),
        ]),
        html.Div(children=[
            html.P('Select a data disk type:'),
            dcc.Dropdown(options=['gp3', 'st1'], value='gp3', id='disk-type', style={'width': '300px'}, searchable=False)
        ]),
        html.Div(children=[
            html.P('Enter an IOPS per gp3 volume:'),
            dcc.Input(min=3000, max=16000, step=1, value=3000, id='gp3-iops', type='number', style={'width': '300px'}),
            html.Br(), 
            html.Small('Min: 3000 IOPS, Max: 16000 IOPS. The value must be an integer.', style={'color': 'gray'}),
            html.P('Enter a throughput (MiB/s) per gp3 volume:'),
            dcc.Input(min=125, max=1000, step=1, value=125, id='gp3-thpt', type='number', style={'width': '300px'}),
            html.Br(), 
            html.Small('Min: 125 MiB, Max: 1000 MiB/s. Ensure throughput/iops <= 0.25', style={'color': 'gray'}),
        ], id='gp3-perf-div', style={'display': 'block'}),
        html.Div(children=[
            html.P('Select the desired number of nodes in the cluster:'),
            dcc.Dropdown(options=node_amount_options, value=6, id='node-amount', style={'width': '300px'}, searchable=False)
        ]),
        html.Div(children=[
            html.P('Select the desired number of data disks in each node:'),
            dcc.Dropdown(options=node_disk_amount_options, value=12, id='node-disk-amount', style={'width': '300px'}, searchable=False)
        ]),
        
        html.Div(children=[
            html.P('Select the desired raw size of each data disk. (TiB):'),
            dcc.Input(min=node_disk_size_min, max=node_disk_size_max, step=node_disk_size_step, value=5.000, id='node-disk-size', type='number', style={'width': '300px'}),
            html.Br(), 
            html.Small(id='node-disk-size-small', style={'color': 'gray'}),
        ]),
        
        html.Div(children=[
            html.P('Select an Amazon EC2 payment options:'),
            dcc.Dropdown(['on-demand', 'ec2-saving-plan-3-years-no-upfront'], 'ec2-saving-plan-3-years-no-upfront', id='ec2-payment-option', style={'width': '300px'}, searchable=False)
        ]),
        html.Div(children=[
            html.P('Enter an estimated data reduction ratio of OneFS for customer dataset:'),
            dcc.Input(min=1, max=10, step=0.1, value=1.6, id='onefs-drr-ratio', type='number', style={'width': '300px'})
        ]),
        html.Div(children=[
            html.Br(),
            html.Button('Calculate', id='submit-val', n_clicks=0, style={'background':'#0672CB', 'color':'white', 'border': 'none', 'padding': '10px 20px', 'font-size': '16px', 'border-radius': '4px', 'box-shadow': '0 8px 16px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19)'})
        ]),
    ], style={'float': 'left', 'width': '30%'}),
    html.Div(children=[
        dcc.Graph(id='results', figure=fig),
        html.P('Cost Breakdown Table', style={'textAlign': 'left'}),
        dash_table.DataTable(id='cost_table', columns=cost_table_columns, data=cost_table_data, style_table={'width': '800px'}, style_header={'textAlign': 'center'}, style_data={'textAlign': 'center'}),
        html.Div([
            #html.P("Notes:"),
            html.P("  *EFS One Zone storage provides continuous availability within a single AWS availability zone in a single AWS region.", style={'color': 'red'}),
            html.P("  *EFS Standard storage is designed to provide continuous availability across multiple AWS regions.", style={'color': 'red'}),
            html.P("  *OneFS on AWS is simillar to EFS One Zone, which is only available within a single AWS availability zone.",  style={'color': 'red'}),
            html.P("  *TCO includes Storage, compute and license cost, but it doesn't include network costs.",  style={'color': 'red'})   
        ]),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Div([html.P(" Pease contact Lieven Lin (lieven.lin@dell.com) if you have any issues and feedback.", style={'color': 'gray'})], style={'float': 'right', 'text-align': 'left'})
    ], style={'float': 'right', 'width': '70%'}),
])


# show supported regions based on OneFS version
@callback(
    Output(component_id='aws-region', component_property='options'),
    Output(component_id='aws-region', component_property='value'),
    Input(component_id='onefs-version', component_property='value')
)
def show_supported_aws_regions(onefs_version):
    global cal_config
    # supported_aws_regions = costcal.get_supported_regions(onefs_version)
    supported_aws_regions = cal_config.get_supported_regions(onefs_version)
    return supported_aws_regions, supported_aws_regions[0]


# show supported instance types based on aws region input
@callback(
    Output(component_id='instance-type', component_property='options'),
    Output(component_id='instance-type', component_property='value'),
    Input(component_id='onefs-version', component_property='value'),
    Input(component_id='aws-region', component_property='value')
)
def show_supported_instance_types(onefs_version, aws_region):
    global cal_config
    # supported_instance_types = costcal.get_supported_instance_types(onefs_version, aws_region)
    supported_instance_types = cal_config.get_supported_instance_types(onefs_version, aws_region)
    return supported_instance_types, supported_instance_types[0]


@callback(
    Output(component_id='node-amount', component_property='options'),
    Output(component_id='node-amount', component_property='value'),
    Input(component_id='onefs-version', component_property='value')
)
def show_supported_node_amount_options(onefs_version):
    global cal_config
    #supported_node_amount_options = clsconfig.get_supported_cluster_node_amount(onefs_version)
    supported_node_amount_options = cal_config.get_supported_cluster_node_amount(onefs_version)
    return supported_node_amount_options, supported_node_amount_options[0]

# visibility of gp3 perf input
@callback(
    Output(component_id='gp3-perf-div', component_property='style'), 
    Input(component_id='disk-type', component_property='value')
)
def gp3_perf_div_visibility(disk_type):
    # Toggle the visibility of the div based on button clicks
    if disk_type == "gp3":
        return {'display': 'block'}
    else:
        return {'display': 'none'}

#show different supported node disk amount and size config based on onefs version and disk type input
@callback(
    Output(component_id='node-disk-amount', component_property='options'),
    Output(component_id='node-disk-size', component_property='min'),
    Output(component_id='node-disk-size', component_property='max'),
    Output(component_id='node-disk-size', component_property='step'),
    Output(component_id='node-disk-size-small', component_property='children'),
    Input(component_id='onefs-version', component_property='value'),
    Input(component_id='disk-type', component_property='value')
)
def show_disk_amount(onefs_version, disk_type):
    global cal_config
    supported_node_disk_amount = cal_config.get_supported_node_disk_amount(onefs_version, disk_type)
    supported_node_disk_size = cal_config.get_supported_node_disk_size(onefs_version, disk_type)
    supported_node_disk_size_min = supported_node_disk_size[0]
    supported_node_disk_size_max = supported_node_disk_size[1]
    supported_node_disk_size_step = supported_node_disk_size[2]
    if disk_type == "gp3":
        node_disk_size_small = "Min: 1 TiB, Max: 16 TiB. Any size between Min and Max is allowed."
    elif disk_type == "st1":
        node_disk_size_small = "Allow 4 TiB or 10 TiB for a single st1 volume."
    return supported_node_disk_amount, supported_node_disk_size_min, supported_node_disk_size_max, supported_node_disk_size_step, node_disk_size_small

# show cost results figure and table
@callback(
    Output(component_id='results', component_property='figure'),
    Output(component_id='cost_table', component_property='columns'),
    Output(component_id='cost_table', component_property='data'),
    Input(component_id='submit-val', component_property='n_clicks'),
    State(component_id='onefs-version', component_property='value'),
    State(component_id='aws-region', component_property='value'),
    State(component_id='onefs-contract-term', component_property='value'),
    State(component_id='onefs-license-discount', component_property='value'),
    State(component_id='instance-type', component_property='value'),
    State(component_id='disk-type', component_property='value'),
    State(component_id='node-amount', component_property='value'),
    State(component_id='node-disk-amount', component_property='value'),
    State(component_id='node-disk-size', component_property='value'),
    State(component_id='ec2-payment-option', component_property='value'),
    State(component_id='onefs-drr-ratio', component_property='value'),
    State(component_id='gp3-iops', component_property='value'),
    State(component_id='gp3-thpt', component_property='value')
)
def show_results(n_clicks, onefs_version, aws_region, onefs_contract_term, onefs_license_discount, instance_type, disk_type, node_amount, node_disk_amount, node_disk_size, ec2_payment_option, onefs_drr_ratio, gp3_iops, gp3_thpt):
    global cal_config
    ec2_instance = Ec2Instance(instance_type, aws_region,ec2_payment_option)
    # remember to convert to GiB for all storage related size
    ebs_volume = EbsVolume(disk_type, aws_region, node_disk_size*1024, volume_iops=gp3_iops, volume_thpt=gp3_thpt)
    node = AwsOnefsNode(onefs_version, ec2_instance, ebs_volume, node_disk_amount)
    cluster = AwsOnefsCluster(aws_region, onefs_contract_term, onefs_license_discount, node, node_amount, onefs_drr_ratio, protection_level="2n")
    cluster_raw_capacity_gib = cluster.cal_cluster_raw_capacity()
    cluster_effective_capacity_gib = cluster.cal_cluster_effective_capacity()
    cluster_effective_capacity_tib = cluster_effective_capacity_gib / 1024
    cluster_ec2_hourly_cost = cluster.cal_cluster_ec2_hourly_cost(cal_config.ec2_price)
    cluster_ebs_monthly_cost = cluster.cal_cluster_ebs_monthly_cost(cal_config.ebs_price)
    cluster_onefs_monthly_cost = cluster.cal_cluster_onefs_monthly_cost(cal_config.onefs_license_price)
    
    
    
    platforms = ['OneFS on AWS Annual Costs - USD', 'EFS Standard Storage Annual Costs - USD', 'EFS One Zone Storage Annual Costs - USD']
    annual_aws_ec2_cost = [0, 0, 0]
    annual_aws_storage_cost = [0, 0, 0]
    annual_license_cost = [0, 0, 0]

    # Cost breakdown table data
    data = {
        'Cost categories': [
            'Annual AWS EC2 Cost - USD', 
            'Annual AWS Storage Cost - USD', 
            'Annual License Cost - USD', 
            'Annual Total Solution Cost - USD', 
            'Total Raw Capacity (TiB)', 
            'Total Effective Capacity to Clients (TiB)', 
            'Annual Effective Capacity Cost (USD/TiB)'
        ],
        'OneFS on AWS': [0, 0, 0, 0, 0, 0, 0],
        'EFS Standard Storage': [0, 0, 0, 0, 'N/A', 0, 0],
        'EFS One Zone Storage': [0, 0, 0, 0, 'N/A', 0, 0]
    }

    
    if n_clicks > 0:
        annual_aws_ec2_cost[0] = 12 * cluster_ec2_hourly_cost * HOURS_PER_MONTH
        annual_aws_storage_cost[0] = 12 * cluster_ebs_monthly_cost
        annual_license_cost[0] = 12 * cluster_onefs_monthly_cost
    
        data['OneFS on AWS'][0] = round(annual_aws_ec2_cost[0], 2)
        data['OneFS on AWS'][1] = round(annual_aws_storage_cost[0], 2)
        data['OneFS on AWS'][2] = round(annual_license_cost[0], 2)
        data['OneFS on AWS'][3] = round(annual_aws_ec2_cost[0] + annual_aws_storage_cost[0] + annual_license_cost[0], 2)
        data['OneFS on AWS'][4] = round(cluster_raw_capacity_gib/1024, 2)
        data['OneFS on AWS'][5] = round(cluster_effective_capacity_tib, 2)
        data['OneFS on AWS'][6] = round((annual_aws_ec2_cost[0] + annual_aws_storage_cost [0] + annual_license_cost[0])/cluster_effective_capacity_tib, 2)
        
        efs_storage_standard = EfsStorage(aws_region, "standard_storage", cluster_effective_capacity_gib)
        efs_storage_standard_monthly_cost = efs_storage_standard.cal_efs_monthly_cost(cal_config.efs_price)
        annual_aws_storage_cost[1] = 12 * efs_storage_standard_monthly_cost
        annual_license_cost[1] = 0
        data['EFS Standard Storage'][1] = round(annual_aws_storage_cost[1], 2)
        data['EFS Standard Storage'][3] = round(annual_aws_storage_cost[1], 2)
        data['EFS Standard Storage'][5] = round(cluster_effective_capacity_tib, 2)
        data['EFS Standard Storage'][6] = round(annual_aws_storage_cost[1]/cluster_effective_capacity_tib, 2)
        
        # One Zone Storage EFS related cost
        # the regions that does not have One Zone-General Purpose capacity price: ap-south-2, ap-southeast-3, ap-southeast-4, eu-south-2, eu-central-2, me-central-1, il-central-1
        if(aws_region in ["ap-south-2", "ap-southeast-3", "ap-southeast-4", "eu-south-2", "eu-central-2", "me-central-1", "il-central-1"]):
            annual_aws_storage_cost[2] = 0
            annual_license_cost[2] = 0
            data['EFS One Zone Storage'][1] = 'N/A'
            data['EFS One Zone Storage'][3] = 'N/A'
            data['EFS One Zone Storage'][5] = 'N/A'
            data['EFS One Zone Storage'][6] = 'N/A'
            data['EFS One Zone Storage'][7] = 'N/A'
            data['EFS One Zone Storage'][8] = 'N/A'
        else:
            efs_storage_one_zone = EfsStorage(aws_region, "one_zone_storage", cluster_effective_capacity_gib)
            efs_storage_one_zone_monthly_cost = efs_storage_one_zone.cal_efs_monthly_cost(cal_config.efs_price)
            annual_aws_storage_cost[2] = 12 * efs_storage_one_zone_monthly_cost
            annual_license_cost[2] = 0
            data['EFS One Zone Storage'][1] = round(annual_aws_storage_cost[2], 2)
            data['EFS One Zone Storage'][3] = round(annual_aws_storage_cost[2], 2)
            data['EFS One Zone Storage'][5] = round(cluster_effective_capacity_tib, 2)
            data['EFS One Zone Storage'][6] = round(annual_aws_storage_cost[2]/cluster_effective_capacity_tib, 2)
        
        # prepare data for result figure
        wide_data = pd.DataFrame({'Platforms': platforms,                            
                            'Annual AWS Storage Cost - USD': annual_aws_storage_cost,
                            'Annual AWS EC2 Cost - USD': annual_aws_ec2_cost,
                            'Annual License Cost - USD': annual_license_cost})

        fig = px.bar(wide_data, x="Platforms", y=["Annual AWS Storage Cost - USD", "Annual AWS EC2 Cost - USD", "Annual License Cost - USD"], title="Annual Cost Compare to Amazon EFS", text_auto=True, height=600)
        # prepare data for result table
        df = pd.DataFrame(data)
        cost_table_columns = [{'name': col, 'id': col} for col in df.columns]
        cost_table_data = df.to_dict('records') 
        print(datetime.datetime.now())
    else:
        wide_data = pd.DataFrame({'Platforms': platforms,
                            'Annual AWS Storage Cost - USD': annual_aws_storage_cost,
                            'Annual AWS EC2 Cost - USD': annual_aws_ec2_cost,
                            'Annual License Cost - USD': annual_license_cost})

        fig = px.bar(wide_data, x="Platforms", y=["Annual AWS Storage Cost - USD", "Annual AWS EC2 Cost - USD", "Annual License Cost - USD"], title="Annual Cost Compare to Amazon EFS", text_auto=True, height=600)
        df = pd.DataFrame(data)
        cost_table_columns = [{'name': col, 'id': col} for col in df.columns]
        cost_table_data = df.to_dict('records')
    print(request.remote_addr)
    return fig, cost_table_columns, cost_table_data
