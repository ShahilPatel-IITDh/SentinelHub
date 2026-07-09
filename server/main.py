from fastapi import FastAPI # type: ignore
from db.database import engine, Base
from routes import auth_routes, node_routes
from scripts.seed_posts import seed_posts

app = FastAPI(title="Sentinel Monitoring System")
# # Create DB tables
# Base.metadata.create_all(bind=engine)
# # Seed default posts
# seed_posts()
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    seed_posts()

# Include routers
app.include_router(auth_routes.router)
app.include_router(node_routes.router)

# Basic endpoints for testing
@app.get("/")
def root():
    return {"message": "Sentinel Server Running"}

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    