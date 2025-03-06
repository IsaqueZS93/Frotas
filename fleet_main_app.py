import streamlit as st
from backend.services.Service_Google_Drive import create_folder

# Nome da pasta que será criada
FOLDER_NAME = "BDFROTAS"

st.title("📂 Criação de Pasta no Google Drive")

st.write(f"🔄 Criando/verificando a pasta `{FOLDER_NAME}` no Google Drive...")

# Chamar a função para criar a pasta
folder_id = create_folder(FOLDER_NAME)

if folder_id:
    st.success(f"✅ Pasta '{FOLDER_NAME}' criada ou encontrada com sucesso! ID: `{folder_id}`")
else:
    st.error(f"❌ Erro ao criar/verificar a pasta `{FOLDER_NAME}`!")
