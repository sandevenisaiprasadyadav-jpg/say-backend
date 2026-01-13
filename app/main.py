from fastapi import FastAPI

app = FastAPI(title="SAY Backend", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "SAY backend is running"}


