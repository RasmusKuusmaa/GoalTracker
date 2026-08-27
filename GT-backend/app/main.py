from fastapi import FastAPI

app = FastAPI(title="Goal Tracker")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
