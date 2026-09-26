import resend
from dotenv import load_dotenv
import os

# load .env
load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

r = resend.Emails.send({
  "from": "onboarding@resend.dev",
  "to": os.getenv("MAIL_TEST"),
  "subject": "Hello World",
  "html": "<p>Congrats on sending your <strong>first email</strong>!</p>"
})
