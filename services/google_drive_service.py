"""
services/google_drive_service.py

Este módulo gerencia a integração com o Google Drive utilizando a API do Google.
Ele realiza a autenticação via OAuth 2.0 e fornece funções para upload de arquivos e criação de pastas.
"""

import os
import pickle
import io
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload  # Correção da importação
from config import GOOGLE_DRIVE_CONFIG
from googleapiclient.errors import HttpError


# Escopo necessário para acessar arquivos no Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Caminho para salvar o token de autenticação
TOKEN_PATH = 'token.pickle'

def authenticate_google_drive():
    """
    Autentica e retorna um serviço da API do Google Drive.

    O fluxo utiliza um token salvo localmente (token.pickle) para reutilização.
    Se o token não existir ou estiver expirado, inicia o fluxo OAuth.

    Retorna:
        service (googleapiclient.discovery.Resource): Objeto de serviço para interagir com a API.
    """
    creds = None

    # Verifica se já existe um token salvo
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

    # Se não houver credenciais válidas, inicia o fluxo OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("🔑 Iniciando fluxo OAuth para autenticação no Google Drive...")
            flow = InstalledAppFlow.from_client_config({
                "installed": {
                    "client_id": GOOGLE_DRIVE_CONFIG["client_id"],
                    "client_secret": GOOGLE_DRIVE_CONFIG["client_secret"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            }, SCOPES)
            creds = flow.run_local_server(
                port=8080,
                authorization_prompt_message="🔗 Autorize o acesso ao Google Drive no link acima.",
                success_message="✅ Autenticação concluída com sucesso! Você pode fechar esta janela."
            )
        # Salva o token para reutilização futura
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)

    # Constrói e retorna o serviço do Google Drive
    return build('drive', 'v3', credentials=creds)

def get_or_create_drive_folder(folder_name, parent_folder_id=None):
    """
    Verifica se uma pasta existe no Google Drive. Se não existir, cria uma nova pasta.

    Parâmetros:
        folder_name (str): Nome da pasta a ser verificada/criada.
        parent_folder_id (str, opcional): ID da pasta pai.

    Retorna:
        str: ID da pasta existente ou recém-criada.
    """
    service = authenticate_google_drive()

    # Verifica se a pasta já existe
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"

    existing_folders = service.files().list(q=query, fields="files(id, name)").execute()
    if existing_folders.get("files"):
        return existing_folders["files"][0]["id"]

    # Se a pasta não existir, cria uma nova
    folder_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder"
    }
    if parent_folder_id:
        folder_metadata["parents"] = [parent_folder_id]

    folder = service.files().create(body=folder_metadata, fields="id").execute()
    return folder["id"]

def create_drive_folder(folder_name, parent_folder_id=None):
    """
    Cria uma pasta no Google Drive.

    Parâmetros:
        folder_name (str): Nome da pasta a ser criada.
        parent_folder_id (str, opcional): ID da pasta onde a nova pasta será criada.

    Retorna:
        str: ID da pasta criada.
    """
    service = authenticate_google_drive()

    # Verifica se a pasta pai existe
    if parent_folder_id:
        parent_check = service.files().get(fileId=parent_folder_id).execute()
        if not parent_check:
            raise ValueError(f"Erro: Pasta pai com ID {parent_folder_id} não encontrada no Google Drive.")

    # Verifica se a pasta já existe para evitar duplicações
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"

    existing_folders = service.files().list(q=query, fields="files(id, name)").execute()
    if existing_folders.get("files"):
        folder_id = existing_folders["files"][0]["id"]
        print(f"📂 A pasta '{folder_name}' já existe no Google Drive. ID: {folder_id}")
        return folder_id

    # Criar a nova pasta se não existir
    folder_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder"
    }
    if parent_folder_id:
        folder_metadata["parents"] = [parent_folder_id]

    folder = service.files().create(body=folder_metadata, fields="id").execute()
    print(f"📁 Pasta '{folder_name}' criada no Google Drive. ID: {folder['id']}")
    return folder["id"]

def upload_file_to_drive(file_bytes, filename, mime_type, folder_id):
    """
    Faz o upload de um arquivo para o Google Drive e define permissão pública para download.

    Parâmetros:
        file_bytes (io.BytesIO): O conteúdo do arquivo.
        filename (str): Nome do arquivo.
        mime_type (str): Tipo MIME do arquivo (ex.: 'image/jpeg').
        folder_id (str): ID da pasta onde o arquivo será armazenado.

    Retorna:
        dict | None: Dados do arquivo no Google Drive, incluindo o ID.
    """
    try:
        service = authenticate_google_drive()  # Autenticação no Google Drive
        
        file_metadata = {
            "name": filename,
            "parents": [folder_id]
        }
        media = MediaIoBaseUpload(file_bytes, mimetype=mime_type, resumable=True)

        file = service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()

        file_id = file.get("id")

        if file_id:
            # 🔹 FORÇA PERMISSÃO PÚBLICA PARA QUALQUER USUÁRIO ACESSAR
            permission = {
                "type": "anyone",  # Qualquer pessoa pode acessar
                "role": "reader"   # Apenas leitura (sem edição)
            }
            service.permissions().create(fileId=file_id, body=permission).execute()

            return {"id": file_id}
    
    except Exception as e:
        print(f"❌ Erro ao fazer upload para o Google Drive: {e}")
        return None

