import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go

import app_layout as al
import mylib as my

import requests 
import pandas as pd
import numpy as np
import sys, os
import datetime
import pickle as pkl


##### 원래 교수님 코드 #########
# items = ['button1','time1', 'pred1', 'graph1', 'table1']

# app = dash.Dash()
# app.layout =  al.app_layout(items)

# @app.callback(
#     Output('time1','children'),
#     Output('table1','data'),
#     Output('pred1', 'children'),
#     Output('graph1', 'figure'),
#     Input('button1','n_clicks'),
#     prevent_initial_call=False,
# )
# def fn(n_clicks): 

#     tt = str(datetime.datetime.now())

#     df = my.db_to_df_random(db_name='steel.db', table_name='test')

#     output = requests.post(url='https://friendly-potato-6q69gr56xr634wqr-8000.app.github.dev/predict', 
#                            headers={"accept": "application/json", "Content-Type": "application/json"}, 
#                            json={"data": df.to_dict("records")} )

#     pred = output.json()['prediction']
#     x_cols = output.json()['input_column_names']

#     pred_df = pd.DataFrame(data=[pred], columns=["pred"])
#     my.df_to_db(df[x_cols], "operation.db", "input_x")
#     my.df_to_db(pred_df, "operation.db","pred")
    
#     print_df = my.db_to_df("operation.db","input_x")
#     pred_history = my.db_to_df("operation.db","pred")

#     fig=px.line(x=pred_history.index.tolist(), y=pd.to_numeric(pred_history['pred']))
#     out=print_df.to_dict('records')
    
#     return tt, out, pred, fig
#app.run(host="0.0.0.0", port=9101, debug=True) 
######################################



##### 내가 수정한 코드 #######
# Layout item IDs
items = ['line_select', 'station_input', 'direction_radio', 'station_heading', 'result_graph']
app = dash.Dash(suppress_callback_exceptions=True)

app.layout = al.app_layout(items)

station_dict = {
    "3호선": [
        ('지축', 309), ('구파발', 310), ('연신내', 311), ('불광', 312), ('녹번', 313), ('홍제', 314), ('무악재', 315),
        ('독립문', 316), ('경복궁', 317), ('안국', 318), ('종로3가', 319), ('을지로3가', 320), ('충무로', 321),
        ('동대입구', 322), ('약수', 323), ('금호', 324), ('옥수', 325), ('압구정', 326), ('신사', 327), ('잠원', 328),
        ('고속터미널', 329), ('교대', 330), ('남부터미널', 331), ('양재', 332), ('매봉', 333), ('도곡', 334), ('대치', 335),
        ('학여울', 336), ('대청', 337), ('일원', 338), ('수서', 339), ('가락시장', 340), ('경찰병원', 341), ('오금', 342)
    ],
    "4호선": [
        ('당고개', 409), ('상계', 410), ('노원', 411), ('창동', 412), ('쌍문', 413), ('수유', 414), ('미아', 415), ('미아사거리',416),
        ('길음', 417), ('성신여대입구', 418), ('한성대입구', 419), ('혜화', 420), ('동대문', 421), ('동대문역사문화공원', 422),
        ('충무로', 423), ('명동', 424), ('회현', 425), ('서울역', 426), ('숙대입구', 427), ('삼각지', 428), ('신용산', 429),
        ('이촌', 430), ('동작', 431), ('총신대입구', 432), ('사당', 433), ('남태령', 434)
    ]
}
line_colors = {
    "1호선": "#2955A4",  # (41, 85, 164)
    "2호선": "#00BA00",  # (0, 186, 0)
    "3호선": "#F36F21",  # (210, 104, 61)
    "4호선": "#3B66B6",  # (59, 102, 182)
    "5호선": "#7947A1",  # (121, 71, 151)
    "6호선": "#96572A",  # (150, 87, 42)
    "7호선": "#555D10",  # (85, 93, 16)
    "8호선": "#B43867",  # (180, 56, 103)
    "9호선": "#C6AF5B",  # (198, 175, 91)
}


@app.callback(
    Output('info-modal', 'style'),
    [Input('info-icon', 'n_clicks'),
     Input('close-modal', 'n_clicks')],
    State('info-modal', 'style')
)
def toggle_modal(open_clicks, close_clicks, current_style):
    ctx = dash.callback_context

    if not ctx.triggered:
        return current_style

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == "info-icon":
        return {**current_style, 'display': 'flex'}
    elif trigger_id == "close-modal":
        return {**current_style, 'display': 'none'}
    return current_style

@app.callback(
    Output('direction_radio', 'children'),
    Input('line_select', 'value'),
    Input('station_input', 'value'),
)
def update_direction_radios(line, station):
    if not line or not station:
        return ""

    station_list = station_dict.get(line, [])
    name_to_code = {name: code for name, code in station_list}
    code_to_name = {code: name for name, code in station_list}

    curr_code = name_to_code.get(station)
    if not curr_code:
        return html.Div("해당 역명을 찾을 수 없습니다.")

    up_name = code_to_name.get(curr_code - 1, "종점")
    down_name = code_to_name.get(curr_code + 1, "종점")

    return dcc.RadioItems(
        id='direction_choice',
        options=[
            {"label": f"{up_name} 방면", "value": "up"},
            {"label": f"{down_name} 방면", "value": "down"}
        ],
        value="up",
        labelStyle={"display": "inline-block", "margin-right": "15px"}
    )


