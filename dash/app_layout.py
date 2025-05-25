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
    line_id, station_id, direction_radio_id, graph_id = items

    # 호선별 색상
    line_colors = {
        "1호선": "#2955A4",
        "2호선": "#00BA00",
        "3호선": "#D2683D",
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
                style={"margin": "0 10px"}
            )
        ], style={"display": "flex", "gap": "10px"}),

        html.Br(),

        # 상/하행 선택 radio
        html.Div(id=direction_radio_id, style={"margin": "10px 0"}),

        html.Br(),

        # 예측 그래프
        dcc.Graph(id=graph_id),

        # ❓아이콘 + 이미지 함께 배치 (오른쪽 하단 고정)
        html.Div([
            html.Span("❓", id="info-icon", style={
                'cursor': 'pointer',
                'fontSize': '20px',
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

        # ❓아이콘 클릭 시 나타나는 모달 이미지
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
        )
    ])

    return layout