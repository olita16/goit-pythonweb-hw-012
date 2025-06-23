from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from src.databases.connect import get_db
from src.routers import contacts, auth, users
from src.databases.models import init_db


from src.services.limiter import limiter


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


if __name__ == "__main__":
    from src.databases.models import init_db

    init_db()


@app.get("/", name="API root")
def get_index():
    return {"message": "Welcome to contacts API"}


@app.get("/health", name="Service availability")
def get_health_status(db=Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1+1")).fetchone()
        if result is None:
            raise Exception
        return {"message": "API is ready to work"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database is not available")


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."},
    )


app.include_router(contacts.router)
app.include_router(auth.router)
app.include_router(users.router)