# 📊 예측 및 시각화
@app.callback(
    [Output('station_heading', 'children'),
     Output('result_graph', 'figure')],
    Input('direction_choice', 'value'),
    State('line_select', 'value'),
    State('station_input', 'value'),
    prevent_initial_call=True
)
def predict_congestion(direction, line, station_name):
    if not station_name or not line:
        return html.Div("입력 오류"), go.Figure()

    station_list = station_dict.get(line, [])
    name_to_code = {name: code for name, code in station_list}
    code_to_name = {code: name for name, code in station_list}

    curr_code = name_to_code.get(station_name)
    prev_station = code_to_name.get(curr_code - 1, "")
    next_station = code_to_name.get(curr_code + 1, "")
    line_color = line_colors.get(line, "#000")


    # box_style = {
    # "minWidth": "80px",              # 고정 최소 너비 (길이에 상관없이 넉넉하게)
    # "height": "40px",                # 고정 높이
    # "display": "flex",               # 가운데 정렬을 위해 flex 사용
    # "alignItems": "center",
    # "justifyContent": "center",
    # "fontSize": "20px",              # 글자 크기 키움
    # "fontWeight": "bold",            # 굵게
    # "padding": "5px 10px",
    # "margin": "0 5px",
    # "borderRadius": "10px"
    # }
    
    # heading = html.Div([
    #     html.Span(prev_station, style={
    #         **box_style,
    #         "backgroundColor": line_color,
    #         "color": "white",
    #         "borderTopLeftRadius": "10px",
    #         "borderBottomLeftRadius": "10px"
    #     }) if prev_station else None,

    #     html.Span(station_name, style={
    #         **box_style,
    #         "backgroundColor": "white",
    #         "color": line_color,
    #         "border": f"2px solid {line_color}"
    #     }),

    #     html.Span(next_station, style={
    #         **box_style,
    #         "backgroundColor": line_color,
    #         "color": "white",
    #         "borderTopRightRadius": "10px",
    #         "borderBottomRightRadius": "10px"
    #     }) if next_station else None

    # ], style={"display": "flex", "justifyContent": "center", "marginBottom": "20px"})

    heading = html.Div([
            html.Span(prev_station, style={
                "backgroundColor": line_color,
                "color": "white",
                "padding": "8px 0",
                "minWidth": "120px",
                "height": "40px",
                "lineHeight": "40px",  
                "textAlign": "center",
                "borderTopLeftRadius": "30px",
                "borderBottomLeftRadius": "30px",
                "fontSize": "17px",
                "fontWeight": "bold"
            }) if prev_station else None,

            html.Span(station_name, style={
                "backgroundColor": "white",
                "color": line_color,
                "padding": "8px 0",
                "minWidth": "120px",
                "height": "40px",               
                "lineHeight": "40px",
                "textAlign": "center",
                "border": f"2px solid {line_color}",
                "fontSize": "19px",
                "fontWeight": "bold"
            }),

            html.Span(next_station, style={
                "backgroundColor": line_color,
                "color": "white",
                "padding": "8px 0",
                "minWidth": "120px",
                "height": "40px",               
                "lineHeight": "40px",
                "textAlign": "center",
                "borderTopRightRadius": "30px",
                "borderBottomRightRadius": "30px",
                "fontSize": "17px",
                "fontWeight": "bold"
            }) if next_station else None
        ], style={
            "display": "inline-flex",
            "justifyContent": "center",
            "alignItems": "center",
            "marginTop": "20px"
        })


    # 👇 API 예측 호출
    try:
        res = requests.post(
            url="https://friendly-potato-6q69gr56xr634wqr-8000.app.github.dev/predict",
            headers={"Content-Type": "application/json"},
            json={"line": line, "station": station_name, "direction": direction}
        )
        congestion = res.json()["predictions"]
    except Exception as e:
        print("API 호출 실패:", e)
        return heading, go.Figure(layout_title_text="❗ 예측 실패")

    # 🎨 시각화
    def map_color(c):
        if c <= 34: return "green"
        elif c <= 100: return "gold"
        else: return "red"

    car_ids = [str(i) for i in range(1, 11)]
    colors = [map_color(c) for c in congestion]

    fig = go.Figure()
    for car, cong, color in zip(car_ids, congestion, colors):
        fig.add_trace(go.Bar(
            x=[car],
            y=[cong],
            marker_color=color,
            text=f"{int(cong)}%",
            textposition='outside',
            textfont=dict(size=14, color="black"),
            hovertext=f"{car}호차: {int(cong)}%",
            width=0.8
        ))

    next_name = next_station if direction == "down" else prev_station
    fig.update_layout(
        title=f"<span style='color:{line_color}'>{line}</span> {station_name}역 - {next_name} 방면 (10분 후 도착)",
        showlegend=False,
        yaxis=dict(title="혼잡도 (%)", range=[0, 250]),
        xaxis=dict(title="호차"),
        height=400,
        bargap=0.2
    )

    return heading, fig
    
app.run(host="0.0.0.0", port=9101, debug=True) 