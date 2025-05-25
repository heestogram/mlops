import os
import pickle
import pandas as pd
import numpy as np
from pydantic import BaseModel, conlist
from typing import List, Literal
from fastapi import FastAPI, Body

# with open("model.pkl", "rb") as f:
#     model = pickle.load(f)
# with open("transform.pkl","rb") as f:
#     trans = pickle.load(f) 
    
# class Dataset(BaseModel):
#     data: List

# app = FastAPI()

# @app.post("/predict")
# def get_prediction(dataset: Dataset):
#     data = dict(dataset)['data']   ## [ {'x1': 123, 'x2': 456} ]
#     data = pd.DataFrame(data=[data[0].values()], columns=data[0].keys())

#     # ## x variables preprocessing 
#     x_cols = ['V'+str(i) for i in range(1,28)]
#     test_x = trans.transform(data[x_cols])

#     # ## make prediction for testset
#     pred = model.predict(test_x)

#     print(pred)
#     return {"prediction": pred[0], "input_column_names": x_cols}


app = FastAPI()

class PredictionInput(BaseModel):
    line: str        
    station: str      
    direction: Literal["up", "down"]


@app.post("/predict")
def predict(dataset: PredictionInput):
    # 임의의 예측값 반환 (0~230% 사이)
    
    result = np.random.uniform(0, 230, size=10).tolist()

    return {
        "predictions": result,
        "cars": list(range(1, 11))  # 1호차 ~ 10호차
    }

if __name__ == "__main__":
    print("test")
