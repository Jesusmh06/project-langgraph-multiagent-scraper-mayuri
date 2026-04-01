"""
Tool de envío de email por SMTP (Gmail).
Usa APP_PASSWORD_GMAIL para autenticación.

Variables de entorno para la firma (opcionales, tienen valores por defecto):
    FIRMA_NOMBRE    → nombre del remitente
    FIRMA_CARGO     → cargo / puesto
    FIRMA_EMPRESA   → nombre de la empresa
    FIRMA_TELEFONO  → teléfono de contacto
    FIRMA_EMAIL     → email visible en la firma (por defecto usa EMAIL_REMITENTE)
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from langchain_core.tools import tool


def _build_signature() -> str:
    """Construye la firma del correo desde variables de entorno con valores por defecto."""
    nombre   = os.getenv("FIRMA_NOMBRE",   "Tu Nombre")
    cargo    = os.getenv("FIRMA_CARGO",    "Tu Cargo")
    empresa  = os.getenv("FIRMA_EMPRESA",  "Nombre de tu Empresa")
    telefono = os.getenv("FIRMA_TELEFONO", "Tu Teléfono")
    email    = os.getenv("FIRMA_EMAIL",    os.getenv("EMAIL_REMITENTE", "Tu Email"))

    return (
        "\n\nQuedo atento a su respuesta.\n\n"
        "Cordialmente,\n\n"
        f"{nombre}\n"
        f"{cargo}\n"
        f"{empresa}\n"
        f"{telefono}\n"
        f"{email}"
    )


@tool
def send_email(recipient_email: str, subject: str, body: str) -> str:
    """Envia un email via SMTP de Gmail al destinatario indicado.

    Args:
        recipient_email: Direccion de correo del destinatario.
        subject: Asunto del email.
        body: Cuerpo del email en texto plano (sin firma, se añade automáticamente).
    """
    sender_email = os.getenv("EMAIL_REMITENTE")
    app_password = os.getenv("APP_PASSWORD_GMAIL")

    if not sender_email or not app_password:
        return "Error: Variables EMAIL_REMITENTE o APP_PASSWORD_GMAIL no configuradas en .env"

    full_body = body + _build_signature()

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(full_body, "plain", "utf-8"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        return f"Email enviado exitosamente a {recipient_email}"
    except Exception as e:
        return f"Error al enviar email: {str(e)}"
