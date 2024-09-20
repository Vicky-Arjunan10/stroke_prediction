from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union, Optional  # Optional is now included
from datetime import date
from database import StrokePrediction, session
from sqlalchemy.sql import and_
import joblib
import logging
import pandas as pd

# Initialize FastAPI app
app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Pydantic models
class HeartStrokePrediction(BaseModel):
    gender: str
    age: int
    hypertension: int
    diseases: int
    glucose: float
    bmi: float

class PredictionRequest(BaseModel):
    data: Union[HeartStrokePrediction, List[HeartStrokePrediction]]  # Accepts either a single prediction or a list

# Load models and scalers
le = joblib.load('Models/label_encoder.joblib')
scaler = joblib.load('Models/scaler.joblib')
model = joblib.load('Models/logistic_regression_model.joblib')

def preprocess_and_predict(df: pd.DataFrame) -> List[str]:
    try:
        df['gender'] = le.transform(df['gender'])
        X_scaled = scaler.transform(df)  # Use transform, not fit_transform
        logger.info(f"Input shape: {X_scaled.shape}")
        y_pred = model.predict(X_scaled).tolist()
        result = ['high' if x == 1 else 'low' for x in y_pred]
        logger.info(f"Predictions: {result}")
        return result
    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

def insert_data(data: HeartStrokePrediction, result: str, source: str):
    table_data = StrokePrediction(
        gender=data.gender,
        age=data.age,
        hypertension=data.hypertension,
        heart_diseases=data.diseases,
        glucose=data.glucose,
        bmi=data.bmi,
        result=result,
        source=source,
    )
    session.add(table_data)
    session.commit()

@app.post('/predict')
def predict(request: PredictionRequest):
    if isinstance(request.data, list):
        # Multi-prediction
        dict_data = [row.dict() for row in request.data]
        input_data = pd.DataFrame(dict_data)
        predictions = preprocess_and_predict(input_data)

        for i in range(len(request.data)):
            insert_data(request.data[i], predictions[i], 'Scheduled')
        return predictions
    else:
        # Single prediction
        dict_data = request.data.dict()
        input_data = pd.DataFrame([dict_data])
        predictions = preprocess_and_predict(input_data)
        insert_data(request.data, predictions[0], 'webapp')
        return predictions[0]

@app.get('/past_predictions')
def past_prediction(start: date, end: date, source: Optional[str] = None):
    try:
        query = session.query(StrokePrediction).filter(
            and_(
                StrokePrediction.created_date >= start,
                StrokePrediction.created_date <= end
            )
        )
        if source and source != "All":
            query = query.filter(StrokePrediction.source == source)

        result = query.all()
        return result
    except Exception as e:
        logger.error(f"Error fetching past predictions: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
