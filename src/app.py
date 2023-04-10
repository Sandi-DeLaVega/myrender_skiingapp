from flask import Flask
from dash import Dash, dcc, html, dash_table, Dash
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import load_figure_template
import os
import plotly.express as px
import pandas as pd
import numpy as np

assets_path = os.getcwd() +'\\assets'
dbc_css = os.path.join("assets_path", "skiresort.css")

resorts = (
    pd.read_csv("./Data/Ski Resorts/resorts.csv", encoding = "ISO-8859-1")
    .assign(
        country_elevation_rank = lambda x: x.groupby("Country", as_index=False)["Highest point"].rank(ascending=False),
        country_price_rank = lambda x: x.groupby("Country", as_index=False)["Price"].rank(ascending=False),
        country_slope_rank = lambda x: x.groupby("Country", as_index=False)["Total slopes"].rank(ascending=False),
        country_cannon_rank = lambda x: x.groupby("Country", as_index=False)["Snow cannons"].rank(ascending=False),
    ))

server = Flask(__name__)
app = Dash(server = server,  external_stylesheets=[dbc.themes.ZEPHYR,  dbc_css])
app.title = 'Skiing Resort Dashboard'
server = app.server

load_figure_template("ZEPHYR")

app.layout = dbc.Container([
    #Header
    html.Div(
            className = "grid-container2",
            children = [
                html.Div(
                    className="item1",
                    children=[
                        html.Div('SKIING RESORT DASHBOARD'), 
                        ], 
                        )
                     ]
             ),
    ### Tab 1: Map of Skiing Hotspots based on filters
    dcc.Tabs(className="navbar navbar-expand-lg navbar-light bg-light", children = [
        dbc.Tab(className="btn btn-lg btn-primary navbar-toggler",label="Geographical View",
                children = [
            html.Div(className = "grid-main-row", 
                     children = [
                            html.Br(),
                            html.H1(id="map-title", style={"text-align": "center"}),
                            html.Br(),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Card([
                                        dcc.Markdown(" #### ** Price Limit **"),
                                        #A slider that sets a maximum price
                                        dcc.Slider(id="price-slider", min=0, max=150, step=25, value=150, 
                                                   className="price-slider"),
                                        html.Br(),
                                        dcc.Markdown(" #### ** Feature Preferences **"),
                                        #A checkbox to filter to resorts with summer skiing
                                        dcc.Checklist(
                                            id="summer-ski-checklist", 
                                            options=[{"label": " Has Summer Skiing?", "value": "Yes"}], value=[]),
                                        #A checkbox to filter to resorts with night skiing
                                        dcc.Checklist(
                                            id="night-ski-checklist", 
                                            options=[{"label": " Has Night Skiing?", "value": "Yes"}], value=[]),
                                        #A checkbox to filter to resorts with a snowpark
                                        dcc.Checklist(
                                            id="snow-park-checklist", 
                                            options=[{"label": " Has Snow Park?", "value": "Yes"}], value=[]),
                                        #A checkbox to filter to resorts that are child friendly
                                        dcc.Checklist(
                                            id="child-friendly-checklist", 
                                            options=[{"label": " Have to be Child Friendly?", "value": "Yes"}], value=[])
                                            ], className = "grid-tab-selection"),
                                        html.Br(),
                                        dcc.Markdown("Select a Metric to Plot:"),
                                        dcc.Dropdown(
                                            id="column-picker-tab1",
                                            options=resorts.select_dtypes("number").columns[3:],
                                            value="Price", clearable=False,
                                            className="dbc", style={"background-color": "#E0FFFF"}
                                        ),
                                        ], width=3),
                                dbc.Col(dcc.Graph(id="resort-map"), style={"text-align": "center"}, width=9)
                                    ])
                                ]),
            
        ]),
        # Tab 2: Country report & Resort Report card
        dbc.Tab(className="btn btn-lg btn-primary", label="Detailed View", style={"text-align": "center",
                                                                                 "color": "black"},
                children=[
                    html.Div(className = "grid-main-row", 
                             children = [
                                 html.Br(),
                                html.H1(id="country-title", style={"text-align": "center"}),
                                html.Br(),
                                dbc.Row([
                                    #A sidebar that allows users to first select a continent. 
                                    #Based on the selected continent, a second dropdown will populate with the countries in that continent
                                    dbc.Col([
                                        dcc.Markdown("Select Continent:"),
                                        dcc.Dropdown(
                                            id="continent-dropdown",
                                            options=resorts["Continent"].unique(),
                                            value="Europe", clearable=False,
                                            className="dbc", style={"background-color": "#E0FFFF"},
                                        ),
                                        html.Br(),
                                        #, allowing users to select a country. 
                                        dcc.Markdown("Select Country:"),
                                        dcc.Dropdown(id="country-dropdown", value="Norway", clearable=False, 
                                                     className="dbc", style={"background-color": "#E0FFFF"}),
                                        html.Br(),
                                        #Finally, users will use a dropdown menu to select the column they want to plot in our bar chart. 
                                        dcc.Markdown("Select a Metric to Plot:"),
                                        dcc.Dropdown(
                                            id="column-picker",
                                            options=resorts.select_dtypes("number").columns[3:],
                                            value="Price", clearable=False,
                                            className="dbc", style={"background-color": "#E0FFFF"}
                                        ),
                                    ], width=2),
                                    #bar chart where the x-axis is resort (consider removing x-axis labels), 
                                    #and y-axis is the users selected metric. 
                                    #Plot the top 10 resorts by the selected metric. 
                                    dbc.Col([dcc.Graph(id="metric-bar",
                                                       hoverData={'points': [{'customdata': ['Hemsedal']}]})]
                                            , width=7),
                                    #A Resort Report Card. 
                                    #A basic version of this would a handful of key metrics by country. 
                                    dbc.Col([
                                        html.Div(children = [dcc.Markdown("#### Resort Metrics")], style={"text-align": "center"}),
                                        dbc.Row([html.Div(id="resort-name", 
                                                                   style={"text-align": "center", "fontSize":20, 
                                                                                   "background-color": " rgba(255, 255, 255, 1)"})]),
                                        dbc.Row([dbc.Col([html.Div('Elevation Rank: ')], width=8),
                                                 dbc.Col([html.Div(id="elevation-kpi", 
                                                                   style={"text-align": "center", "fontSize":16,
                                                                                    "background-color": " rgba(255, 255, 255, 1)"})])]),
                                        dbc.Row([dbc.Col([html.Div('Price Rank: ')], width=8),
                                                 dbc.Col([html.Div(id="price-kpi", 
                                                                   style={"text-align": "center", "fontSize":16,
                                                                                "background-color": " rgba(255, 255, 255, 1)"})])]),
                                        dbc.Row([dbc.Col([html.Div('Slope Rank: ')], width=8),
                                                 dbc.Col([html.Div(id="slope-kpi", style={"text-align": "center", "fontSize":16,
                                                                                "background-color": " rgba(255, 255, 255, 1)"})])]),
                                        dbc.Row([dbc.Col([html.Div('Cannon Rank')], width=8),
                                                 dbc.Col([html.Div(id="cannon-kpi", style={"text-align": "center", "fontSize":16,
                                                                                 "background-color": " rgba(255, 255, 255, 1)"})])]),
                                    ], width=3)
                                ])
                             ]),
            
        ])
    ]),
    #Footer
    html.Div(children = [
    dbc.Row(
        [ 
            dbc.Col([html.Div("Project by: Sandi De La Vega")], width = 3),
            dbc.Col([html.Div("sandi@optimousse.tech")], width = 2),
            dbc.Col([html.Div("Revised from Udemy Course: Python Data Visualization: Dashboards with Plotly & Dash Maven Analytics")], width = 7),
            ]), #end of footer Class
    ], className="footer")
], style={"width":1300, "background": "#F7F7F7"})



