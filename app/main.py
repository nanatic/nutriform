from fastapi import FastAPI
from app.config.settings import get_settings
from app.handlers import anthropometry, patients, users, questionnaires, doctors, admin, questions, submissions

settings = get_settings()

app = FastAPI(
    title="Nutriform API",
    version="1.0.0",
    description="Сервис для работы с пациентами, опросниками и антропометрией",
    docs_url="/",  # 👈 Открывает Swagger сразу по корневому URL
    redoc_url=None  # 👈 Отключаем ReDoc, если не нужно
)

app.include_router(patients)
app.include_router(users)
app.include_router(doctors)
app.include_router(questionnaires)
app.include_router(questions)
app.include_router(submissions)
app.include_router(anthropometry)
app.include_router(admin)



if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
