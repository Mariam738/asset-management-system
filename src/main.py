from fastapi import FastAPI
from src.utils.db import Base, engine
from src.assets.router import assets_routes
from src.auth.router import auth_routes
from src.relationships.router import relationships_routes
from src.graph.router import graph_routes
from contextlib import asynccontextmanager
from src.utils.scheduler import start_scheduler

# @app.on_event("startup")
# async def startup():
#     Base.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)

    scheduler = start_scheduler()
    yield

    scheduler.shutdown()

app = FastAPI(title="Asset Management System", lifespan=lifespan)


app.include_router(assets_routes)
app.include_router(auth_routes)
app.include_router(relationships_routes)
app.include_router(graph_routes)