def set_public_permission(file_id):
    """
    Define a permissão pública de um arquivo no Google Drive.

    Parâmetros:
        file_id (str): ID do arquivo no Google Drive.
    """
    try:
        service = authenticate_google_drive()
        permission = {
            "type": "anyone",  # Qualquer pessoa pode acessar
            "role": "reader"   # Apenas leitura (sem edição)
        }
        service.permissions().create(fileId=file_id, body=permission).execute()
        print(f"✅ Permissão pública aplicada ao arquivo {file_id}")

    except Exception as e:
        print(f"❌ Erro ao aplicar permissão pública: {e}")



def get_folder_id_by_name(folder_name, parent_folder_id):
    """
    Busca o ID de uma pasta dentro de outra pasta no Google Drive pelo nome.
    """
    drive_service = authenticate_google_drive()  # 🔹 Obtém o serviço do Google Drive
    query = f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and name='{folder_name}'"
    
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get("files", [])

    if folders:
        return folders[0]["id"]
    return None

def list_files_in_folder(folder_id):
    """
    Lista os arquivos dentro de uma pasta do Google Drive.
    """
    drive_service = authenticate_google_drive()  # 🔹 Obtém o serviço do Google Drive
    query = f"'{folder_id}' in parents and mimeType contains 'image/'"

    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    return results.get("files", [])

def upload_file_to_drive2(file_bytes, filename, mime_type, folder_id):
    """
    Faz o upload de um arquivo diretamente da memória (sem salvar localmente) para o Google Drive.

    Parâmetros:
        file_bytes (bytes): Conteúdo do arquivo carregado pelo usuário.
        filename (str): Nome do arquivo a ser salvo no Google Drive.
        mime_type (str): Tipo MIME do arquivo (ex.: 'image/jpeg').
        folder_id (str): ID da pasta onde o arquivo será armazenado.

    Retorna:
        dict: Metadados do arquivo enviado, incluindo o ID do arquivo no Drive.
    """
    service = authenticate_google_drive()

    file_metadata = {
        "name": filename,
        "parents": [folder_id]
    }

    media = MediaIoBaseUpload(io.BytesIO(file_bytes.getvalue()), mimetype=mime_type, resumable=True)


    file_drive = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    print(f"📤 Arquivo '{filename}' enviado para o Google Drive. ID: {file_drive['id']}")
    return file_drive

def delete_drive_folder(folder_id):
    """
    Exclui uma pasta do Google Drive e todo o seu conteúdo.

    Parâmetros:
        folder_id (str): ID da pasta a ser excluída.

    Retorna:
        bool: True se a exclusão foi bem-sucedida, False caso contrário.
    """
    service = authenticate_google_drive()
    try:
        # Exclui a pasta e todo o conteúdo dentro dela
        service.files().delete(fileId=folder_id).execute()
        print(f"🗑️ Pasta {folder_id} excluída do Google Drive.")
        return True
    except Exception as e:
        print(f"⚠️ Erro ao excluir a pasta {folder_id}: {e}")
        return False
def delete_new_folders_from_drive(parent_folder_id):
    """
    Busca e exclui todas as pastas chamadas 'New Folder' dentro da pasta especificada no Google Drive.

    Parâmetros:
        parent_folder_id (str): ID da pasta principal onde as pastas 'New Folder' serão apagadas.

    Retorna:
        list: Lista com os nomes das pastas excluídas.
    """
    service = authenticate_google_drive()
    deleted_folders = []

    try:
        # 🔍 Busca por todas as pastas chamadas "New Folder" dentro da pasta "Imagens Veículos"
        query = f"name='New Folder' and mimeType='application/vnd.google-apps.folder' and '{parent_folder_id}' in parents"
        folders = service.files().list(q=query, fields="files(id, name)").execute()

        for folder in folders.get("files", []):
            folder_id = folder["id"]
            folder_name = folder["name"]
            # 🚮 Apaga a pasta encontrada
            service.files().delete(fileId=folder_id).execute()
            deleted_folders.append(folder_name)
            print(f"🗑️ Pasta '{folder_name}' excluída do Google Drive.")

    except HttpError as error:
        print(f"❌ Erro ao excluir pastas 'New Folder': {error}")

    return deleted_folders
