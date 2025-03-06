import streamlit as st
from backend.services.Service_Google_Drive import list_files_in_folder, get_folder_id_by_name

# Nome da pasta no Google Drive
FOLDER_NAME = "Gestão de Frotas"
DB_FILE_NAME = "fleet_management.db"

st.title("🔍 Teste Completo de Acesso ao Google Drive")

st.write(f"📂 Buscando ID da pasta: `{FOLDER_NAME}`...")

# 🔍 Buscar o ID da pasta pelo nome
folder_id = get_folder_id_by_name(FOLDER_NAME)

if folder_id:
    st.success(f"✅ Pasta encontrada! ID: `{folder_id}`")
    
    # Listar arquivos na pasta
    st.write("📂 Verificando arquivos dentro da pasta...")
    arquivos = list_files_in_folder(folder_id)

    if arquivos:
        st.success(f"✅ {len(arquivos)} arquivos encontrados na pasta.")

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
        st.error("❌ Nenhum arquivo encontrado na pasta! Verifique se o nome da pasta está correto.")
else:
    st.error(f"❌ ERRO: A pasta `{FOLDER_NAME}` não foi encontrada no Google Drive!")
    st.warning("🔹 O nome da pasta pode estar errado ou a conta de serviço pode não ter acesso.")
