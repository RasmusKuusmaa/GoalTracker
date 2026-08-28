from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.commitments import router as commitments_router
from app.api.completions import router as completions_router
from app.api.goals import router as goals_router
from app.api.journal_entries import router as journal_entries_router
from app.api.journals import router as journals_router
from app.core.config import settings

app = FastAPI(title="Goal Tracker")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(commitments_router)
app.include_router(completions_router)
app.include_router(goals_router)
app.include_router(journal_entries_router)
app.include_router(journals_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