@app.callback(
    Output("map-title", "children"),
    Output("resort-map", "figure"),
    Input("price-slider", "value"),
    Input("summer-ski-checklist", "value"),
    Input("night-ski-checklist", "value"),
    Input("snow-park-checklist", "value"),
    Input("child-friendly-checklist", "value"),
    Input("column-picker-tab1", "value")
)

def snow_map(price, summer_ski, night_ski, child, snow_park, metric):
    
    title = f"Resorts with a Ticket Price up to ${price} by {' '.join(metric.split('_')).title()}." 
    
    df = resorts.loc[(resorts["Price"] <= price)]
    
    if "Yes" in summer_ski:
        df = df.loc[(df["Summer skiing"] == "Yes")]
        
    if "Yes" in night_ski:
        df = df.loc[(df["Nightskiing"] == "Yes")]
    
    if "Yes" in snow_park:
        df = df.loc[(df["Snowparks"] == "Yes")]
    
    if "Yes" in child:
        df = df.loc[(df["Child friendly"] == "Yes")]
    
    fig = px.density_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        z = metric,
        hover_name="Resort",
        center={"lat": 45, "lon": -100},
        zoom=0.6,
        opacity=1,
        mapbox_style="stamen-terrain",
        color_continuous_scale="oranges",
        width=850,
        height=600
    )
    return title, fig



