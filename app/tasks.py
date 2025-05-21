import os
from email.message import EmailMessage

from aiosmtplib import send
from celery import shared_task

from app.infrastructure.db.session import SessionLocal
from app.infrastructure.repositories.user_repository import UserRepository
from formulas import bsa_mosteller, bmr_mifflin, Sex
from .celery_app import celery
from .infrastructure.db.models import Users


@celery.task
def send_admin_report():
    # собрать статистику по врачам и пациентам
    db = SessionLocal()
    repo = UserRepository(db)
    stats = {}
    # например, по каждому доктору
    for user in db.query(Users).filter(Users.role == "doctor"):
        stats[user.email] = repo.get_patient_stats(str(user.id), all_patients=True)
    # собрать письмо
    text = "\n".join(f"{email}: {s}" for email, s in stats.items())
    msg = EmailMessage()
    msg["Subject"] = "[Nutriform] Daily Doctors Report"
    msg["From"] = os.getenv("FROM_EMAIL")
    msg["To"] = os.getenv("ADMIN_EMAIL")
    msg.set_content(text)
    send(
        msg,
        hostname=os.getenv("SMTP_HOST"),
        port=int(os.getenv("SMTP_PORT", 587)),
        start_tls=True,
        username=os.getenv("SMTP_USER"),
        password=os.getenv("SMTP_PASS"),
    )


@shared_task
def recalc_body_metrics(patient_id: int, weight: float, height: float,
                        age: int, sex_str: str):
    sex = Sex(sex_str)
    bsa = bsa_mosteller(weight, height)
    bmr = bmr_mifflin(weight, height, age, sex)
