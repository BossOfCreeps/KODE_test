import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from account.views import router as account_router
from messages.views import router as messages_router

app = FastAPI()
app.mount("/media", StaticFiles(directory="media"), name="media")

# routing
app.include_router(account_router)
app.include_router(messages_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
