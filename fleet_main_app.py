import streamlit as st
from backend.services.Service_Google_Drive import search_files, download_file

# 🔹 ID da pasta onde o banco de dados está salvo
BDFROTAS_FOLDER_ID = "1dPaautky1YLzYiH1IOaxgItu_GZSaxcO"
DB_FILE_NAME = "fleet_management.db"
OUTPUT_PATH = "backend/database/fleet_management.db"  # Caminho onde o banco será salvo

st.write("🔍 Buscando o arquivo no Google Drive...")

# 🔹 Busca o arquivo pelo nome dentro da pasta
query = f"name='{DB_FILE_NAME}' and '{BDFROTAS_FOLDER_ID}' in parents and trashed=false"
arquivos = search_files(query)

if arquivos:
    file_id = arquivos[0]["id"]  # Pega o primeiro encontrado
    st.write(f"✅ Arquivo encontrado! ID: {file_id}")
    
    # 🔄 Iniciando download do banco de dados
    st.write("📥 Baixando o banco de dados...")
    download_file(file_id, OUTPUT_PATH)
    
    st.success("✅ Download concluído! Banco de dados atualizado com sucesso.")
else:
    st.error("❌ O banco de dados não foi encontrado na pasta BDFROTAS!")
