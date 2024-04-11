# Make sure all cross dir import of this project works.
import sys
import os
current_path = os.getcwd()
if current_path not in sys.path:
    sys.path.insert(0, current_path)
sys.path.append(current_path)

import dash
import git, socket
from dash import Dash, dcc, html, Input, Output, dash_table, State, callback
import dash_bootstrap_components as dbc
from tcocal.cal_config import cal_config
from onefs_sizing.sizing_lib.aws.page_sizer_connector import SizeSolutionFromPage

dash.register_page(__name__, path='/aws-sizer')
# cal_config = CalConfig()

# Prepare region list
onefs_version_support_dict = {}
onefs_versions = cal_config.get_supported_onefs_versions()
for version in onefs_versions:
    supported_aws_regions = cal_config.get_supported_regions(version)
    onefs_version_support_dict[version] = supported_aws_regions

# Get the current git branch
branch = git.Repo('.', search_parent_directories=True).active_branch.name
ip_address = socket.gethostbyname(socket.gethostname())

if branch == 'main' and ip_address == '10.246.159.130':
    owa_tracking_js_src = "assets/owa-tracking-main.js"
elif branch == 'dev':
    owa_tracking_js_src = "assets/owa-tracking-dev.js"
else:
    owa_tracking_js_src = ""

layout = dbc.Container(
    [
        html.Script(src=owa_tracking_js_src, type="text/javascript"),
        # Title
        dbc.Row(
            [
                dbc.Col(
                    [html.H2("APEX File Storage For AWS Sizing Tool", style={"text-align": "center"})]
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H6("Note: This tool is still under development. Please contact yunlong.zhang@dell.com if you have any questions or suggestions."),
                    ]
                )
            ]
        ),
        # First section: select onefs version, region, workload.
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("Select OneFS Version:"),
                        dcc.Dropdown(
                            id="dropdown-version",
                            options=onefs_versions,
                            value="OneFS 9.7",
                            className="w-50",
                            clearable=False,
                            )                   
                    ]
                ),
                dbc.Col(
                    [
                        html.H5("Select Region:"),
                        dcc.Dropdown(
                            id="dropdown-region",
                            options=supported_aws_regions,
                            value="us-east-1",
                            className="w-50",
                            clearable=False,
                            )                    
                    ]
                ),
                dbc.Col(
                    [                        
                        html.H5("Select workload:"),
                        dcc.Dropdown(
                            id="dropdown-workload",
                            options=["Archive", "General"],
                            value="General",
                            className="w-50",
                            clearable=False,
                            ),                        
                    ]
                )
            ]
        ),
        # Second section: input capacity and drr.
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("Input Dataset Capacity (TiB):"),
                        dcc.Input(
                            id="input-capacity",
                            value="100",
                            className="w-100",
                            placeholder="100",
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        html.H5("Input Data Reduction Ratio (1.0 - 5.0):"),
                        dcc.Input(
                            id="input-drr",
                            value="2.0",
                            className="w-100",
                            placeholder="2.0",
                        ),
                    ]
                ),                
            ]
        ),
        # Third section: input read and write performance requirement.
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("Input Read Throughput Performance Requirement (MB/sec/cluster):"),
                        dcc.Input(
                            id="input-read-tput",
                            value="5000",
                            className="w-100",
                            placeholder="5000",
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        html.H5("Input Write Throughput Performance Requirement (MB/sec/cluster):"),
                        dcc.Input(
                            id="input-write-tput",
                            value="1200",
                            className="w-100",
                            placeholder="1200",
                        ),
                    ]
                ),
            ]
        ),
        # Forth section: a button to size the solution using the inputs.
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Button(
                            "Show Sizing Results", id="btn-size-it", n_clicks=0
                        ),
                    ]
                ),
            ]
        ),
        # Fifth section: show sizing result table.
        dbc.Row(
            [
                dbc.Col(id='table-col')
            ]
        ), 
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H6("Note: The data reduction ratio is only for sizing the capacity. Similar as PowerSizer, the read/write performance are measuring irreducible datasets. For AWS, annual cost contain cloud cost and OneFS license cost."),
                    ]
                )
            ],
        ),       
    ]
)

# Callback，according to onefs version Dropdown, update region Dropdown
@callback(
    Output('dropdown-region', 'options'),
    Output('dropdown-region', 'value'),
    Input('dropdown-version', 'value')
)
def update_dropdown_region(selected_version):
    options = [{'label': option, 'value': option} for option in onefs_version_support_dict[selected_version]]
    value = onefs_version_support_dict[selected_version][0]
    return options, value

# Click Button to show sizing result table.
@callback(
    Output('table-col', 'children'),
    Input("btn-size-it", "n_clicks"),
    State("dropdown-version", "value"),
    State("dropdown-region", "value"),
    State("dropdown-workload", "value"),
    State("input-capacity", "value"),
    State("input-drr", "value"),
    State("input-read-tput", "value"),
    State("input-write-tput", "value"),
)
def show_sizing_results(n_clicks, version, region, workload, capacity, drr, read_tput, write_tput):
    if n_clicks > 0:
        # Prepare data for table
        data_list = SizeSolutionFromPage(version, region, workload, drr, capacity, read_tput, write_tput, "AWS")
        if len(data_list) != 0: 
            columns_with_btn = [{"name": i, "id": i} for i in data_list[0].keys()]
            columns_with_btn.append({"name": "Action", "id": "Action", "presentation": "dropdown"})
            
            data_table = dash_table.DataTable(
                                        id='datatable',
                                        data=data_list,
                                        columns=columns_with_btn,
                                        page_size=20,
                                        style_table={"overflowX": "auto"}                                    
                                    )
            return [data_table]
        else:
            table_data = [
                {'Message': 1, 'Detail': 'No Valid Sizing Result. Check the Read Throughput Requirement.'}
            ]
            data_table = dash_table.DataTable(
                                        id='datatable',
                                        data=table_data,
                                        columns=[{"name": col, "id": col} for col in table_data[0].keys()]
                                    )
            return [data_table]      
    else:
        return []
