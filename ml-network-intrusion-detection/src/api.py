import io
import json
from contextlib import asynccontextmanager
import pandas as pd
import joblib
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .common import ROOT, FEATURES, validate_frame

@asynccontextmanager
async def lifespan(app):
    app.state.model = joblib.load(ROOT/'models/model.joblib')
    app.state.metrics = json.loads((ROOT/'models/metrics.json').read_text())
    yield

app = FastAPI(title='ML Network Intrusion Detection', lifespan=lifespan)
app.mount('/static', StaticFiles(directory=ROOT/'web'), name='static')

class TrafficRecord(BaseModel):
    features: dict[str, str | int | float | None]

@app.get('/')
def index(): return FileResponse(ROOT/'web/index.html')

@app.get('/health')
def health(): return {'status':'ok','model_loaded':True}

@app.get('/model-info')
def info():
    return {'algorithm':'Random Forest (100 trees)', 'dataset':'NSL-KDD KDDTrain+ / KDDTest+', 'classification':'Normal / Attack', 'expected_features':FEATURES,'metrics':app.state.metrics}

def predict(df):
    try: X = validate_frame(df, max_rows=10000)
    except (ValueError, TypeError) as exc: raise HTTPException(422,str(exc)) from exc
    model = app.state.model
    labels = model.predict(X)
    probabilities = model.predict_proba(X)
    rows = [{'record':i+1,'prediction':'Attack' if label else 'Normal','confidence':round(float(probabilities[i,label]),4)} for i,label in enumerate(labels)]
    attacks = int(labels.sum())
    return {'total':len(rows),'normal':len(rows)-attacks,'attack':attacks,'attack_percentage':round(attacks/len(rows)*100,2),'rows':rows}

@app.post('/predict')
def predict_one(record: TrafficRecord): return predict(pd.DataFrame([record.features]))

@app.post('/predict-file')
async def predict_file(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith('.csv'): raise HTTPException(400,'Upload a .csv file')
    data = await file.read(5_000_001)
    if len(data)>5_000_000: raise HTTPException(413,'Maximum file size is 5 MB')
    try: df = pd.read_csv(io.BytesIO(data))
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeError) as exc: raise HTTPException(400,'Invalid CSV') from exc
    return predict(df)
