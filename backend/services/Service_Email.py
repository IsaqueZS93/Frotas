from datetime import datetime
import smtplib
import os
import mimetypes
from email.message import EmailMessage
import streamlit as st  # Importa streamlit para acessar st.secrets
from dotenv import load_dotenv

# Se estivermos em ambiente Streamlit e as secrets estiverem configuradas, use-as;
# caso contrário, carregue as variáveis do arquivo .env.
if hasattr(st, "secrets") and st.secrets:
    EMAIL_SMTP_SERVER = st.secrets["EMAIL_SMTP_SERVER"]
    EMAIL_SMTP_PORT = int(st.secrets["EMAIL_SMTP_PORT"])
    EMAIL_ADDRESS = st.secrets["EMAIL_ADDRESS"]
    EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
    GESTOR_EMAIL = st.secrets.get("GESTOR_EMAIL", "gestor@frotas.com")
else:
    load_dotenv()
    EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER")
    EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT"))
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    GESTOR_EMAIL = os.getenv("GESTOR_EMAIL", "gestor@frotas.com")

def send_email(to_email, subject, body, attachments=None):
    """
    Envia um e-mail via SMTP do Gmail.

    Args:
        to_email (str): Endereço de e-mail do destinatário.
        subject (str): Assunto do e-mail.
        body (str): Corpo do e-mail.
        attachments (list, optional): Lista de caminhos de arquivos a serem anexados.
    
    Returns:
        bool: True se o e-mail for enviado com sucesso, False caso contrário.
    """
    try:
        msg = EmailMessage()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        # Anexar arquivos, se houver
        if attachments:
            for file_path in attachments:
                file_type, _ = mimetypes.guess_type(file_path)
                main_type, sub_type = file_type.split("/", 1) if file_type else ("application", "octet-stream")
                with open(file_path, "rb") as f:
                    msg.add_attachment(
                        f.read(), maintype=main_type, subtype=sub_type, filename=os.path.basename(file_path)
                    )

        # Configuração do servidor SMTP
        with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        print(f"E-mail enviado com sucesso para {to_email}!")
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False

def send_discrepancy_email(to_email, veiculo_placa, checklist_info):
    """
    Envia um e-mail sobre discrepâncias encontradas no checklist de um veículo.

    Args:
        to_email (str): Endereço de e-mail do gestor de frotas.
        veiculo_placa (str): Placa do veículo com discrepâncias.
        checklist_info (str): Informações detalhadas sobre as discrepâncias.
    
    Returns:
        bool: True se o e-mail for enviado com sucesso, False caso contrário.
    """
    subject = f"🚨 Discrepância no Checklist do Veículo {veiculo_placa}"
    body = f"""
    Prezado gestor,

    O seguinte veículo apresentou discrepâncias no checklist:

    🏎 Placa: {veiculo_placa}
    
    🔍 Detalhes das discrepâncias:
    {checklist_info}

    Por favor, verifique e tome as providências necessárias.

    Atenciosamente,
    Equipe de Gestão de Frotas
    """
    return send_email(to_email, subject, body)

def send_report_email(to_email, report_path):
    """
    Envia um e-mail contendo um relatório gerado como anexo.

    Args:
        to_email (str): Endereço de e-mail do destinatário.
        report_path (str): Caminho do arquivo de relatório a ser anexado.
    
    Returns:
        bool: True se o e-mail for enviado com sucesso, False caso contrário.
    """
    subject = "📊 Relatório de Gestão de Frotas"
    body = "Segue anexo o relatório atualizado da frota."
    return send_email(to_email, subject, body, attachments=[report_path])

def send_email_alert(placa, checklist_data):
    """
    Envia um alerta por e-mail caso um checklist apresente discrepâncias.

    Args:
        placa (str): Placa do veículo.
        checklist_data (dict | str): Dados do checklist com problemas ou uma string já formatada.

    Returns:
        bool: True se o e-mail for enviado com sucesso, False caso contrário.
    """
    # Usar o GESTOR_EMAIL carregado
    gestor_email_local = GESTOR_EMAIL

    # Se checklist_data for um dicionário, processar as discrepâncias
    if isinstance(checklist_data, dict):
        discrepancias = [
            f"❌ {chave.replace('_', ' ').title()}" for chave, valor in checklist_data.items() if valor == "NÃO"
        ]
        if not discrepancias:
            return False  # Nenhuma discrepância encontrada, não enviar e-mail
        body = f"""
        🚨 **Alerta de Discrepância no Checklist**

        **Veículo:** {placa}
        **Data:** {datetime.now().strftime("%d/%m/%Y %H:%M")}

        🔍 **Problemas identificados:**
        {chr(10).join(discrepancias)}

        📢 **Ação necessária:** Verifique a condição do veículo e tome as devidas providências.

        **Atenciosamente,**
        Equipe de Gestão de Frotas
        """
    # Se checklist_data for uma string, usar diretamente
    elif isinstance(checklist_data, str):
        body = checklist_data
    else:
        print("❌ Erro: Tipo de dado inválido para checklist_data. Esperado dict ou str.")
        return False

    return send_email(gestor_email_local, f"🚨 Alerta de Problema no Veículo {placa}", body)

if __name__ == "__main__":
    # Teste de envio de e-mail de alerta
    test_data = {
        "pneus_ok": "NÃO",
        "faróis_setas_ok": "SIM",
        "freios_ok": "NÃO",
        "óleo_ok": "NÃO"
    }
    send_email_alert("ABC-1234", test_data)
