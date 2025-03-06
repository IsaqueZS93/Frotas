import streamlit as st
from backend.services.Service_Google_Drive import download_file

# 🔹 ID do arquivo encontrado no Google Drive
FILE_ID = "1u-kwDCVRq-fNRRv1NsUbpiqOM8rz_LeW"
OUTPUT_PATH = "backend/database/fleet_management.db"  # Caminho onde o banco será salvo

st.write("🔄 Baixando o banco de dados do Google Drive...")

# 🔹 Tentar baixar o arquivo
try:
    download_file(FILE_ID, OUTPUT_PATH)
    st.success(f"✅ Download concluído! Arquivo salvo em: {OUTPUT_PATH}")
except Exception as e:
    st.error(f"❌ Erro ao baixar o arquivo: {e}")
