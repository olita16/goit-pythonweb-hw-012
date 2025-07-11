"""
Головний модуль застосунку Contacts API.

Цей модуль ініціалізує та налаштовує FastAPI застосунок, включаючи
middleware, маршрути, обробники винятків та налаштування бази даних.
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from src.db.connect import get_db, engine
from src.db.models import Base
from src.routers import contacts, auth, users
from src.services.limiter import limiter

app = FastAPI()

# Middleware для CORS (дозволяє крос-домени запити)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware для обмеження кількості запитів (rate limiting)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Створення всіх таблиць, описаних у моделях SQLAlchemy
Base.metadata.create_all(bind=engine)

@app.get("/", name="API root")
def get_index():
    """
    Головна (коренева) точка входу API.

    Повертає:
        dict: Вітальне повідомлення.
    """
    return {"message": "Welcome to contacts API"}

@app.get("/health", name="Перевірка стану сервісу")
def get_health_status(db=Depends(get_db)):
    """
    Перевірка доступності API та бази даних.

    Аргументи:
        db: Сесія бази даних (SQLAlchemy).

    Повертає:
        dict: Повідомлення про готовність сервісу.

    Викликає:
        HTTPException: Якщо база даних недоступна.
    """
    try:
        result = db.execute(text("SELECT 1+1")).fetchone()
        if result is None:
            raise Exception
        return {"message": "API is ready to work"}
    except Exception:
        raise HTTPException(status_code=503, detail="База даних недоступна")

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Обробник помилки перевищення ліміту запитів.

    Аргументи:
        request (Request): Об’єкт HTTP-запиту.
        exc (RateLimitExceeded): Виняток перевищення ліміту.

    Повертає:
        JSONResponse: Відповідь з кодом 429 та повідомленням про помилку.
    """
    return JSONResponse(
        status_code=429,
        content={"detail": "Перевищено ліміт запитів. Спробуйте пізніше."},
    )

# Підключення роутерів до основного застосунку
app.include_router(contacts.router)
app.include_router(auth.router)
app.include_router(users.router)