@app.callback(
    Output("country-dropdown", "options"), 
    Input("continent-dropdown", "value"))
def country_select(continent):
    return np.sort(resorts.query("Continent == @continent").Country.unique())



@app.callback(
    Output("country-title", "children"),
    Output("metric-bar", "figure"),
    Input("country-dropdown", "value"),
    Input("column-picker", "value")
)
def plot_bar(country, metric): 
    if not country and metric:
        raise PreventUpdate
    
    df = resorts.query("Country == @country").sort_values(metric, ascending=False).head(10)
    total = len(df)
    title = f"Top {total} Resorts in {country} by {' '.join(metric.split('_')).title()}"    
    figure = px.bar(df, x="Resort", y=metric, custom_data=["Resort"], text = metric, 
                    color_discrete_sequence = [px.colors.qualitative.G10[9],
                                               px.colors.qualitative.Prism[1],
                                              px.colors.qualitative.G10[0],
                                              px.colors.qualitative.D3[0],
                                               px.colors.qualitative.T10[0],
                                              px.colors.qualitative.D3[9],
                                               px.colors.qualitative.Plotly[2],
                                               px.colors.qualitative.Plotly[5],
                                               px.colors.qualitative.Set3[4],
                                               px.colors.qualitative.Pastel[1],
                                              ]).update_xaxes(showticklabels=True)
    
    figure.update_traces(marker_color='rgb(55, 83, 109)', 
                         marker_line_color='rgb(8,48,107)',
                         textfont_color="white",
                  marker_line_width=1.5, opacity=0.6)
        
    return title, figure



@app.callback(
    Output("resort-name", "children"),
    Output("elevation-kpi", "children"),
    Output("price-kpi", "children"),
    Output("slope-kpi", "children"),
    Output("cannon-kpi", "children"),
    Input("metric-bar", "hoverData"))
def report_card(hoverData):
    resort = hoverData["points"][0]["customdata"][0]
    df = resorts.query("Resort == @resort")
    elev_rank = f"{int(df['country_elevation_rank'])}"
    price_rank = f"{int(df['country_price_rank'])}"
    slope_rank = f"{int(df['country_slope_rank'])}"
    cannon_rank = f"{int(df['country_cannon_rank'])}"
    
    return resort, elev_rank, price_rank, slope_rank, cannon_rank 



if __name__ == "__main__":
    app.run_server(port=2034)