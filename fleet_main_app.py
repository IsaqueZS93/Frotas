from backend.services.Service_Google_Drive import search_files

# 🔍 Definir a query para buscar o arquivo no Google Drive
file_name = "fleet_management.db"
query = f"name='{file_name}' and trashed=false"

# 🔎 Executar a busca
st.write("🔍 Buscando arquivos no Google Drive...")
files_found = search_files(query)

# 📌 Exibir os resultados encontrados
if files_found:
    st.success(f"✅ {len(files_found)} arquivo(s) encontrado(s) com o nome '{file_name}':")
    for file in files_found:
        st.write(f"📂 Nome: {file['name']} - ID: {file['id']} - Link: {file.get('webViewLink', 'Sem link')}")
else:
    st.error(f"❌ Nenhum arquivo encontrado com o nome '{file_name}' no Google Drive!")
    st.warning("🔹 Verifique se o arquivo está na pasta correta e se a conta de serviço tem permissão.")
