import streamlit as st
from backend.services.Service_Google_Drive import list_files_in_folder

# ID da pasta no Google Drive
FLEETBD_FOLDER_ID = "https://drive.google.com/drive/folders/1TeLkfzLxKCMR060z5kd8uNOXev1qLPda"

st.title("🔍 Teste de Acesso ao Google Drive")

st.write("📂 Verificando acesso à pasta do Google Drive...")

# Listar arquivos na pasta
arquivos = list_files_in_folder(FLEETBD_FOLDER_ID)

if arquivos:
    st.success("✅ Pasta acessada com sucesso!")
    st.write("📄 Arquivos encontrados na pasta:", arquivos)
else:
    st.error("❌ ERRO: Nenhum arquivo encontrado na pasta!")
    st.warning("🔹 Verifique se a conta de serviço tem acesso à pasta.")
