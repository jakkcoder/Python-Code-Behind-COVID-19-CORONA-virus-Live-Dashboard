# dash for layout
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import State, Input, Output
from dash.exceptions import PreventUpdate
import io
from flask import Flask, request, render_template, redirect, url_for, send_file
import plotly
import pandas as pd
import numpy as np
from random import random
from bs4 import BeautifulSoup
import requests
import plotly.express as px
# Plotly function to generate table plot
app = dash.Dash()   
def table_creater(df):
    df = df.dropna(subset=['Country'])
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    line_color='rgb(60,60,60)',
                    fill_color='rgb(40,40,40)',
                    align='left',font=dict(color='white', size=17)),
        cells=dict(values=df.T.values,
                   fill_color='rgb(20,10,30)',
                   line_color='rgb(20,10,30)',
                   align='left',font=dict(color='white', size=14)))
    ])
    fig.update_layout(
        autosize=False,
        margin=dict(l=0,r=0,b=0,t=0,pad=0),
        paper_bgcolor='rgb(20,10,30)',
    )
    return(fig.data,fig.layout)
##################################################################################
def get_corona_data():
    url="https://www.worldometers.info/coronavirus/"
    # Make a GET request to fetch the raw HTML content
    html_content = requests.get(url).text
    # Parse the html content
    soup = BeautifulSoup(html_content, "lxml")
    gdp_table = soup.find("table", id = "main_table_countries")
    gdp_table_data = gdp_table.tbody.find_all("tr")

    # Getting all countries names
    dicts = {}
    for i in range(len(gdp_table_data)):
        try:
            key = (gdp_table_data[i].find_all('a', href=True)[0].string)
        except:
            key = (gdp_table_data[i].find_all('td')[0].string)

        value = [j.string for j in gdp_table_data[i].find_all('td')]
        dicts[key] = value
    live_data= pd.DataFrame(dicts).drop(0).T
    live_data.columns = ["Total Cases","New Cases", "Total Deaths", "New Deaths", "Total Recovered","Active","Serious Critical",
"Tot Cases/1M pop"]
    live_data.index.name = 'Country'
    live_data.iloc[:,:5].to_csv("input_data/base_data.csv")
################################################################################################
def horigental_plots(df):
    df['Active cases'] = df['Total Cases']- (df.iloc[:,2:].sum(1))
    df = df.drop('Total Cases',1)
    big_df = pd.DataFrame(columns= ['Country',"Total Cases","Type"])
    for i in df.columns[1:]:
        small_df = df[["Country",i]].rename(columns = {i:"Total Cases"}).reset_index(drop=True)
        small_df["Type"] = i
        big_df = big_df.append(small_df)
        fig = px.bar(big_df, x="Total Cases", y="Country", color='Type', orientation='h',
                     title='Current count',opacity=.9,text="Total Cases")

        fig.layout.yaxis.showtickprefix = 'first'
        fig.update_layout(plot_bgcolor='rgb(20,10,30)',
                 paper_bgcolor='rgb(20,10,30)',
                 font=dict(family="Courier New, monospace",
                           color="white"),margin= dict(t=0,r=0,b=40,l=40),legend = dict(x=.5,y=1),
                  width=500,height=300)
        fig.update_yaxes(ticks="inside",tickangle = -55)
    
    
    return(fig.data,fig.layout)
	
	
###############################################################################################################################
def build_upper_left_panel():
    return html.Div(
        id="upper-left",
        className="six columns",
        children=[
            html.P(
                id="section-title",
                children="SPREAD RATE OF CORONA AROUND THE WORLD LIVE",
            ),
            html.Div(
                className="control-row-1",
                children=[
                    html.Div(
                        id="state-select-outer",
                        children=[
                            html.Div([
                            dcc.Interval(
                                id='interval-component-2',
                                interval=30*1000, # in milliseconds
                                n_intervals=0
                            ),
                            dcc.Interval(
                                id='interval-component-1',
                                interval=590*1000, # in milliseconds
                                n_intervals=0
                            )
                                
                        ]),
                        html.Div(id="loading-outer-frame1",
                                 children=[]),
                            html.Div(dcc.Loading(
                                    id="loading3",
                                    children=dcc.Graph(
                                        id='graph3',
                                        figure={
                                            "data": [],
                                            "layout": []
                                        },
                                    style={'width':'400%','hight':'400','margin':'0%'}),
                                ),
                        )
                        ]
                    ),
                ],
            )],
    style={'width':'50%','hight':'120%','margin':'0%','display':'inline-block'})
