from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.routes import graph

app = FastAPI(
    title="DecentrlAI API",
    description="Backend API for DecentrlAI Investigation Engine",
    version="0.1.0",
)

# Allow Next.js frontend to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graph.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
