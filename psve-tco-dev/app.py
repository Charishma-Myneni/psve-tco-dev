import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])


navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", active=True, href="/")),
        dbc.NavItem(dbc.NavLink("AWS TCO", active=True, href="/aws-tco")),
        dbc.NavItem(dbc.NavLink("AWS Sizer", active=True, href="/aws-sizer")),
        #dbc.NavItem(dbc.NavLink("Azure TCO", active=True, href="/azure-tco")),
        dbc.NavItem(dbc.NavLink("Azure Sizer", active=True, href="/azure-sizer")),
    ],
    brand="AFSTools",
    brand_href="/",
    color="primary",
    dark=True,
    links_left=True,
)

app.layout = html.Div([
    html.Div([navbar]),
    dash.page_container
])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)