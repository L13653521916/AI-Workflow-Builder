from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import engine, Base
from routes.auth import router as auth_router
from routes.chat import router as chat_router
from routes.workflow import router as workflow_router
from routes.knowledge import router as knowledge_router
from routes.tools import router as tools_router
from routes.execution import router as execution_router
from routes.models import router as models_router

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(chat_router, prefix=settings.API_V1_PREFIX)
app.include_router(workflow_router, prefix=settings.API_V1_PREFIX)
app.include_router(knowledge_router, prefix=settings.API_V1_PREFIX)
app.include_router(tools_router, prefix=settings.API_V1_PREFIX)
app.include_router(execution_router, prefix=settings.API_V1_PREFIX)
app.include_router(models_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {"message": "AI Workflow Builder API"}


@app.get("/health")
def health():
    return {"status": "ok"}