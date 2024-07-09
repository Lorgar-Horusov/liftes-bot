from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date
from database import get_logs
import uvicorn


app = FastAPI()


# Модель для входных данных
class LogRequest(BaseModel):
    token: str
    time_from: Optional[date] = None
    time_to: Optional[date] = None


# Проверка токена (замените на реальную проверку)
def validate_token(token: str):
    valid_tokens = ["SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"]
    if token not in valid_tokens:
        raise HTTPException(status_code=403, detail="Invalid token")


@app.post("/get_logs")
def fetch_logs(request: LogRequest):
    validate_token(request.token)

    today = date.today()
    current_day = today.strftime('%Y-%m-%d')
    time_from = request.time_from if request.time_from else current_day
    time_to = request.time_to if request.time_to else current_day

    logs = get_logs(time_from, time_to)
    logs = {"logs": logs}
    return logs


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
