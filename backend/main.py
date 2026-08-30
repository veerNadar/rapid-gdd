from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import projects, reviews, sections

app = FastAPI(title="Rapid GDD API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(sections.router)
app.include_router(reviews.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
