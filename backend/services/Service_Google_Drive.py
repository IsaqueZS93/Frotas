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
DB_FILE_PATH = "backend/database/fleet_management.db"
DB_FILE_NAME = "fleet_management.db"

def get_google_drive_service():
    """
    Autentica no Google Drive e retorna um serviço da API.

    - Primeiro, tenta carregar as credenciais do `st.secrets`.
    - Se não encontrar, solicita ao usuário que cole manualmente o JSON de autenticação.
    - Converte e valida o JSON antes de autenticar.
    """
    st.write("🔍 Tentando autenticação no Google Drive...")

    credentials_json = None

    # 🔹 Primeiro, tenta pegar do secrets do Streamlit (útil na nuvem)
    if "GOOGLE_CREDENTIALS" in st.secrets:
        try:
            credentials_json = {
                "type": st.secrets["GOOGLE_CREDENTIALS"]["type"],
                "project_id": st.secrets["GOOGLE_CREDENTIALS"]["project_id"],
                "private_key_id": st.secrets["GOOGLE_CREDENTIALS"]["private_key_id"],
                "private_key": st.secrets["GOOGLE_CREDENTIALS"]["private_key"].replace("\\n", "\n"),
                "client_email": st.secrets["GOOGLE_CREDENTIALS"]["client_email"],
                "client_id": st.secrets["GOOGLE_CREDENTIALS"]["client_id"],
                "auth_uri": st.secrets["GOOGLE_CREDENTIALS"]["auth_uri"],
                "token_uri": st.secrets["GOOGLE_CREDENTIALS"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets["GOOGLE_CREDENTIALS"]["auth_provider_x509_cert_url"],
                "client_x509_cert_url": st.secrets["GOOGLE_CREDENTIALS"]["client_x509_cert_url"],
                "universe_domain": st.secrets["GOOGLE_CREDENTIALS"]["universe_domain"],
            }
        except Exception as e:
            st.error("⚠️ Erro ao carregar credenciais do secrets.toml: " + str(e))

    # 🔹 Se não encontrou nos segredos, pede para o usuário fornecer manualmente o JSON
    if not credentials_json:
        json_input = st.text_area("📥 Cole seu JSON de autenticação do Google Drive aqui:", height=250)
        if st.button("🔑 Autenticar"):
            try:
                credentials_json = json.loads(json_input)
                credentials_json["private_key"] = credentials_json["private_key"].replace("\\n", "\n")
                st.success("✅ JSON válido! Prosseguindo com a autenticação.")
            except Exception as e:
                st.error("❌ JSON inválido. Verifique o formato: " + str(e))
                return None

    # 🔹 Se ainda não tiver credenciais, aborta
    if not credentials_json:
        st.error("❌ Nenhuma credencial válida encontrada. Autenticação abortada.")
        return None

    # 🔹 Criar credenciais do Google Drive com as informações obtidas
    try:
        creds = Credentials.from_service_account_info(credentials_json, scopes=SCOPES)
        st.success("✅ Autenticado via Conta de Serviço com sucesso!")
        return build("drive", "v3", credentials=creds)
    except Exception as e:
        st.error("❌ Erro ao autenticar no Google Drive: " + str(e))
        return None

# Configuração do Google Drive
FLEETBD_FOLDER_ID = "1TeLkfzLxKCMR060z5kd8uNOXev1qLPda"  # ID correto da pasta no Google Drive
DB_FILE_NAME = "fleet_management.db"  # Nome do banco no Drive


def list_files_in_folder(folder_id):
    """Lista todos os arquivos dentro da pasta do Google Drive (debug)."""
    service = get_google_drive_service()
    if not service:
        return []

    try:
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id, name)"
        ).execute()
        return results.get("files", [])
    except Exception as e:
        st.error(f"❌ Erro ao listar arquivos na pasta: {e}")
        return []

