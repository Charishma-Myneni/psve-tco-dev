import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, dash_table, State, callback
import pandas as pd
import plotly.graph_objs as go
import dash_ag_grid as dag
import git, socket

from onefs_sizing.sizing_lib.azure.azure_page_sizer_connector import SizeSolutionFromPage
from azure_tcocal.azure_costcal import AzureFiles, AzureOnefsNode, AzureOnefsCluster, AzureNetappFiles
from azure_tcocal.azure_cal_config import azure_cal_config

dash.register_page(__name__, path='/azure-sizer')

data_list = []
columns_with_btn = []
selected_rows = []
columnDefs = []

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
    html.Title(children='Azure Sizer'),
    html.Script(src=owa_tracking_js_src, type="text/javascript"),
    html.H2(children='APEX File Storage For Azure Sizing Tool', style={'textAlign':'center'}),
    html.H6("Note: This tool is still under development. Please contact yunlong.zhang@dell.com if you have any questions or suggestions.", style={"text-align": "center"}),
    html.Div(children=[
        html.P("Select OneFS Version:"),
        dcc.Dropdown(
            id="dropdown-az-version",
            options=["OneFS 9.8"],
            value="OneFS 9.8",
            className="w-50",
            clearable=False,
        ),
        html.P("Select Region:"),
        dcc.Dropdown(
            id="dropdown-region",
            options=["southcentralus"],
            value="southcentralus",
            className="w-50",
            clearable=False,
        ),
        html.P("Select Cluster Disk Type:"),
        dcc.Dropdown(
            id="dropdown-cluster-disk-type",
            options=["Standard HDD (not supported yet)", "Standard SSD", "Premium SSD"],
            value="Premium SSD",
            className="w-50",
            clearable=False,
        ),
        html.P("Select protection-level:"),
        dcc.Dropdown(
            id="dropdown-protection",
            options=["+2n", "+2d:1n"],
            value="+2n",
            className="w-50",
            clearable=False,
        ),
        html.P("Select a OneFS License Contract Term (Includes ProSupport Plus for APEX File Storage for Public Coud):"),
        dcc.Dropdown(
            id="dropdown-onefs-license-term",
            options=["1 Year", "3 Years"],
            value="3 Years",
            className="w-50",
            clearable=False,
        ),
        html.P("Select an Azure VM payment options:"),
        dcc.Dropdown(
            id="dropdown-azure-vm-payment-option",
            options=["pay as you go", "savings plan"], # when choosing savings plan, the savings plan term is same with onefs license term
            value="savings plan",
            className="w-50",
            clearable=False,
        ),
        html.P("Input Dataset Capacity (TiB):"),
        dcc.Input(
            id="input-capacity",
            value="100",
            className="w-100",
            placeholder="100",
        ),  
        html.P("Input Data Reduction Ratio (1.0 - 5.0):"),
        dcc.Input(
            id="input-drr",
            value="1.0",
            className="w-100",
            placeholder="1.0",
        ),  
        html.P("Input Read Throughput Performance Requirement (GB/sec/cluster):"),
        dcc.Input(
            id="input-read-tput",
            value="5",
            className="w-100",
            placeholder="5",
        ),
        html.P("Input Write Throughput Performance Requirement (GB/sec/cluster):"),
        dcc.Input(
            id="input-write-tput",
            value="1.2",
            className="w-100",
            placeholder="1.2",
        ),
        dbc.Button(
            "Show Sizing Results", id="btn-size-it", n_clicks=0
        )
    ], style={'float': 'left', 'width': '30%', 'padding-left': '20px'}),

    html.Div(children=[
        # Fifth section: show sizing result table.
        dbc.Row(
            [                
                dbc.Col(id='sizing-results', children = [
                    dag.AgGrid(
                    id="data-ag-grid",
                    columnDefs=columnDefs,
                    rowData=data_list,
                    columnSize="sizeToFit", # columnSize (a value equal to: 'sizeToFit', 'autoSize', 'responsiveSizeToFit' or null; optional): 
                    defaultColDef={"filter": True},
                    dashGridOptions={"rowSelection": "single", "pagination": True, "animateRows": False},
                    selectedRows=selected_rows
                ),
                ]),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H6("Select the sizing result you want to see details."),
                        html.H6("Note: The data reduction ratio is only for sizing the capacity. Samilar as PowerSizer, the read/write performance are measuring irreducible datasets."),
                    ]
                )
            ],
        ),
        html.Div(id='details-container'),

    ], style={'float': 'right', 'width': '70%', 'padding-left': '30px'}),
])

