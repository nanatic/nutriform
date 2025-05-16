from fastapi import FastAPI
from app.config.settings import get_settings
from app.handlers import anthropometry, patients, users, questionnaires

settings = get_settings()

app = FastAPI(
    title="Nutriform API",
    version="1.0.0",
    description="Сервис для работы с пациентами, опросниками и антропометрией"
)

app.include_router(patients)
app.include_router(users)
app.include_router(questionnaires)
app.include_router(anthropometry)
