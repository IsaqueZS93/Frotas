import streamlit as st
import io
import os
from googleapiclient.http import MediaIoBaseDownload
from backend.services.Service_Google_Drive import get_google_drive_service

# 🔹 ID do arquivo no Google Drive (substitua pelo correto se necessário)
FILE_ID = "1u-kwDCVRq-fNRRv1NsUbpiqOM8rz_LeW"  # ID real do arquivo

def download_file(file_id, output_path):
    """Baixa um arquivo do Google Drive e salva no caminho escolhido."""
    try:
        service = get_google_drive_service()
        request = service.files().get_media(fileId=file_id)
        
        with open(output_path, "wb") as file:
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        
        st.success(f"✅ Download concluído! Arquivo salvo em: {output_path}")
    
    except Exception as e:
        st.error(f"❌ Erro ao baixar o arquivo: {e}")

# 🔹 Interface Streamlit para escolher caminho de salvamento
st.title("📥 Baixar Banco de Dados do Google Drive")

# Campo de entrada para o caminho de salvamento
save_path = st.text_input("📂 Digite o caminho para salvar o arquivo:", "backend/database/fleet_management.db")

if st.button("🔽 Baixar Banco de Dados"):
    if not save_path.strip():
        st.warning("⚠️ Por favor, digite um caminho válido para salvar o arquivo.")
    else:
        download_file(FILE_ID, save_path)
