from fastapi import FastAPI
from app.db.database import Base, engine

app = FastAPI(
    title="Marketing Campaign Management"
    )

Base.metadata.create_all(bind=engine)
