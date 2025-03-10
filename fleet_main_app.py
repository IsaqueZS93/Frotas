import os
import io
import json
import sqlite3
import requests
import streamlit as st
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# =============================================================================
# CONFIGURAÇÕES DO GOOGLE DRIVE
# =============================================================================
# ID da pasta no Google Drive onde o banco de dados será armazenado
FOLDER_ID = "1dPaautky1YLzYiH1IOaxgItu_GZSaxcO"

# Caminho para o arquivo de credenciais do service account (JSON)
SERVICE_ACCOUNT_FILE = "path/to/service_account.json"  # ATUALIZE para o caminho correto

SCOPES = ["https://www.googleapis.com/auth/drive"]

def get_google_drive_service():
    """Inicializa e retorna o serviço da API do Google Drive."""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("drive", "v3", credentials=creds)
    return service

def upload_db_to_drive(file_path, folder_id=FOLDER_ID):
    """Faz o upload do arquivo do banco de dados para a pasta especificada no Google Drive."""
    try:
        service = get_google_drive_service()
        file_metadata = {"name": os.path.basename(file_path), "parents": [folder_id]}
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(
            body=file_metadata, media_body=media, fields="id, webViewLink"
        ).execute()
        st.sidebar.info(f"Banco de dados salvo no Drive: {file.get('webViewLink')}")
        return file.get("webViewLink")
    except Exception as e:
        st.error(f"❌ Erro ao fazer upload do banco: {e}")
        return None

