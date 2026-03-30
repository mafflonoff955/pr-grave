from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.config import settings
from app.routes.analyze import router as analyze_router

load_dotenv()

app = FastAPI(
    title="PR Graveyard API",
    description="GitHub PR and CI/CD analysis — calculate the real cost of developer friction",
    version="1.0.0",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)


@app.get("/health")
async def health():
    return {"status": "ok", "tokenConfigured": bool(settings.GITHUB_TOKEN)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)