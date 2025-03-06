import os
import streamlit as st
import io
import sqlite3
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Configuração do Google Drive
FLEETBD_FOLDER_ID = "1TeLkfzLxKCMR060z5kd8uNOXev1qLPda"  # ID correto da pasta no Google Drive
DB_FILE_NAME = "fleet_management.db"  # Nome do banco no Drive

def get_google_drive_service():
    """Autentica no Google Drive e retorna um serviço da API."""
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

        creds = Credentials.from_service_account_info(credentials_json, scopes=['https://www.googleapis.com/auth/drive'])
        return build("drive", "v3", credentials=creds)
    except Exception as e:
        st.error(f"❌ Erro na autenticação com o Google Drive: {e}")
        return None

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
