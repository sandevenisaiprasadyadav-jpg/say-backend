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
from fastapi_utils.tasks import repeat_every
from app.utils import close_matured_fds

@app.on_event("startup")
@repeat_every(seconds=60)  # runs every minute
def fd_scheduler() -> None:
    close_matured_fds()


