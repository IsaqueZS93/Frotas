import os
import pickle
import streamlit as st
import io
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from dotenv import load_dotenv

# Carregar variáveis de ambiente (útil para ambientes locais)
load_dotenv()

# Definir escopo de acesso (permite gerenciar arquivos no Google Drive)
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Caminho do arquivo token (usado anteriormente em autenticação OAuth, mas não será utilizado na nuvem)
TOKEN_PATH = "backend/config/token.pickle"

import os
import json
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_google_drive_service():
    """
    Autentica no Google Drive e retorna um serviço da API.
    
    - Recupera as credenciais do `st.secrets`
    - Reconstrói o JSON original antes de autenticar
    - Reformata a `private_key` para corrigir problemas de padding
    """
    st.write("🔍 Tentando autenticação no Google Drive...")

    if "GOOGLE_SERVICE_ACCOUNT" in st.secrets:
        try:
            st.write("✅ Credenciais carregadas. Reconstruindo JSON...")

            # 🔹 Recupera os dados do secrets e reestrutura para o formato JSON correto
            service_account_info = {
                "type": st.secrets["GOOGLE_SERVICE_ACCOUNT"]["type"],
                "project_id": st.secrets["GOOGLE_SERVICE_ACCOUNT"]["project_id"],
                "private_key_id": st.secrets["GOOGLE_SERVICE_ACCOUNT"]["private_key_id"],
                "private_key": st.secrets["GOOGLE_SERVICE_ACCOUNT"]["private_key"].replace('\\n', '\n'),  # Corrigir quebras de linha
                "client_email": st.secrets["GOOGLE_SERVICE_ACCOUNT"]["client_email"],
                "client_id": st.secrets["GOOGLE_SERVICE_ACCOUNT"]["client_id"],
                "auth_uri": st.secrets["GOOGLE_SERVICE_ACCOUNT"]["auth_uri"],
                "token_uri": st.secrets["GOOGLE_SERVICE_ACCOUNT"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets["GOOGLE_SERVICE_ACCOUNT"]["auth_provider_x509_cert_url"],
                "client_x509_cert_url": st.secrets["GOOGLE_SERVICE_ACCOUNT"]["client_x509_cert_url"]
            }

            # Depuração: Exibir JSON reconstruído
            st.json(service_account_info)

            # Criar credenciais do Google Drive
            creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
            st.success("✅ Autenticado via Conta de Serviço.")
            return build("drive", "v3", credentials=creds)

        except Exception as e:
            st.error(f"⚠️ Erro ao carregar credenciais de conta de serviço: {e}")

    else:
        st.error("❌ Conta de serviço NÃO encontrada em `st.secrets`.")

    st.error("❌ Nenhuma credencial válida encontrada. Verifique `secrets.toml`.")
    raise Exception("Falha na autenticação do Google Drive.")

def create_folder(folder_name):
    """
    Cria uma pasta no Google Drive e retorna seu ID.
    Se a pasta já existir, retorna o ID existente.
    """
    try:
        service = get_google_drive_service()
        
        # Verifica se a pasta já existe
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        folders = results.get("files", [])

        if folders:
            print(f"📂 Pasta '{folder_name}' já existe. Usando ID existente: {folders[0]['id']}")
            return folders[0]['id']

        # Se a pasta não existe, criar uma nova
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder"
        }

        folder = service.files().create(body=file_metadata, fields="id").execute()
        folder_id = folder.get("id")

        if not folder_id:
            raise Exception("Falha ao criar a pasta no Google Drive.")

        print(f"✅ Pasta '{folder_name}' criada com sucesso! ID: {folder_id}")
        return folder_id

    except Exception as e:
        print(f"❌ Erro ao criar pasta: {e}")
        return None  # Retorna None caso ocorra um erro

def upload_file_to_drive(file_path, folder_id=None):
    """Faz upload de um arquivo para uma pasta no Google Drive e retorna o link público."""
    try:
        service = get_google_drive_service()
        file_metadata = {"name": os.path.basename(file_path)}
        if folder_id:
            file_metadata["parents"] = [folder_id]

        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields="id, webViewLink").execute()
        return file.get("webViewLink")
    except Exception as e:
        print(f"❌ Erro ao fazer upload: {e}")
        return None