@callback(
    Output(component_id='data-ag-grid', component_property='rowData'),
    Output(component_id='data-ag-grid', component_property='columnDefs'),
    Output(component_id='data-ag-grid', component_property='selectedRows'),
    Input("btn-size-it", "n_clicks"),
    State("dropdown-az-version", "value"),
    State("dropdown-region", "value"),
    State("dropdown-cluster-disk-type", "value"),
    State("dropdown-protection", "value"),
    State("dropdown-onefs-license-term", "value"),
    State("dropdown-azure-vm-payment-option", "value"),    
    State("input-capacity", "value"),
    State("input-drr", "value"),
    State("input-read-tput", "value"),
    State("input-write-tput", "value"),
    allow_duplicate=True
)
def show_sizing_results(n_clicks, version, region, cluster_disk_type, protection, onefs_license_term, vm_payment_option, capacity, drr, read_tput, write_tput):
    data_list = []
    columns_with_btn = []
    columnDefs = []
    selected_rows = []
    if n_clicks > 0:
        # Prepare data for table
        data_list = SizeSolutionFromPage(version, region, cluster_disk_type, drr, capacity, protection, onefs_license_term, vm_payment_option, read_tput, write_tput, "Azure")
        if len(data_list) != 0: 
            # columns_with_btn = [{"name": i, "id": i} for i in data_list[0].keys()]
            columnDefs = [{"field": i} for i in data_list[0].keys()]
            # columns_with_btn.append({"name": "Action", "id": "Action", "presentation": "dropdown"})
        else:
            table_data = [
                {'Message': 1, 'Detail': 'No Valid Sizing Result. Your capacity requriement or performance is too high.'}
            ]
            data_list=table_data
            columnDefs = [{"field": i} for i in table_data[0].keys()]
            #columns_with_btn=[{"name": col, "id": col} for col in table_data[0].keys()]
    return data_list, columnDefs, selected_rows



