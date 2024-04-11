import dash
from dash import Dash, html, dcc, callback, Output, Input, State, dash_table
import plotly.express as px
import pandas as pd
from azure_tcocal.azure_cal_config import azure_cal_config
from tcocal.costcal import HOURS_PER_MONTH, Ec2Instance, EbsVolume, EfsStorage, AwsOnefsNode, AwsOnefsCluster
from flask import request
import datetime

#dash.register_page(__name__, path='/azure-tco')

onefs_license_term = azure_cal_config.get_supported_onefs_license_term()
# Per PdM, 83% is the average discount that we provide on list price for customers. So some get 80%, some get 90% but more or less most of them get 83%
onefs_license_discount = 83
# when choosing savings plan, the savings plan term is same with onefs license term
azure_vm_payment_option = ["pay as you go", "savings plan"]

# parameters from sizing results
onefs_versions = ""
azure_region = ""
onefs_protection_level = "2n"
data_reduction_ratio = 1.0
azure_vm_size = ""
cluster_node_count = ""
cluster_node_disk_amount = ""
cluster_node_disk_tier = ""




# Cost breakdown table data
data = {
        'Cost categories': [
            'Annual Azure VM Cost - USD', 
            'Annual Azure Storage Cost - USD', 
            'Annual OneFS License Cost - USD', 
            'Annual Total Solution Cost - USD', 
            'Total Raw Capacity (TiB)', 
            'Total Effective Capacity to Clients (TiB)', 
            'Annual Effective Capacity Cost (USD/TiB)',
            'Max Write Throughput (GB/s)',
            'Max Read Throughput (GB/s)'
        ],
        'APEX File Storage for Azure': [0, 0, 0, 0, 0, 0, 0, 0, 0],
        'Azure Files Premium SSD LRS': [0, 0, 0, 0, 'N/A', 0, 0, 0, 0]
    }

df = pd.DataFrame(data)

cost_table_columns = [{'name': col, 'id': col} for col in df.columns]
cost_table_data = df.to_dict('records')

layout = html.Div(children=[
    html.H1(children='APEX File Storage for Azure TCO Estimator and Comparison', style={'textAlign':'center'}),
    html.Div(children=[
        html.P('This is a placeholder for showing the sizing result of custer configuration'),
    ]),
    html.Div(children=[
        html.P('Select a OneFS License Contract Term (Includes ProSupport Plus for APEX File Storage for Public Coud):'),
        dcc.Dropdown(onefs_license_term, '3-years', id='onefs-contract-term', style={'width': '300px'}, searchable=False)
    ]),
    html.Div(children=[
        html.P('Select an Amazon EC2 payment options:'),
        dcc.Dropdown(['on-demand', 'ec2-saving-plan-3-years-no-upfront'], 'ec2-saving-plan-3-years-no-upfront', id='ec2-payment-option', style={'width': '300px'}, searchable=False)
    ]),
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
    html.Div([html.P(" Pease contact Lieven Lin (lieven.lin@dell.com) if you have any issues and feedback.", style={'color': 'gray'})], style={'float': 'left', 'text-align': 'left'})

    # html.Div(children=[
    #     html.Div(children=[
    #         html.P('This is a placeholder for showing the sizing result of custer configuration'),
    #     ]),
    #     html.Div(children=[
    #         html.P('Select a OneFS License Contract Term (Includes ProSupport Plus for APEX File Storage for Public Coud):'),
    #         dcc.Dropdown(onefs_license_term, '3-years', id='onefs-contract-term', style={'width': '300px'}, searchable=False)
    #     ]),
    #     html.Div(children=[
    #         html.P('Select an Amazon EC2 payment options:'),
    #         dcc.Dropdown(['on-demand', 'ec2-saving-plan-3-years-no-upfront'], 'ec2-saving-plan-3-years-no-upfront', id='ec2-payment-option', style={'width': '300px'}, searchable=False)
    #     ])
    # ], style={'float': 'left', 'width': '30%'}),
    # html.Div(children=[
    #     html.P('Cost Breakdown Table', style={'textAlign': 'left'}),
    #     dash_table.DataTable(id='cost_table', columns=cost_table_columns, data=cost_table_data, style_table={'width': '800px'}, style_header={'textAlign': 'center'}, style_data={'textAlign': 'center'}),
    #     html.Div([
    #         #html.P("Notes:"),
    #         html.P("  *EFS One Zone storage provides continuous availability within a single AWS availability zone in a single AWS region.", style={'color': 'red'}),
    #         html.P("  *EFS Standard storage is designed to provide continuous availability across multiple AWS regions.", style={'color': 'red'}),
    #         html.P("  *OneFS on AWS is simillar to EFS One Zone, which is only available within a single AWS availability zone.",  style={'color': 'red'}),
    #         html.P("  *TCO includes Storage, compute and license cost, but it doesn't include network costs.",  style={'color': 'red'})   
    #     ]),
    #     html.Br(),
    #     html.Br(),
    #     html.Br(),
    #     html.Br(),
    #     html.Div([html.P(" Pease contact Lieven Lin (lieven.lin@dell.com) if you have any issues and feedback.", style={'color': 'gray'})], style={'float': 'right', 'text-align': 'left'})
    # ], style={'float': 'right', 'width': '70%'}),
])
