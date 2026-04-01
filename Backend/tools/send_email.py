"""
Tool de envío de email via Resend API (HTTP).
Reemplaza el envío SMTP que falla en entornos con puerto 587 bloqueado.

Variables de entorno requeridas:
    RESEND_API_KEY      → API key de Resend (starts with 're_...')
    EMAIL_REMITENTE     → Email del remitente (debe pertenecer al dominio verificado en Resend)

Variables de entorno para la firma (opcionales, tienen valores por defecto):
    FIRMA_NOMBRE    → nombre del remitente
    FIRMA_CARGO     → cargo / puesto
    FIRMA_EMPRESA   → nombre de la empresa
    FIRMA_TELEFONO  → teléfono de contacto
    FIRMA_EMAIL     → email visible en la firma (por defecto usa EMAIL_REMITENTE)
"""

import os
import requests

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
    """Envía un email via Resend API al destinatario indicado.

    Args:
        recipient_email: Dirección de correo del destinatario.
        subject: Asunto del email.
        body: Cuerpo del email en texto plano (sin firma, se añade automáticamente).
    """
    api_key      = os.getenv("RESEND_API_KEY")
    sender_email = os.getenv("EMAIL_REMITENTE")

    if not api_key:
        return "Error: Variable RESEND_API_KEY no configurada en .env"
    if not sender_email:
        return "Error: Variable EMAIL_REMITENTE no configurada en .env"

    full_body = body + _build_signature()

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from":    sender_email,
                "to":      [recipient_email],
                "subject": subject,
                "text":    full_body,
            },
            timeout=15,
        )

        if response.status_code == 200:
            return f"Email enviado exitosamente a {recipient_email}"
        else:
            return f"Error Resend {response.status_code}: {response.text}"

    except requests.exceptions.Timeout:
        return "Error: Timeout al conectar con Resend API"
    except Exception as e:
        return f"Error al enviar email: {str(e)}"
