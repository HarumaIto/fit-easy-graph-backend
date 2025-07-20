from fastapi import FastAPI, HTTPException
from scraper import fetch_congestion_info

app = FastAPI()

@app.get("/congestion")
def get_congestion():
    try:
        info = fetch_congestion_info()
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))