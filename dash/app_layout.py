import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np

import layout_components as lc
import datetime

import mylib as my

# def app_layout(items):
    
#     button_id = items[0]
#     time_id = items[1]
#     predict_id = items[2]
#     graph_id = items[3]
#     table_id = items[4]
    
#     ## layout
#     layout = html.Div(children = [
                        
#                 ## 최근 호출시점+예측값
#                 html.Div(children=[
#                     html.Div(children=[
#                         html.H4(children="지지지지ddㅣ"),
#                         html.H1(id=time_id),
#                     ], style={'flex':'1'}),

#                     html.Div(children=[
#                         html.H4(children="최근예측값"),
#                         html.H1(id=predict_id),
#                     ], style={'flex':'1'}),
                    
#                     lc.button(idname=button_id, text="예측 (inference)"),

#                 ],style={'display':'flex','flex-direction':'row'}),

                
#                 ## 누적 yhat 그래프
#                 html.H4(children="예측값 Trned"),
#                 lc.showgraph(idname=graph_id),

#                 ## 누적 X 테이블 
#                 html.H4(children="입력값"),
#                 lc.showtable(idname=table_id),
        
#     ])
    
#     return layout




def app_layout(items):
    line_id, input_id, direction_id, button_id, graph_id = items

    layout = html.Div([
        html.H2("지하철 칸별 혼잡도 예측"),

        html.Div([
            dcc.Dropdown(
                id=line_id,
                options=[{"label": f"{i}호선", "value": f"{i}호선"} for i in range(1, 10)],
                placeholder="호선을 선택하세요",
                style={"width": "150px"}
            ),

            dcc.Input(
                id=input_id,
                type="text",
                placeholder="역명을 입력하세요",
                style={"margin-left": "10px", "width": "150px"}
            ),

            dcc.RadioItems(
                id=direction_id,
                options=[{"label": "상행", "value": "up"}, {"label": "하행", "value": "down"}],
                value="up",
                labelStyle={"display": "inline-block", "margin": "0 10px"}
            ),

            html.Button("예측", id=button_id, n_clicks=0)
        ], style={"display": "flex", "gap": "10px", "alignItems": "center"}),

        html.Br(),

        dcc.Graph(id=graph_id)
    ])

    return layout