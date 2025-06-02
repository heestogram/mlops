import os
import pickle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pydantic import BaseModel, conlist
from typing import List, Literal
from fastapi import FastAPI, Body
import xgboost

with open("model.pkl", "rb") as f:
    model = pickle.load(f)
with open("preprocessing.pkl","rb") as f:
    processed = pickle.load(f) 

preprocessor = processed["preprocessor"]

drop_df = pd.read_csv("drop_info.csv")
drop_df["drop"] = drop_df["drop"].apply(eval)

final_data = pd.read_csv("final_final_final.csv")


app = FastAPI()


class PredictionInput(BaseModel):
    line: str        
    station: int      
    direction: Literal["up", "down"]
    date: str
    time: str


@app.post("/predict")
def predict(dataset: PredictionInput):
    # 임의의 예측값 반환 (0~230% 사이)

    row = drop_df[
        (drop_df["station_code"] == dataset.station) &
        (drop_df["direction"] == dataset.direction)
    ]

    if row.empty:
        drop_list = []
    else:
        drop_list = row.iloc[0]["drop"]

    drop_features = {f"drop_{i}": int(i in drop_list) for i in range(1, 11)}

    direction = "상행" if dataset.direction == "up" else "하행"

    date_obj = datetime.strptime(dataset.date, "%Y-%m-%d")
    weekday_raw = date_obj.weekday()  # 월(0)~일(6)
    if weekday_raw == 5:
        weekday = "1"  # 토요일
    elif weekday_raw == 6:
        weekday = "2"  # 일요일
    else:
        weekday = "0"  # 평일

    filtered_df = final_data[
        (final_data["station_code"] == dataset.station) &
        (final_data["arrivetime"] == dataset.time) &
        (final_data["상하선"] == direction)
    ]
    if not filtered_df.empty:
        train_no = str(filtered_df["train_no"].mode().iloc[0])
    else:
        hundred_digit = dataset.station // 100
        if hundred_digit == 3:
            train_no = "3288"
        elif hundred_digit == 4:
            train_no = "K4649"
        else:
            train_no = "9999"

    filtered_df2 = final_data[
        (final_data['station_code'] == dataset.station) &
        (final_data['arrivetime'] == dataset.time) &
        (final_data['상하선'] == direction) &
        (final_data['요일'] == int(weekday))
    ]
    def remove_outliers_iqr(df, col):
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        return df[(df[col] >= lower) & (df[col] <= upper)]

    def safe_sample_mean_std(df, col, default=100, non_negative=False):
        df_filtered = remove_outliers_iqr(df, col)
        if not df_filtered.empty:
            mean_val = df_filtered[col].mean()
            std_val = df_filtered[col].std()
            if np.isnan(std_val) or std_val == 0:
                std_val = 1
            sampled = np.random.normal(loc=mean_val, scale=std_val)
            if non_negative:
                sampled = max(0, sampled)
            return int(sampled)
        return default

    if not filtered_df2.empty:
        onboard_person = safe_sample_mean_std(filtered_df2, '열차내인원', non_negative=True)
        delta_person = safe_sample_mean_std(filtered_df2, '인원변화')

    else:
        # 요일 제외
        filtered_df2 = final_data[
            (final_data['station_code'] == dataset.station) &
            (final_data['arrivetime'] == dataset.time) &
            (final_data['상하선'] == direction)
        ]
        
        if not filtered_df2.empty:
            onboard_person = safe_sample_mean_std(filtered_df2, '열차내인원', non_negative=True)
            delta_person = safe_sample_mean_std(filtered_df2, '인원변화')
        else:
            onboard_person = 100
            delta_person = 100


    #### 인원변화, 열차내인원은 임의로 설정 ####
    # delta_person = int(np.clip(np.random.normal(loc=14, scale=50), -273, 331))
    # onboard_person = int(np.clip(np.random.normal(loc=640, scale=440), 3, 6324))
    #####################

    model_input = {
        "station_code": dataset.station,
        "상하선": direction,
        "요일": weekday,
        "인원변화": delta_person,
        "열차내인원": onboard_person,
        "train_no": train_no,
        **drop_features
    }

    input_df = pd.DataFrame([model_input])
    X_transformed = preprocessor.transform(input_df)
    predicted = model.predict(X_transformed).tolist()[0]
    
    # result = np.random.uniform(0, 230, size=10).tolist()

    return {
        "predictions": predicted,
        "cars": list(range(1, 11)),
        "model_input": model_input
    }

if __name__ == "__main__":
    print("test")
