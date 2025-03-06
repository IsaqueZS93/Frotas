import streamlit as st
from backend.services.Service_Google_Drive import list_files_in_folder

# ID da pasta no Google Drive (verifique se está correto)
FLEETBD_FOLDER_ID = "1TeLkfzLxKCMR060z5kd8uNOXev1qLPda"
DB_FILE_NAME = "fleet_management.db"

st.title("🔍 Teste Completo de Acesso ao Google Drive")

st.write("📂 Verificando acesso à pasta do Google Drive...")

# Listar arquivos na pasta
arquivos = list_files_in_folder(FLEETBD_FOLDER_ID)

if arquivos:
    st.success(f"✅ Pasta acessada com sucesso! {len(arquivos)} arquivos encontrados.")
    
    # Exibir lista de arquivos
    st.subheader("📄 Arquivos encontrados:")
    for file in arquivos:
        st.write(f"📄 **Nome:** {file['name']} | 🆔 ID: {file['id']} | 📦 Tamanho: {file.get('size', 'Desconhecido')} bytes")

    # **Caso 1: O arquivo esperado está na pasta?**
    db_files = [file for file in arquivos if file["name"].lower() == DB_FILE_NAME.lower()]
    if db_files:
        st.success(f"✅ Banco de dados encontrado: {db_files[0]['name']} (ID: {db_files[0]['id']})")
    else:
        st.warning("⚠️ O arquivo 'fleet_management.db' não foi encontrado com esse nome exato.")

    # **Caso 2: Existem arquivos com nome semelhante?**
    similar_files = [file for file in arquivos if "fleet_management" in file["name"].lower()]
    if similar_files:
        st.info("📌 Foram encontrados arquivos similares:")
        for file in similar_files:
            st.write(f"📄 {file['name']} (ID: {file['id']})")
    else:
        st.warning("⚠️ Nenhum arquivo parecido com 'fleet_management.db' foi encontrado.")

else:
    st.error("❌ ERRO: Nenhum arquivo encontrado na pasta! O ID da pasta pode estar errado ou vazio.")
    st.warning("🔹 Verifique se a conta de serviço tem acesso à pasta.")
