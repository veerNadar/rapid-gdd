from fastapi import FastAPI

app = FastAPI(title="Rapid GDD API")


@app.get("/health")
def health_check():
    return {"status": "ok"}
