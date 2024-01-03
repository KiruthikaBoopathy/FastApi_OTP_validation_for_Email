import datetime
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
import schemas
from models import OTPSend
from database import engine, SessionLocal

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# Email configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = 'kiruthika.b@vrdella.com'
EMAIL_PASSWORD = 'renm kixf nlxy avbx'


def generate_otp() -> str:
    return str(random.randint(10000, 99999))


def send_email_otp(email, otp):
    subject = ' Hi KAVYA '
    body = f'Your updated OTP is: {otp}'

    msg = MIMEMultipart()
    msg.attach(MIMEText(body, 'plain'))
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = email

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, email, msg.as_string())


@app.post("/request_otp_email", tags=["OTP_send_validation"])
def request_otp_email(
        email_verification_request: schemas.EmailVerificationRequest,
        db: Session = Depends(get_db)
):
    Email_ID = email_verification_request.Email_id
    formatted_email = ''.join(filter(str.isalnum, Email_ID))
    otp = generate_otp()

    existing_otp_info = db.query(models.OTPSend).filter(models.OTPSend.Email_Id == Email_ID).first()

    if existing_otp_info:
        existing_otp_info.OTP = otp
        db.commit()
        response = {"message": "OTP updated successfully", "otp": otp, "formatted_email": formatted_email}
    else:
        otp_info = models.OTPSend(Email_Id=Email_ID, OTP=otp, Verification="Invalid")
        db.add(otp_info)
        db.commit()
        response = {"message": "OTP sent successfully", "otp": otp, "formatted_email": formatted_email}

    send_email_otp(Email_ID, otp)
    return response


@app.post("/otp_validation_request", tags=["OTP_send_validation"])
def verify_otp(otp_validation_request: schemas.OTPVerificationRequest, db: Session = Depends(get_db)):
    entered_otp = otp_validation_request.otp
    Email_ID = otp_validation_request.Email_id

    # Retrieve OTP information from the database
    otp_info = db.query(models.OTPSend).filter(models.OTPSend.Email_Id == Email_ID).first()

    if entered_otp == otp_info.OTP:
        otp_info.Verification = "Valid"
        db.commit()
        return {"message": "OTP verification successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid OTP")
