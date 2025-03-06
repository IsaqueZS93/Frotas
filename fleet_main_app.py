import streamlit as st
from backend.services.Service_Google_Drive import list_files_in_folder2

# ID da pasta onde o banco de dados foi armazenado
BDFROTAS_FOLDER_ID = "1dPaautky1YLzYiH1IOaxgItu_GZSaxcO"

st.title("🔍 Teste Avançado de Busca no Google Drive")
st.write(f"📂 Verificando arquivos na pasta ID: {BDFROTAS_FOLDER_ID}...")

# Teste de busca
arquivos = list_files_in_folder2(BDFROTAS_FOLDER_ID)

if arquivos:
    st.success(f"✅ {len(arquivos)} arquivo(s) encontrado(s) na pasta!")
    for arquivo in arquivos:
        st.write(f"📂 {arquivo['name']} - ID: {arquivo['id']}")
else:
    st.error(f"❌ Nenhum arquivo encontrado na pasta ID: {BDFROTAS_FOLDER_ID}!")
    st.warning("🔹 Verifique se o arquivo está na pasta e se a conta de serviço tem permissão.")

