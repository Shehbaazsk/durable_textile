from email.mime.application import MIMEApplication
from pathlib import Path
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr

from app.config.setting import get_settings


settings = get_settings()


EMAIL_CONFIF = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    TEMPLATE_FOLDER=Path(__file__).resolve().parent.parent.parent / 'templates'
)


class EmailRequest(BaseModel):
    subject: str
    body: str | None = None
    template_body: dict | None = None
    template_name: str = None
    to_email: EmailStr
    is_html: bool = False
    attachments: list[dict] | None = None


async def send_email(email_request: EmailRequest):
    attachments = []

    if email_request.attachments:
        for attachment in email_request.attachments:
            attachment_file = MIMEApplication(
                attachment['content'], _subtype="octet-stream")
            attachment_file.add_header(
                'Content-Disposition', 'attachment', filename=attachment['filename'])
            attachments.append(attachment_file)

    fm = FastMail(EMAIL_CONFIF)

    if email_request.template_body:
        message = MessageSchema(
            subject=email_request.subject,
            recipients=[email_request.to_email],
            template_body=email_request.template_body,
            subtype=MessageType.html,
            attachments=attachments
        )
        try:
            await fm.send_message(message, template_name=email_request.template_name)
        except Exception as e:
            raise e
    else:
        message = MessageSchema(
            subject=email_request.subject,
            recipients=[email_request.to_email],
            body=email_request.body,
            subtype=MessageType.html if email_request.is_html else MessageType.plain,
            attachments=attachments
        )
        try:
            await fm.send_message(message)
        except Exception as e:
            raise e