#################################################################################################################
app.layout = html.Div(
    className="container scalable",
    children=[
        html.Div(
            id="banner",
            className="banner",
            children=[
                html.H6("CORONAVIRUS EPIDEMIC CASES AROUND THE WORLD LIVE COUNT AND ANALYSIS")
            ],style={'color': 'white', 'fontSize': 100,'font-family' :'Arial Black'}
        ),
        html.Div(
            id="upper-container",
            className="row",
            children=[
                build_upper_left_panel(),
                html.Div(
                    id="geo-map-outer",
                    className="six columns",
                    children=[
                        html.P(
                            id="map-title",
                            children="CONFIRMED CASES AND DEATHS BY COUNTRY UPDATED EVERY 10 SECONDS",
                        ),
                        html.Div(
                            id="loading-outer-frame",
                            children=[
                                dcc.Loading(
                                    id="loading",
                                    children=dcc.Graph(
                                        id='graph1',
                                        figure={
                                            "data": [],
                                            "layout": []
                                        },
                                    style={'width':'100%','hight':'100%','margin':'0%'}),
                                )
                            ],
                        ),
                    ]
                , style={'width':'46%','hight':'120%','margin':'0%','display':'inline-block','animation-name': 'example',
  'animation-duration': '10s','animation-iteration-count': 'infinite'}),
            ],
        )
    ],
style={'width':'100%','hight':'120%','margin':'0%'})

## Callback function to generate take input on dropdown and update the child checklist 

@app.callback(
    [Output('graph1', "figure"),
    Output('graph3', "figure"),
    Output("loading-outer-frame1", "children")],
    [Input('interval-component-2', 'n_intervals')],
)

def update_region_dropdown(state_select):
    df = pd.read_csv("input_data/base_data.csv")
    df = df.loc[np.unique(np.random.randint(0,df.shape[0],(40)))]
    for i in df.columns[1:]:
        df[i] = df[i].apply(lambda x : x.replace(",","").replace(" ",""))
        df[i] = df[i].apply(lambda x : int(x) if len(x)>0 else 0)
        df = df.sort_values('Total Cases',ascending =False)
    traces,layouts=table_creater(df)
    traces_hori1,layouts_hori2=horigental_plots(df.iloc[:8,:])
    return (
       [{
        'data':traces,
        'layout':layouts
        }
       ,
       {
        'data':traces_hori1,
        'layout':layouts_hori2
        },
       html.Video(src='/static/2_5_1.webm',controls=True,autoPlay=True,loop=True,width="220%",height='400%')]
      )
########################################################################################
@app.callback([Output('section-title', "children")],
    [Input('interval-component-1', 'n_intervals')]
    )

def download_data(state_select):
    get_corona_data()
    df = pd.read_csv("input_data/base_data.csv",index_col=[0])
    for i in df.columns:
        df[i] = df[i].apply(lambda x : x.replace(",","").replace(" ",""))
        df[i] = df[i].apply(lambda x : int(x) if len(x)>0 else 0)
    cc =df.sum()

    return (
       ["TOTAL CASES- {}, NEW CASES- {}      ......      TOTAL DEATHS- {},  NEW DEATHS-{}      ......        TOTAL RECOVERED-{}".format(cc[0],cc[1],cc[2],cc[3],cc[4])])

if __name__=='__main__':
    app.run_server()  
  