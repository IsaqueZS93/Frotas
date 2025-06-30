import smtplib
from email.message import EmailMessage

EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587
EMAIL_ADDRESS = "frotasnovaes@gmail.com"
EMAIL_PASSWORD = "iaoz txod pzrl cipa"  # Senha de app gerada

# Configuração da mensagem de e-mail
msg = EmailMessage()
msg["From"] = EMAIL_ADDRESS
msg["To"] = "destinatario@exemplo.com"  # Altere para o e-mail do destinatário
msg["Subject"] = "Teste de envio de e-mail"
msg.set_content("Olá,\n\nEste é um teste de envio de e-mail usando Python e Gmail SMTP.\n\nAtenciosamente,\nFrotas")

try:
    # Conecta ao servidor SMTP e envia o e-mail
    with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

    print("E-mail enviado com sucesso!")
except Exception as e:
    print("Erro ao enviar o e-mail:", e)
