from fastapi import FastAPI
from db.database import engine, Base
from api import auth_routes, node_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sentinel Monitoring System")

app.include_router(auth_routes.router)
app.include_router(node_routes.router)


@app.get("/")
def root():
    return {"message": "Sentinel Server Running"}


@app.get("/health")
def health():
    return {"status": "ok"}