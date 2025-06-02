import numpy as np
import pandas as pd
import pickle
from pydantic import BaseModel
from typing import Literal
from datetime import datetime


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


def load_model_and_preprocessor(model_path="model.pkl", preproc_path="preprocessing.pkl"):
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    with open(preproc_path, "rb") as f:
        processed = pickle.load(f)
    return model, processed["preprocessor"]

def load_drop_info(path="drop_info.csv"):
    drop_df = pd.read_csv(path)
    drop_df["drop"] = drop_df["drop"].apply(eval)
    return drop_df

def load_final_data(path="final_final_final.csv"):
    return pd.read_csv(path)

def get_weekday_code(date_str: str) -> str:
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    weekday_raw = date_obj.weekday()
    if weekday_raw == 5:
        return "1"  # 토요일
    elif weekday_raw == 6:
        return "2"  # 일요일 + 공휴일
    else:
        return "0"  # 평일

def get_drop_features(drop_df: pd.DataFrame, station_code: int, direction: str) -> dict:
    row = drop_df[
        (drop_df["station_code"] == station_code) &
        (drop_df["direction"] == direction)
    ]
    drop_list = row.iloc[0]["drop"] if not row.empty else []
    return {f"drop_{i}": int(i in drop_list) for i in range(1, 11)}

def estimate_train_no(df: pd.DataFrame, station_code: int, time: str, direction: str) -> str:
    filtered_df = df[
        (df["station_code"] == station_code) &
        (df["arrivetime"] == time) &
        (df["상하선"] == direction)
    ]
    if not filtered_df.empty:
        return str(filtered_df["train_no"].mode().iloc[0])
    
    hundred_digit = station_code // 100
    if hundred_digit == 3:
        return "3288"
    elif hundred_digit == 4:
        return "K4649"
    else:
        return "9999"


def sample_passenger_info(
    df: pd.DataFrame,
    station: int,
    time: str,
    direction: str,
    weekday: str,
    default: int = 100
):
    df_full = df[
        (df['station_code'] == station) &
        (df['arrivetime'] == time) &
        (df['상하선'] == direction) &
        (df['요일'] == int(weekday))
    ]

    if not df_full.empty:
        onboard = safe_sample_mean_std(df_full, '열차내인원', non_negative=True)
        delta = safe_sample_mean_std(df_full, '인원변화')
        return onboard, delta

    else:
        df_loose = df[
            (df['station_code'] == station) &
            (df['arrivetime'] == time) &
            (df['상하선'] == direction)
        ]
        if not df_loose.empty:
            onboard = safe_sample_mean_std(df_loose, '열차내인원', non_negative=True)
            delta = safe_sample_mean_std(df_loose, '인원변화')
            return onboard, delta

    return default, default

# 모델 인풋 정의
class PredictionInput(BaseModel):
    line: str        
    station: int      
    direction: Literal["up", "down"]
    date: str
    time: str