def upload_images_to_drive(file_paths, folder_id):
    """Faz upload de múltiplos arquivos do sistema local para uma pasta no Google Drive e retorna os IDs das imagens."""
    try:
        service = get_google_drive_service()
        
        uploaded_file_ids = []
        for file_path in file_paths:
            file_name = os.path.basename(file_path)  # 🔹 Pega apenas o nome do arquivo
            
            file_metadata = {"name": file_name, "parents": [folder_id]}
            media = MediaFileUpload(file_path, mimetype="image/jpeg", resumable=True)
            file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            
            uploaded_file_ids.append(file.get("id"))

        return uploaded_file_ids
    except Exception as e:
        print(f"❌ Erro ao fazer upload de imagens: {e}")
        return []

def download_file(file_id, output_path):
    """Baixa um arquivo do Google Drive pelo ID e salva localmente."""
    try:
        service = get_google_drive_service()
        request = service.files().get_media(fileId=file_id)
        with open(output_path, "wb") as file:
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
    except Exception as e:
        print(f"❌ Erro ao baixar arquivo: {e}")
        
def list_files_in_folder(folder_id):
    """Lista todos os arquivos dentro de uma pasta do Google Drive."""
    try:
        service = get_google_drive_service()
        query = f"'{folder_id}' in parents and trashed=false"
        results = service.files().list(q=query, fields="files(id, name, webViewLink)").execute()
        return results.get("files", [])
    except Exception as e:
        print(f"❌ Erro ao listar arquivos na pasta {folder_id}: {e}")
        return []
    
def get_folder_id_by_name(folder_name):
    """Busca o ID de uma pasta pelo nome, se ela já existir no Google Drive."""
    try:
        service = get_google_drive_service()
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        folders = results.get("files", [])
        return folders[0]['id'] if folders else None
    except Exception as e:
        print(f"❌ Erro ao buscar a pasta {folder_name}: {e}")
        return None

def update_file(file_id, new_file_path):
    """Substitui um arquivo existente no Google Drive por um novo."""
    try:
        service = get_google_drive_service()
        media = MediaFileUpload(new_file_path, mimetype="image/jpeg", resumable=True)
        file = service.files().update(fileId=file_id, media_body=media).execute()
        print(f"✅ Arquivo atualizado com sucesso: {file_id}")
        return file.get("id")
    except Exception as e:
        print(f"❌ Erro ao atualizar arquivo {file_id}: {e}")
        return None
    
def create_subfolder(parent_folder_id, subfolder_name):
    """
    Cria uma subpasta dentro de uma pasta principal no Google Drive.
    Retorna o ID da subpasta, ou o ID existente se já existir.
    """
    try:
        service = get_google_drive_service()

        # Verifica se a subpasta já existe
        query = f"name='{subfolder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false and '{parent_folder_id}' in parents"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        folders = results.get("files", [])

        if folders:
            print(f"📂 Subpasta '{subfolder_name}' já existe. Usando ID existente: {folders[0]['id']}")
            return folders[0]['id']

        # Criar a subpasta se não existir
        file_metadata = {
            "name": subfolder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_folder_id]
        }

        folder = service.files().create(body=file_metadata, fields="id").execute()
        folder_id = folder.get("id")

        if not folder_id:
            raise Exception(f"Erro ao criar a subpasta '{subfolder_name}'.")

        print(f"✅ Subpasta '{subfolder_name}' criada com sucesso! ID: {folder_id}")
        return folder_id

    except Exception as e:
        print(f"❌ Erro ao criar subpasta: {e}")
        return None

def delete_file(file_id):
    """Exclui um arquivo do Google Drive pelo ID."""
    try:
        service = get_google_drive_service()
        service.files().delete(fileId=file_id).execute()
        print(f"✅ Arquivo {file_id} excluído com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao excluir arquivo: {e}")

def search_files(query):
    """Busca arquivos no Google Drive com base em uma consulta (query)."""
    try:
        service = get_google_drive_service()
        results = service.files().list(q=query, fields="files(id, name, webViewLink)").execute()
        return results.get("files", [])
    except Exception as e:
        print(f"❌ Erro ao buscar arquivos: {e}")
        return []

if __name__ == "__main__":
    print("🔍 Teste da integração com Google Drive.")

    # Criar uma pasta de teste
    folder_id = create_folder("Teste_Pasta")
    print(f"Pasta criada com ID: {folder_id}")

    # Fazer upload de um arquivo de teste
    test_file = "teste.jpg"  # Certifique-se de que esse arquivo existe no diretório de teste
    if os.path.exists(test_file):
        file_link = upload_file_to_drive(test_file, folder_id)
        print(f"📁 Arquivo enviado com sucesso: {file_link}")

    # Buscar arquivos no Google Drive
    files = search_files("name contains 'teste'")
    print("📄 Arquivos encontrados:", files)
