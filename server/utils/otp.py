# AgriCare/server/utils/otp.py

from email.message import EmailMessage
import random, string
from utils.redis import redis
from fastapi import BackgroundTasks, HTTPException
from config import Config
import aiosmtplib

def generate_otp(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))

async def check_rate_limit(email: str) -> str:
    # Rate Limit
    otp_key = f"otp:{email}"
    count_key = f"otp_count:{email}"
    
    try:
        otp_count = await redis.get(count_key)

        if otp_count and int(otp_count) >= 3:
            ttl = await redis.ttl(count_key)
            raise HTTPException(status_code=429, detail=f"OTP limit exceeded. Try again in {ttl // 60} minutes.")
        
        # OTP Logic
        otp = generate_otp()
        print(f"📧 Generated OTP for {email}: {otp}")  # Debug log
        await redis.setex(otp_key, 3600, otp)

        await redis.incr(count_key)
        if otp_count is None:
            await redis.expire(count_key, 3600)

        return otp
    except HTTPException:
        # Re-raise HTTP exceptions (like rate limit exceeded)
        raise
    except Exception as e:
        # Log the error and generate OTP anyway (fallback behavior)
        print(f"⚠️ Redis error in check_rate_limit: {e}")
        otp = generate_otp()
        print(f"📧 Generated OTP (fallback) for {email}: {otp}")
        return otp

async def send_otp_to_email(email: str, otp: str):
    message = EmailMessage()
    message["From"] = f"{Config.EMAIL_NAME} <{Config.EMAIL_USERNAME}>"
    message["To"] = email
    message["Subject"] = "Your AgriCare OTP"
    message.set_content(f"Your OTP is: {otp}. It will expire in 1 hour.")

    try:
        await aiosmtplib.send(
            message,
            hostname=Config.SMTP_HOST,
            port=Config.SMTP_PORT,
            start_tls=True,
            username=Config.EMAIL_USERNAME,
            password=Config.EMAIL_PASSWORD
        )
        print(f"✅ OTP email sent successfully to {email}")
    except Exception as e:
        print(f"❌ Failed to send OTP email to {email}: {e}")
        raise


async def verify_email_otp(email: str, otp: str) -> bool:
    otp_key = f"otp:{email}"
    
    try:
        saved_otp = await redis.get(otp_key)
        print(f"🔍 Verifying OTP for {email}: provided={otp}, saved={saved_otp}")

        if saved_otp is None:
            print(f"❌ No OTP found for {email}")
            return False
        
        # Ensure both are strings and strip whitespace
        if str(saved_otp).strip() == str(otp).strip():
            await redis.delete(otp_key)
            print(f"✅ OTP verified successfully for {email}")
            return True
        
        print(f"❌ OTP mismatch for {email}")
        return False
    except Exception as e:
        print(f"⚠️ Redis error in verify_email_otp: {e}")
        # If Redis fails, we can't verify - return False for security
        return False