def load_database_into_memory():
    """Carrega o banco de dados do Google Drive para a memória."""

    service = get_google_drive_service()
    if not service:
        return None

    st.write("🔄 Buscando banco de dados no Google Drive...")

    # 🔹 LISTA TODOS OS ARQUIVOS NA PASTA PARA DEBUG
    files_in_drive = list_files_in_folder(FLEETBD_FOLDER_ID)
    st.write("📂 Arquivos encontrados na pasta:", files_in_drive)

    # 🔹 TENTAR ENCONTRAR O BANCO EXATO NO DRIVE
    existing_files = [
        file for file in files_in_drive if file["name"].strip() == DB_FILE_NAME
    ]

    if not existing_files:
        st.error(f"❌ O banco de dados '{DB_FILE_NAME}' não foi encontrado no Google Drive!")
        return None

    file_id = existing_files[0]["id"]
    request = service.files().get_media(fileId=file_id)

    file_stream = io.BytesIO()
    downloader = MediaIoBaseDownload(file_stream, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    file_stream.seek(0)  # Retorna ao início do stream

    # Conecta ao banco de dados diretamente da memória
    conn = sqlite3.connect(":memory:")  # Criar um banco SQLite temporário na RAM
    with conn:
        with open("temp_db.sqlite", "wb") as temp_db:
            temp_db.write(file_stream.read())  # Salva temporariamente para conexão

        temp_conn = sqlite3.connect("temp_db.sqlite")
        temp_conn.backup(conn)  # Copia os dados para o banco na memória
        temp_conn.close()
    
    st.success("✅ Banco de dados carregado da nuvem para a memória!")
    return conn

from backend.services.Service_Google_Drive import get_google_drive_service

def list_files_in_folder2(folder_id):
    """ Lista todos os arquivos dentro de uma pasta no Google Drive """
    try:
        service = get_google_drive_service()
        query = f"'{folder_id}' in parents and trashed=false"  # 🔹 Busca arquivos dentro da pasta
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get("files", [])
        
        if not files:
            print(f"❌ Nenhum arquivo encontrado na pasta ID: {folder_id}")
        else:
            print(f"📂 {len(files)} arquivo(s) encontrado(s) na pasta ID: {folder_id}")
            for file in files:
                print(f"  - {file['name']} (ID: {file['id']})")

        return files

    except Exception as e:
        print(f"❌ Erro ao listar arquivos na pasta {folder_id}: {e}")
        return []


def upload_database():
    """ Envia ou atualiza o banco de dados no Google Drive """
    
    # Verifica se o banco de dados existe antes do upload
    if not os.path.exists(DB_FILE_PATH):
        st.error("❌ Erro: O banco de dados não foi encontrado localmente. Nenhum upload foi realizado.")
        return

    service = get_google_drive_service()
    if not service:
        return

    file_metadata = {
        "name": DB_FILE_NAME,
        "parents": [FLEETBD_FOLDER_ID]
    }

    media = MediaFileUpload(DB_FILE_PATH, resumable=True)

    existing_files = service.files().list(
        q=f"name='{DB_FILE_NAME}' and '{FLEETBD_FOLDER_ID}' in parents",
        fields="files(id)"
    ).execute().get("files", [])

    if existing_files:
        file_id = existing_files[0]["id"]
        service.files().update(fileId=file_id, media_body=media).execute()
        st.success("✅ Banco de dados atualizado no Google Drive!")
    else:
        service.files().create(body=file_metadata, media_body=media).execute()
        st.success("✅ Banco de dados salvo no Google Drive pela primeira vez!")

def download_database():
    """ Baixa o banco de dados do Google Drive e substitui o local """
    service = get_google_drive_service()
    if not service:
        return

    existing_files = service.files().list(
        q=f"name='{DB_FILE_NAME}' and '{FLEETBD_FOLDER_ID}' in parents",
        fields="files(id)"
    ).execute().get("files", [])

    if not existing_files:
        st.warning("⚠️ Nenhum backup encontrado no Google Drive. Criando um novo banco local.")
        return

    file_id = existing_files[0]["id"]
    request = service.files().get_media(fileId=file_id)

    with open(DB_FILE_PATH, "wb") as file:
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

    st.success("✅ Banco de dados restaurado do Google Drive!")

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
    """Lista todos os arquivos dentro da pasta do Google Drive (debug)."""
    service = get_google_drive_service()
    if not service:
        return []

    try:
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id, name)"
        ).execute()
        return results.get("files", [])
    except Exception as e:
        st.error(f"❌ Erro ao listar arquivos na pasta: {e}")
        return []

def load_database_into_memory():
    """Carrega o banco de dados do Google Drive para a memória."""

    service = get_google_drive_service()
    if not service:
        return None

    st.write("🔄 Buscando banco de dados no Google Drive...")

    # 🔹 LISTA TODOS OS ARQUIVOS NA PASTA PARA DEBUG
    files_in_drive = list_files_in_folder(FLEETBD_FOLDER_ID)
    st.write("📂 Arquivos encontrados na pasta:", files_in_drive)

    # 🔹 TENTAR ENCONTRAR O BANCO EXATO NO DRIVE
    existing_files = [
        file for file in files_in_drive if file["name"].strip() == DB_FILE_NAME
    ]

    if not existing_files:
        st.error(f"❌ O banco de dados '{DB_FILE_NAME}' não foi encontrado no Google Drive!")
        return None

    file_id = existing_files[0]["id"]
    request = service.files().get_media(fileId=file_id)

    file_stream = io.BytesIO()
    downloader = MediaIoBaseDownload(file_stream, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    file_stream.seek(0)  # Retorna ao início do stream

    # Conecta ao banco de dados diretamente da memória
    conn = sqlite3.connect(":memory:")  # Criar um banco SQLite temporário na RAM
    with conn:
        with open("temp_db.sqlite", "wb") as temp_db:
            temp_db.write(file_stream.read())  # Salva temporariamente para conexão

        temp_conn = sqlite3.connect("temp_db.sqlite")
        temp_conn.backup(conn)  # Copia os dados para o banco na memória
        temp_conn.close()
    
    st.success("✅ Banco de dados carregado da nuvem para a memória!")
    return conn
    
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