@callback(
    Output('details-container', 'children'),
    [Input('data-ag-grid', 'selectedRows')],
    [State('data-ag-grid', 'rowData')],
    [State('dropdown-az-version', 'value')],
    [State('dropdown-region', 'value')],
    [State('dropdown-protection', 'value')],
    [State('input-drr', 'value')],
    State("dropdown-onefs-license-term", "value"),
    State("dropdown-azure-vm-payment-option", "value"),  
    allow_duplicate=True
)
def display_details(selected_rows, data, onefs_version, azure_region, onefs_protection_level, data_reduction_ratio, onefs_license_term, azure_vm_payment_option):
    if selected_rows and "Node Instance Type" in selected_rows[0].keys():
        # selected_row = data[selected_rows[0]]
        selected_row = selected_rows[0]
        # Per PdM, 83% is the average discount that we provide on list price for customers. So some get 80%, some get 90% but more or less most of them get 83%
        onefs_license_discount = 83
        azure_vm_size = selected_row["Node Instance Type"]
        cluster_node_count = selected_row["Cluster Node Count"]
        cluster_node_disk_amount = selected_row["Volumn Count Per Node"]
        cluster_node_disk_tier = selected_row["Volumn Type"]
        cluster_perf_read_tput = selected_row["Config Info"].split(",")[0].split(":")[1]
        cluster_pef_write_tput = selected_row["Config Info"].split(",")[1].split(":")[1]

        azure_onefs_node = AzureOnefsNode(azure_region, onefs_version, azure_vm_size, cluster_node_disk_tier, cluster_node_disk_amount)
        azure_onefs_cluster = AzureOnefsCluster(license_contract_term=onefs_license_term, license_discount=onefs_license_discount, node=azure_onefs_node, node_amount=cluster_node_count, drr_ratio=data_reduction_ratio, protection_level=onefs_protection_level)

        # Cost calculation
        if azure_vm_payment_option.lower() == "pay as you go":
            cluster_vm_monthly_cost = round(azure_onefs_cluster.cal_cluster_vm_monthly_cost_pay_as_you_go())
        elif azure_vm_payment_option.lower() == "savings plan":
            #print("monnthly saving plan cost: " + str(azure_onefs_cluster.node.cal_node_vm_monthly_cost_savings_plan(saving_plan_term=onefs_license_term)))
            cluster_vm_monthly_cost = round(azure_onefs_cluster.cal_cluster_vm_monthly_cost_savings_plan(saving_plan_term=onefs_license_term))
        cluster_disk_monthly_cost = round(azure_onefs_cluster.cal_cluster_disk_monthly_cost_pay_as_you_go())
        cluster_onefs_license_cost = round(azure_onefs_cluster.cal_cluster_onefs_license_monthly_cost())
        cluster_monthly_cost = round(cluster_vm_monthly_cost + cluster_disk_monthly_cost + cluster_onefs_license_cost)
        #print("cluster_vm_monthly_cost" + str(cluster_vm_monthly_cost))
        #print("cluster_disk_monthly_cost" + str(cluster_disk_monthly_cost))
        #print("cluster_onefs_license_cost" + str(cluster_onefs_license_cost))
        #print("cluster_monthly_cost" + str(cluster_monthly_cost))


        cluster_raw_capacity = round(azure_onefs_cluster.cal_cluster_raw_capacity()) # TiB
        cluster_effective_capacity = round(azure_onefs_cluster.cal_cluster_effective_capacity()) # TiB

        # # Azure Files
        # azure_files = AzureFiles(region=azure_region, capacity_gib=cluster_effective_capacity * 1024, tier = "premium_ssd_LRS")
        # azure_files_monthly_cost = azure_files.cal_azure_files_monthly_cost_reservation(reservation_term=onefs_license_term)
        # print("azure_files_monthly_cost" + str(azure_files_monthly_cost))

        # Azure NetApp Files
        azure_netapp_files_ultra = AzureNetappFiles(region=azure_region, capacity_tib=cluster_effective_capacity, tier = "Ultra")
        azure_netapp_files_ultra_monthly_cost = round(azure_netapp_files_ultra.cal_azure_netapp_files_monthly_cost())
        azure_netapp_files_throughput = round(azure_netapp_files_ultra.cal_azure_netapp_files_throughput(), 1) # GB/s

        # Total annual cost
        cluster_vm_annual_cost = round(cluster_vm_monthly_cost * 12)
        cluster_disk_annual_cost = round(cluster_disk_monthly_cost * 12,)
        cluster_onefs_license_annual_cost = round(cluster_onefs_license_cost * 12)
        cluster_annual_cost = round(cluster_monthly_cost * 12)
        azure_netapp_files_ultra_annual_cost = round(azure_netapp_files_ultra_monthly_cost * 12)

        
        # Cost breakdown table data
        data = {
                'Cost categories': [
                    'Monthly Azure VM Cost - USD', 
                    'Monthly Azure Storage Cost - USD', 
                    'Monthly License Cost - USD', 
                    'Monthly Total Solution Cost - USD', 
                    'Total Raw Capacity (TiB)', 
                    'Total Usable Capacity to Clients (TiB)', 
                    'Usable Capacity Monthly Cost (USD/TiB)'
                ],
                'APEX File Storage for Azure': [0, 0, 0, 0, 0, 0, 0],
                'Azure NetApp Files Ultra': [0, 0, 0, 0, 'N/A', 0, 0],
            }

        data['APEX File Storage for Azure'] = [cluster_vm_monthly_cost, cluster_disk_monthly_cost, cluster_onefs_license_cost, cluster_monthly_cost, cluster_raw_capacity, cluster_effective_capacity, round(cluster_monthly_cost/cluster_effective_capacity)]
        data['Azure NetApp Files Ultra'] = [0, azure_netapp_files_ultra_monthly_cost, 0, azure_netapp_files_ultra_monthly_cost, 'N/A', cluster_effective_capacity, round(azure_netapp_files_ultra_monthly_cost/cluster_effective_capacity, 1)]
    
        # Comparison Figure 
        figure_categories = ['APEX File Storage for Azure', 'Azure NetApp Files Ultra']
        figure_annual_vm_cost = [data['APEX File Storage for Azure'][0], data['Azure NetApp Files Ultra'][0]]
        figure_annual_storage_cost = [data['APEX File Storage for Azure'][1], data['Azure NetApp Files Ultra'][1]]
        figure_annual_license_cost = [data['APEX File Storage for Azure'][2], data['Azure NetApp Files Ultra'][2]]
        df = pd.DataFrame(data)

        cost_table_columns = [{'name': col, 'id': col} for col in df.columns]
        cost_table_data = df.to_dict('records')
        return html.Div([
            html.H2('Cost Breakdown Table'),
            # html.P(f'Nodes: {cluster_node_count}'),
            # html.P(f'VM size: {azure_vm_size}'),
            # html.P(f'Node disk amount: {cluster_node_disk_amount}'),
            # html.P(f'Node disk tier: {cluster_node_disk_tier}'),
            # html.P(f'onefs_versions: {onefs_version}'),
            # html.P(f'Email: {selected_row["Email"]}')
            dash_table.DataTable(id='cost_table', columns=cost_table_columns, data=cost_table_data, style_table={'width': '800px'}, style_header={'textAlign': 'center'}, style_data={'textAlign': 'center'}),
            html.H6('Note: The APEX File Storage for Azure license cost is calculated with a 83% discount. This is the average discount that we provide on list price for customers. Azure NetApp Files Ultra uses list price without discount.', style={"color": "red"}),
            dcc.Graph(
                id='stacked-column-chart',
                figure={
                    'data': [
                        go.Bar(
                            x=figure_categories,
                            y=figure_annual_vm_cost,
                            name='Monthly Azure VM Cost - USD'
                        ),
                        go.Bar(
                            x=figure_categories,
                            y=figure_annual_storage_cost,
                            name='Monthly Azure Storage Cost - USD'
                        ),
                        go.Bar(
                            x=figure_categories,
                            y=figure_annual_license_cost,
                            name='Monthly OneFS License Cost - USD'
                        )
                    ],
                    'layout': {
                        'barmode': 'stack',
                        'xaxis': {'title': 'Storage Solutions'},
                        'yaxis': {'title': 'Cost (USD)'},
                        'title': 'Monthly Cost Compared to Azure NetApp Files Ultra',
                    }
                }
            )
        ])
    else:
        return []
