import streamlit as st
import io
import os
from googleapiclient.http import MediaIoBaseDownload
from backend.services.Service_Google_Drive import get_google_drive_service

# 🔹 ID do arquivo no Google Drive (substitua pelo correto se necessário)
FILE_ID = "1u-kwDCVRq-fNRRv1NsUbpiqOM8rz_LeW"  # ID real do arquivo

def download_file(file_id):
    """Baixa um arquivo do Google Drive e permite que o usuário faça o download."""
    try:
        service = get_google_drive_service()
        request = service.files().get_media(fileId=file_id)
        
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        file_stream.seek(0)  # Volta ao início do stream

        return file_stream

    except Exception as e:
        st.error(f"❌ Erro ao baixar o arquivo: {e}")
        return None

# 🔹 Interface Streamlit
st.title("📥 Baixar Banco de Dados do Google Drive")

if st.button("🔽 Baixar Banco de Dados"):
    file_stream = download_file(FILE_ID)
    
    if file_stream:
        st.success("✅ Download concluído! Clique abaixo para baixar o arquivo.")
        
        # Oferecer o download para o usuário
        st.download_button(
            label="📥 Clique para baixar",
            data=file_stream,
            file_name="fleet_management.db",
            mime="application/x-sqlite3"
        )