def download_db_from_drive(file_name, folder_id=FOLDER_ID, dest_path="fleet_management.db"):
    """Faz o download do arquivo do banco de dados da pasta do Google Drive para o caminho local."""
    try:
        service = get_google_drive_service()
        # Procura o arquivo pelo nome na pasta especificada
        query = f"'{folder_id}' in parents and name = '{file_name}' and trashed = false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get("files", [])
        if not files:
            st.error("❌ Banco de dados não encontrado no Google Drive.")
            return None
        file_id = files[0]["id"]
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(dest_path, "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.close()
        st.sidebar.info("Banco de dados baixado do Google Drive.")
        return dest_path
    except Exception as e:
        st.error(f"❌ Erro ao fazer download do banco: {e}")
        return None

# =============================================================================
# IMPORTS E CONFIGURAÇÕES DO SISTEMA
# =============================================================================
import Imports_fleet  # 🔹 Garante que todos os caminhos do projeto sejam adicionados corretamente
from backend.database.db_fleet import create_database, DB_PATH  # Supondo que DB_PATH seja definido lá
from frontend.screens.Screen_Login import login_screen
from frontend.screens.Screen_User_Create import user_create_screen
from frontend.screens.Screen_User_List_Edit import user_list_edit_screen
from frontend.screens.Screen_User_Control import user_control_screen
from frontend.screens.Screen_Veiculo_Create import veiculo_create_screen
from frontend.screens.Screen_Veiculo_List_Edit import veiculo_list_edit_screen
from frontend.screens.Screen_Checklists_Create import checklist_create_screen
from frontend.screens.Screen_Checklist_lists import checklist_list_screen
from frontend.screens.Screen_Abastecimento_Create import abastecimento_create_screen
from frontend.screens.Screen_Abastecimento_List_Edit import abastecimento_list_edit_screen
from frontend.screens.Screen_Dash import screen_dash
from frontend.screens.Screen_IA import screen_ia  # ✅ Importa a tela do chatbot IA

# Se preferir, defina DB_PATH para apontar para um diretório específico
# Por exemplo, salvando o arquivo na raiz do projeto com o nome fleet_management.db:
DB_PATH = os.path.join(os.getcwd(), "fleet_management.db")

# =============================================================================
# CONFIGURAÇÃO INICIAL DO STREAMLIT
# =============================================================================
st.set_page_config(page_title="Gestão de Frotas", layout="wide")

custom_style = """
    <style>
    body {
        background-color: #E3F2FD;
        color: #0D47A1;
        font-family: Arial, sans-serif;
    }
    .stButton>button {
        background-color: #42A5F5;
        color: white;
        border-radius: 10px;
        padding: 10px;
        width: 100%;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
    }
    .stButton>button:hover {
        background-color: #1976D2;
    }
    input, textarea, select {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 8px;
        border: 1px solid #90CAF9;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
    }
    label, h1, h2, h3, h4, h5, h6 {
        font-weight: bold;
    }
    </style>
"""
st.markdown(custom_style, unsafe_allow_html=True)

# =============================================================================
# INICIALIZAÇÃO DAS VARIÁVEIS DE ESTADO
# =============================================================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_type" not in st.session_state:
    st.session_state["user_type"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None

# =============================================================================
# UPLOAD E GERENCIAMENTO DO BANCO DE DADOS
# =============================================================================
st.sidebar.title("⚙️ Configuração do Banco de Dados")
st.sidebar.subheader("📤 Enviar um novo banco de dados")

uploaded_file = st.sidebar.file_uploader("Escolha um arquivo (.db)", type=["db"])

if uploaded_file is not None:
    new_db_path = os.path.join(os.path.dirname(DB_PATH), "fleet_management_uploaded.db")
    with open(new_db_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    # Substituir o banco de dados principal pelo novo
    os.replace(new_db_path, DB_PATH)
    # Após atualizar o arquivo local, faz o upload para o Google Drive
    upload_db_to_drive(DB_PATH)
    st.sidebar.success("✅ Banco de dados atualizado com sucesso! Reinicie o sistema.")
    st.stop()

# Se o banco de dados não existir localmente, tenta baixá-lo do Google Drive
if not os.path.exists(DB_PATH):
    download_db_from_drive("fleet_management.db", dest_path=DB_PATH)
    if not os.path.exists(DB_PATH):
        st.sidebar.error("❌ Banco de dados não encontrado! O sistema não pode continuar sem um banco válido.")
        st.stop()

# =============================================================================
# TELA DE LOGIN E NAVEGAÇÃO
# =============================================================================
if not st.session_state["authenticated"]:
    user_info = login_screen()
    if user_info:
        st.session_state["authenticated"] = True
        st.session_state["user_name"] = user_info["user_name"]
        st.session_state["user_type"] = user_info["user_type"]
        st.rerun()
else:
    st.sidebar.write(f"👤 **Usuário:** {st.session_state.get('user_name', 'Desconhecido')}")
    st.sidebar.write(f"🔑 **Permissão:** {st.session_state.get('user_type', 'Desconhecido')}")
    if st.session_state.get("user_type") == "ADMIN":
        st.sidebar.subheader("⚙️ Configurações Avançadas")
        with open(DB_PATH, "rb") as file:
            st.sidebar.download_button(
                label="📥 Baixar Backup do Banco",
                data=file,
                file_name="fleet_management.db",
                mime="application/octet-stream"
            )
    menu_option = st.sidebar.radio(
        "🚗 **Menu Principal**",
        ["Gerenciar Perfil", "Cadastrar Usuário", "Gerenciar Usuários", "Cadastrar Veículo",
         "Gerenciar Veículos", "Novo Checklist", "Gerenciar Checklists", "Novo Abastecimento",
         "Gerenciar Abastecimentos", "Dashboards", "Chatbot IA 🤖", "Logout"]
    )
    if menu_option == "Gerenciar Perfil":
        user_control_screen()
    elif menu_option == "Cadastrar Usuário":
        user_create_screen()
    elif menu_option == "Gerenciar Usuários" and st.session_state["user_type"] == "ADMIN":
        user_list_edit_screen()
    elif menu_option == "Cadastrar Veículo" and st.session_state["user_type"] == "ADMIN":
        veiculo_create_screen()
    elif menu_option == "Gerenciar Veículos" and st.session_state["user_type"] == "ADMIN":
        veiculo_list_edit_screen()
    elif menu_option == "Novo Checklist":
        checklist_create_screen()
    elif menu_option == "Gerenciar Checklists" and st.session_state["user_type"] == "ADMIN":
        checklist_list_screen()
    elif menu_option == "Novo Abastecimento":
        abastecimento_create_screen()
    elif menu_option == "Gerenciar Abastecimentos" and st.session_state["user_type"] == "ADMIN":
        abastecimento_list_edit_screen()
    elif menu_option == "Dashboards" and st.session_state["user_type"] == "ADMIN":
        screen_dash()
    elif menu_option == "Chatbot IA 🤖":
        screen_ia()
    elif menu_option == "Logout":
        st.session_state.clear()
        st.success("✅ Você saiu do sistema! Redirecionando... 🔄")
        st.rerun()
