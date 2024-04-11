import dash
from dash import html, dcc
import git, socket

dash.register_page(__name__, path='/')

# Get the current git branch
branch = git.Repo('.', search_parent_directories=True).active_branch.name
ip_address = socket.gethostbyname(socket.gethostname())

if branch == 'main' and ip_address == '10.246.159.130':
    owa_tracking_js_src = "assets/owa-tracking-main.js"
elif branch == 'dev':
    owa_tracking_js_src = "assets/owa-tracking-dev.js"
else:
    owa_tracking_js_src = ""

layout = html.Div([
    html.Script(src=owa_tracking_js_src, type="text/javascript"),
    html.P('Choose the sizing tool you want to use:'),
    dcc.Link('AWS Sizer', href='/aws-sizer'),
    html.Br(),
    dcc.Link('Azure Sizer', href='/azure-sizer'),
])