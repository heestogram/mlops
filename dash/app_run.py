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
from datetime import datetime, timedelta
from datetime import date
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
items = ['line_select', 'station_input', 'direction_radio', 'station_heading', 'result_graph', 'date_select', 'hour_select', 'minute_select']
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
    "1호선": "#2955A4",  
    "2호선": "#00BA00",  
    "3호선": "#F36F21",  
    "4호선": "#00A9E0", 
    "5호선": "#7947A1",  
    "6호선": "#96572A",  
    "7호선": "#555D10",  
    "8호선": "#B43867", 
    "9호선": "#C6AF5B",  
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
        value=None,
        labelStyle={"display": "inline-block", "margin-right": "15px"}
    )



@app.callback(
    Output('date_select', 'options'),
    Input('line_select', 'value')  
)
def update_date_options(_):
    today = datetime.today()
    options = [
        {"label": d.strftime("%-m월 %-d일 %a") if i > 0 else "오늘", "value": d.strftime("%Y-%m-%d")}
        for i, d in enumerate([today + timedelta(days=i) for i in range(7)])
    ]
    return options

@app.callback(
    [Output('station_heading', 'children'),
     Output('result_graph', 'figure')],
    Input('predict_button', 'n_clicks'),
    State('direction_choice', 'value'),
    State('line_select', 'value'),
    State('station_input', 'value'),
    State('date_select', 'value'),
    State('hour_select', 'value'),
    State('minute_select', 'value'),
    prevent_initial_call=True
)
def predict_congestion(n_clicks, direction, line, station_name, date_val, hour, minute):
    if not all([line, station_name, direction, date_val, hour, minute]):
        return html.Div("⛔ 모든 입력값을 선택해주세요."), go.Figure()

    if date_val == "오늘":
        date_obj = date.today()
    else:
        try:
            date_obj = date.fromisoformat(date_val)  # '2025-06-04' 같은 문자열 → datetime.date 객체
        except Exception as e:
            return html.Div("❌ 날짜 파싱 실패"), go.Figure()

    hour = int(hour)
    minute = int(minute)

    time_str = f"{hour:02d}:{minute:02d}"


    station_list = station_dict.get(line, [])
    name_to_code = {name: code for name, code in station_list}
    code_to_name = {code: name for name, code in station_list}

    curr_code = name_to_code.get(station_name)
    prev_station = code_to_name.get(curr_code - 1, "")
    next_station = code_to_name.get(curr_code + 1, "")
    line_color = line_colors.get(line, "#000")


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


    try:
        res = requests.post(
            url="https://friendly-potato-6q69gr56xr634wqr-8000.app.github.dev/predict",
            headers={"Content-Type": "application/json"},
            json={"line": line, "station": curr_code, "direction": direction, "date": str(date_obj), "time": time_str}
        )
        congestion = res.json()["predictions"]
        model_input = res.json()["model_input"]

    except Exception as e:
        print("API 호출 실패:", e)
        return heading, go.Figure(layout_title_text="❗ 예측 실패")

    def map_color(c):
        if c <= 34: return "#B6CFB6"
        elif c <= 100: return "#ffd980"
        else: return "#bf4040"

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