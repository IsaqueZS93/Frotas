import streamlit as st
import io
from googleapiclient.http import MediaIoBaseDownload
from backend.services.Service_Google_Drive import get_google_drive_service, search_files

# 🔹 Nome do arquivo no Google Drive
DB_FILE_NAME = "fleet_management.db"

# 🔹 ID da pasta onde o banco de dados está salvo
FOLDER_ID = "1dPaautky1YLzYiH1IOaxgItu_GZSaxcO"  # Substitua pelo ID correto da pasta BDFROTAS

def find_file_id(file_name, folder_id):
    """Busca o ID do arquivo pelo nome dentro da pasta correta."""
    service = get_google_drive_service()
    query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
    files = search_files(query)
    
    if files:
        return files[0]["id"]
    else:
        st.error(f"❌ Arquivo '{file_name}' não encontrado na pasta ID: {folder_id}")
        return None

def download_file(file_id):
    """Baixa um arquivo do Google Drive e permite que o usuário faça o download."""
    try:
        service = get_google_drive_service()
        request = service.files().get_media(fileId=file_id)

        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        file_stream.seek(0)  # Volta ao início do stream
        return file_stream

    except Exception as e:
        st.error(f"❌ Erro ao baixar o arquivo: {e}")
        return None

# 🔹 Interface Streamlit
st.title("📥 Baixar Banco de Dados do Google Drive")

if st.button("🔽 Baixar Banco de Dados"):
    file_id = find_file_id(DB_FILE_NAME, FOLDER_ID)  # Buscar o ID do arquivo dentro da pasta

    if file_id:
        file_stream = download_file(file_id)
        
        if file_stream:
            st.success("✅ Download concluído! Clique abaixo para baixar o arquivo.")

            # Criar botão de download no Streamlit
            st.download_button(
                label="📥 Clique para baixar",
                data=file_stream,
                file_name="fleet_management.db",
                mime="application/x-sqlite3"
            )
