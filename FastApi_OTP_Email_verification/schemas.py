from pydantic import BaseModel, Field


class EmailVerificationRequest(BaseModel):
    Email_id: str




class OTPVerificationRequest(BaseModel):
    Email_id: str = Field(max_length=50)
    otp: str
