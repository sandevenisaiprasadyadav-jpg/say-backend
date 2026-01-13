from fastapi import FastAPI

app = FastAPI(title="SAY Backend", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "SAY backend is running"}
from app.routers import wallet, payments

app.include_router(wallet.router)
app.include_router(payments.router)


