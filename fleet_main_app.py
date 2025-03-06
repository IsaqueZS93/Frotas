import streamlit as st
from backend.services.Service_Google_Drive import list_files_in_folder

# ID da pasta onde o banco de dados foi armazenado
BDFROTAS_FOLDER_ID = "1dPaautky1YLzYiH1IOaxgItu_GZSaxcO"
DB_FILE_NAME = "fleet_management.db"

st.title("🔍 Teste de Busca do Banco de Dados no Google Drive")

st.write(f"📂 Verificando arquivos dentro da pasta ID: {BDFROTAS_FOLDER_ID}...")

# Listar arquivos dentro da pasta
arquivos = list_files_in_folder(BDFROTAS_FOLDER_ID)

if arquivos:
    st.success("✅ Pasta acessada com sucesso!")
    st.write("📄 Arquivos encontrados na pasta:")
    
    encontrado = False
    for arquivo in arquivos:
        st.write(f"📂 {arquivo['name']} - ID: {arquivo['id']}")
        if arquivo["name"] == DB_FILE_NAME:
            encontrado = True
            db_file_id = arquivo["id"]

    if encontrado:
        st.success(f"✅ Banco de dados '{DB_FILE_NAME}' encontrado! ID: {db_file_id}")
    else:
        st.error(f"❌ ERRO: O banco de dados '{DB_FILE_NAME}' não foi encontrado na pasta!")
else:
    st.error("❌ ERRO: Nenhum arquivo encontrado na pasta!")
    st.warning("🔹 Verifique se a conta de serviço tem acesso à pasta.")

