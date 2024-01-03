from sqlalchemy import Column, Integer, String
from database import Base


class OTPSend(Base):
    __tablename__ = "email_otp"
    id = Column(Integer, primary_key=True, index=True)
    Email_Id = Column(String(50))
    OTP = Column(String(10))
    Verification = Column(String(15))