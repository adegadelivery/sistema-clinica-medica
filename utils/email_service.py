import os
import smtplib
from email.mime.text import MIMEText

def enviar_email(destino, nome, data, hora, medico):

    try:
        msg = MIMEText(f"""
Olá {nome},

Sua consulta foi agendada com sucesso.

Médico: {medico}
Data: {data}
Hora: {hora}

Clínica Médica
""")

        msg["Subject"] = "Confirmação de Consulta"
        msg["From"] = os.environ.get("MAIL_FROM", "clinica@sistema.com")
        msg["To"] = destino

        mail_user = os.environ.get("MAIL_USER", "9829e3f30a54aa")
        mail_pass = os.environ.get("MAIL_PASS", "dbda4137031405")

        servidor = smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525, timeout=5)
        servidor.starttls()
        servidor.login(mail_user, mail_pass)
        servidor.send_message(msg)
        servidor.quit()

        print(f"[EMAIL] Enviado para {destino}")

    except Exception as e:
        print(f"[EMAIL] Erro ao enviar para {destino}:", e)