from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# 웹훅 데이터 모델 정의 (선택 사항이지만 권장)
class WebhookPayload(BaseModel):
    event: str
    data: str

@app.post("/webhook")
async def webhook_listener(payload: WebhookPayload):
    # 여기서 웹훅 데이터를 처리하는 로직을 구현합니다.
    # 예: 데이터베이스에 저장, 다른 서비스 호출 등
    print("웹훅 데이터 수신:", payload)

    # 응답을 보냅니다 (선택 사항)
    return {"status": "success", "message": "웹훅 데이터 처리 완료"}

# 또는 Request 객체를 직접 사용하여 데이터 추출
@app.post("/webhook_raw")
async def webhook_listener_raw(request: Request):
    data = await request.json()
    print("웹훅 데이터 수신 (raw):", data)
    return {"status": "success", "message": "웹훅 데이터 처리 완료 (raw)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)