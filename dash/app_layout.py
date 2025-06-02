import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np

import layout_components as lc
from datetime import datetime, timedelta


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
    line_id, station_id, direction_radio_id, heading_id, graph_id, text_id, date_id, hour_id, minute_id = items

    # 호선별 색상
    line_colors = {
        "1호선": "#2955A4",
        "2호선": "#00BA00",
        "3호선": "#F36F21",
        "4호선": "#3B66B7",
        "5호선": "#794797",
        "6호선": "#96572A",
        "7호선": "#555D0F",
        "8호선": "#B23867",
        "9호선": "#C6AF5B"
    }

    layout = html.Div([
        html.H2("지하철 칸별 혼잡도 예측"),

        # 호선 선택 및 역명 입력
        html.Div([
            dcc.Dropdown(
                id=line_id,
                options=[
                    {
                        "label": html.Span(f"{line}", style={"color": color}),
                        "value": line
                    } for line, color in line_colors.items()
                ],
                placeholder="호선을 선택하세요",
                style={"width": "150px"}
            ),
            dcc.Input(
                id=station_id,
                type="text",
                placeholder="역명을 입력하세요",
                style={
                    "width": "150px",
                    "margin": "0 10px",
                    "padding": "8px",
                    "border": "1px solid #ccc",
                    "borderRadius": "4px",
                    "fontSize": "14px"
                }
            ),
            dcc.Dropdown(
                id=date_id,
                placeholder="날짜 선택",
                style={"width": "180px"}
            ),
            

            dcc.Dropdown(
                id=hour_id,
                options=[{"label": str(h), "value": str(h)} for h in range(5, 24)],
                placeholder="시",
                style={"width": "70px"}
            ),
            dcc.Dropdown(
                id=minute_id,
                options=[{"label": f"{m:02d}", "value": f"{m:02d}"} for m in range(0, 60, 10)],
                placeholder="분",
                style={"width": "70px"}
            )
        ], style={"display": "flex", "gap": "8px", "flexWrap": "wrap", "alignItems": "center"}),

        html.Br(),

        html.Div(id='station_heading', style={"margin": "20px", "textAlign": "center"}),


        html.Div(id=direction_radio_id, style={"margin": "10px 0"}),

        html.Button(
            "🚇 예측 실행", 
            id="predict_button", 
            n_clicks=0,
            style={
                "color": "black",
                "border": "none",
                "padding": "12px 24px",
                "fontSize": "18px",
                "fontWeight": "bold",
                "borderRadius": "8px",
                "cursor": "pointer",
                "boxShadow": "2px 2px 5px rgba(0,0,0,0.2)",
                "transition": "0.3s",
                "marginTop": "20px",
                'marginBottom': '20px'
            }
        ),

        html.Br(),

        dcc.Graph(id=graph_id),

        html.Div([
            html.Span("ℹ️", id="info-icon", style={
                'cursor': 'pointer',
                'fontSize': '40px',
                'color': '#007BFF',
                'marginRight': '10px'
            }),
            html.Img(
                src='/assets/complex.png',
                style={'height': '40px'}
            )
        ], style={
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'flex-end',
            'position': 'fixed',
            'bottom': '20px',
            'right': '20px',
            'zIndex': '1000'
        }),

        html.Div(
            id='info-modal',
            children=[
                html.Div([
                    html.Button("닫기", id="close-modal", style={'float': 'right'}),
                    html.Img(src="/assets/complex_info.png", style={'width': '100%'})
                ], style={
                    'backgroundColor': 'white',
                    'padding': '10px',
                    'borderRadius': '10px',
                    'maxWidth': '600px',
                    'margin': 'auto'
                })
            ],
            style={
                'display': 'none',
                'position': 'fixed',
                'top': '0',
                'left': '0',
                'width': '100%',
                'height': '100%',
                'backgroundColor': 'rgba(0, 0, 0, 0.6)',
                'zIndex': '2000',
                'alignItems': 'center',
                'justifyContent': 'center'
            }
        ),
        html.Div(id='model_input_text')
        ])

    return layout