from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.auth import router as auth_router
from src.api.task import router as task_router

openapi_tags = [
    {"name": "Authentication", "description": "User sign up, login, and authentication related endpoints."},
    {"name": "Tasks", "description": "Endpoints for creating, updating, deleting, and organizing tasks."}
]

app = FastAPI(
    title="Task Management Backend API",
    description="Backend API for a fullstack task management application. Provides REST endpoints for authentication, task management, status change, assignment, and more.",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
def health_check():
    """Check API health status."""
    return {"message": "Healthy"}

# Register core routers
app.include_router(auth_router)
app.include_router(task_router)
