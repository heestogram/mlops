import dash
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
items = ['line_select', 'station_input', 'direction_input', 'predict_btn', 'result_graph']
app = dash.Dash()
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
        ('당고개', 409), ('상계', 410), ('노원', 411), ('창동', 412), ('쌍문', 413), ('수유', 414), ('미아', 415),
        ('길음', 417), ('성신여대입구', 418), ('한성대입구', 419), ('혜화', 420), ('동대문', 421), ('동대문역사문화공원', 422),
        ('충무로', 423), ('명동', 424), ('회현', 425), ('서울역', 426), ('숙대입구', 427), ('삼각지', 428), ('신용산', 429),
        ('이촌', 430), ('동작', 431), ('총신대입구', 432), ('사당', 433), ('남태령', 434)
    ]
}



@app.callback(
    Output('result_graph', 'figure'),
    Input('predict_btn', 'n_clicks'),
    State('line_select', 'value'),
    State('station_input', 'value'),
    State('direction_input', 'value'),
    prevent_initial_call=True
)
def predict_congestion(n_clicks, line, station_name, direction):

    station_list = station_dict.get(line, [])
    name_to_code = {name: code for name, code in station_list}
    code_to_name = {code: name for name, code in station_list}

    # 현재 역 번호
    curr_code = name_to_code.get(station_name)

    # 다음 역 계산
    if curr_code is not None:
        if direction == "up":
            next_station_name = code_to_name.get(curr_code - 1, "종점")
        else:
            next_station_name = code_to_name.get(curr_code + 1, "종점")
        heading_text = f"{next_station_name}역 방면 (10분 후 도착)"
    else:
        heading_text = "알 수 없는 역"
        
    if not line or not station_name:
        return go.Figure(layout_title_text="호선과 역명을 입력해주세요")

    try:
        print("good")

        res = requests.post(
            url="https://friendly-potato-6q69gr56xr634wqr-8000.app.github.dev/predict",  # 혹은 Codespaces용 외부 URL
            headers={"accept": "application/json", "Content-Type": "application/json"},
            json={
                    "line": line,
                    "station": station_name,
                    "direction": direction
            }
        )
        print("응답 상태 코드:", res.status_code)
        print("응답 내용:", res.text)

        congestion = res.json()["predictions"]  # 길이 10 리스트
    except Exception as e:
        print("API 호출 실패:", e)
        return go.Figure(layout_title_text="❗ 예측 서버 연결 오류")

    car_ids = [str(i) for i in range(1, 11)]

    def map_color(c):
        if c <= 34:
            return "green"
        elif c <= 100:
            return "gold"
        else:
            return "red"

    colors = [map_color(c) for c in congestion]

    fig = go.Figure()
    for car, cong, color in zip(car_ids, congestion, colors):
        fig.add_trace(go.Bar(
            x=[car],
            y=[cong],
            name=f"{car}호차",
            marker_color=color,
            text=f"{int(cong)}%",
            textposition='outside',
            textfont=dict(size=14, color="black"),
            hovertext=f"{car}호차: {cong}%",
            width=0.8
        ))

    fig.update_layout(
        title=f"{line} {station_name}역 - {heading_text}",
        showlegend=False,
        yaxis=dict(title="혼잡도 (%)", range=[0, 250]),
        xaxis=dict(title="호차"),
        height=400,
        bargap=0.2
    )

    return fig
    
app.run(host="0.0.0.0", port=9101, debug=True) 