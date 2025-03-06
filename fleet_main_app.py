import streamlit as st
from backend.services.Service_Google_Drive import create_subfolder

# ID da pasta principal "Gestão de Frotas"
PARENT_FOLDER_ID = "1xxod-E9hotXDmQ0z4uMofLHHb8zYqwEy"

# Nome da subpasta a ser criada
SUBFOLDER_NAME = "BDFROTAS"

st.title("📂 Criação de Subpasta no Google Drive")

st.write(f"🔄 Criando/verificando a subpasta '{SUBFOLDER_NAME}' dentro da pasta principal...")

# Criar a subpasta
subfolder_id = create_subfolder(PARENT_FOLDER_ID, SUBFOLDER_NAME)

if subfolder_id:
    st.success(f"✅ Subpasta '{SUBFOLDER_NAME}' criada ou encontrada com sucesso! ID: {subfolder_id}")
else:
    st.error(f"❌ Erro ao criar/verificar a subpasta '{SUBFOLDER_NAME}'.")
