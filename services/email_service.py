"""
services/email_service.py

Este módulo fornece uma função para enviar e-mails utilizando o servidor SMTP do Gmail.
As configurações são carregadas a partir das variáveis de ambiente definidas no arquivo de configuração.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from config import EMAIL_CONFIG

def send_email(subject, message, recipient):
    """
    Envia um e-mail utilizando as configurações do Gmail.
    
    Parâmetros:
        subject (str): O assunto do e-mail.
        message (str): O corpo do e-mail em texto simples.
        recipient (str ou list): O(s) destinatário(s) do e-mail.
        
    Retorna:
        bool: True se o e-mail foi enviado com sucesso, False caso contrário.
    """
    try:
        # Cria a mensagem MIME
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG["email_address"]
        
        # Se recipient for uma lista, converte para string separada por vírgulas
        if isinstance(recipient, list):
            msg['To'] = ", ".join(recipient)
        else:
            msg['To'] = recipient
        
        msg['Subject'] = subject
        
        # Adiciona o corpo do e-mail à mensagem
        msg.attach(MIMEText(message, 'plain'))
        
        # Conecta ao servidor SMTP do Gmail
        server = smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
        server.starttls()  # Inicia a conexão segura
        server.login(EMAIL_CONFIG["email_address"], EMAIL_CONFIG["email_password"])
        
        # Converte a mensagem para string e envia
        server.sendmail(EMAIL_CONFIG["email_address"], recipient, msg.as_string())
        server.quit()
        print("E-mail enviado com sucesso.")
        return True
    except Exception as e:
        print("Erro ao enviar e-mail:", e)
        return False

# Exemplo de uso: Esse código pode ser executado separadamente para testar o envio de e-mail.
if __name__ == "__main__":
    subject = "Teste de E-mail"
    message = "Olá, este é um teste de envio de e-mail via SMTP do Gmail."
    recipient = "destinatario@example.com"  # Substitua pelo e-mail de teste desejado
    
    send_email(subject, message, recipient)
