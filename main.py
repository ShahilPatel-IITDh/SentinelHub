from fastapi import FastAPI
from db.database import engine, Base
from routes import auth_routes, node_routes

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sentinel Monitoring System")

# Include routers
app.include_router(auth_routes.router)
app.include_router(node_routes.router)


@app.get("/")
def root():
    return {"message": "Sentinel Server Running"}


@app.get("/health")
def health():
    return {"status": "ok"}