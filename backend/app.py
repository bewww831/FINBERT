import os, warnings, matplotlib
warnings.filterwarnings('ignore')
matplotlib.use("Agg")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from xgboost_model import predict_xgboost
from sentiment_model import predict_sentiment
from cnn_model import predict_cnn
from decision import run_decision_engine

BASE_DIR = os.path.dirname(__file__)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/assets", StaticFiles(directory=os.path.join(BASE_DIR, "../assets")), name="assets")

class TickerRequest(BaseModel):
    ticker: str

@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(BASE_DIR, "../index.html"))

@app.get("/models")
def serve_models():
    return FileResponse(os.path.join(BASE_DIR, "../models.html"))

@app.get("/about")
def serve_about():
    return FileResponse(os.path.join(BASE_DIR, "../about.html"))

@app.get("/health")
def health():
    return {"status": "ok", "models": ["xgboost", "finbert", "cnn"]}

@app.get("/prices")
def prices():
    import yfinance as yf
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA",
               "JPM", "BAC", "GS", "XOM", "CVX", "JNJ", "PFE", "WMT", "HD"]
    try:
        data = yf.download(tickers, period="2d", auto_adjust=True, progress=False)
        closes = data["Close"]
        result = []
        for t in tickers:
            try:
                prices = closes[t].dropna()
                if len(prices) < 2:
                    continue
                prev  = float(prices.iloc[-2])
                curr  = float(prices.iloc[-1])
                chg   = ((curr - prev) / prev) * 100
                result.append({
                    "ticker": t,
                    "price":  round(curr, 2),
                    "change": round(chg, 2)
                })
            except Exception:
                continue
        return JSONResponse(content={"prices": result})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/predict")
def predict(req: TickerRequest):
    ticker = req.ticker.upper().strip()
    try:
        ts     = predict_xgboost(ticker)
        sent   = predict_sentiment(ticker)
        cnn    = predict_cnn(ticker)
        engine = run_decision_engine(ts, sent, cnn)
        return JSONResponse(content={
            "ticker":     ticker,
            "status":     "success",
            "timeseries": ts,
            "sentiment":  sent,
            "cnn":        cnn,
            "decision":   engine
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})