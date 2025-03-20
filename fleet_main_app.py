import Imports_fleet  # 🔹 Garante que todos os caminhos do projeto sejam adicionados corretamente
import streamlit as st
import os
import io
import json
import sqlite3
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# Carregar variáveis de ambiente (útil para ambientes locais)
load_dotenv()

# Definição dos escopos de acesso atualizados (gerenciar, ler e acessar metadados)
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.metadata.readonly"
]

# Configurações do banco de dados
from backend.database.db_fleet import create_database, DB_PATH
DB_FILE_NAME = "fleet_management.db"  # Nome correto do banco de dados

# ID da pasta para o banco de dados no Google Drive
FLEETBD_FOLDER_ID = "1dPaautky1YLzYiH1IOaxgItu_GZSaxcO"

##########################################
# FUNÇÕES DE INTEGRAÇÃO COM O GOOGLE DRIVE #
##########################################

def get_google_drive_service():
    """
    Autentica no Google Drive e retorna um serviço da API.
    """
    st.write("🔍 Tentando autenticação no Google Drive...")
    credentials_json = None

    # Tenta obter credenciais dos segredos do Streamlit (útil na nuvem)
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

    # Se não encontrar, solicita o JSON manualmente
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

    if not credentials_json:
        st.error("❌ Nenhuma credencial válida encontrada. Autenticação abortada.")
        return None

    try:
        creds = Credentials.from_service_account_info(credentials_json, scopes=SCOPES)
        st.success("✅ Autenticado via Conta de Serviço com sucesso!")
        return build("drive", "v3", credentials=creds)
    except Exception as e:
        st.error("❌ Erro ao autenticar no Google Drive: " + str(e))
        return None

def download_database():
    """Baixa o banco de dados do Google Drive e substitui o arquivo local."""
    service = get_google_drive_service()
    if not service:
        return

    existing_files = service.files().list(
        q=f"name='{DB_FILE_NAME}' and '{FLEETBD_FOLDER_ID}' in parents",
        fields="files(id)"
    ).execute().get("files", [])

    if not existing_files:
        st.warning("⚠️ Nenhum backup encontrado no Google Drive. Será criado um novo banco local.")
        return

    file_id = existing_files[0]["id"]
    request = service.files().get_media(fileId=file_id)

    with open(DB_PATH, "wb") as file:
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    st.info("🔄 Banco de dados baixado do Google Drive.")

def upload_database():
    """Envia ou atualiza o banco de dados no Google Drive na pasta definida."""
    if not os.path.exists(DB_PATH):
        st.error("❌ Erro: O banco de dados não foi encontrado localmente. Nenhum upload foi realizado.")
        return

    service = get_google_drive_service()
    if not service:
        return

    file_metadata = {
        "name": DB_FILE_NAME,
        "parents": [FLEETBD_FOLDER_ID]
    }
    media = MediaFileUpload(DB_PATH, resumable=True)

    existing_files = service.files().list(
        q=f"name='{DB_FILE_NAME}' and '{FLEETBD_FOLDER_ID}' in parents",
        fields="files(id)"
    ).execute().get("files", [])

    try:
        if existing_files:
            file_id = existing_files[0]["id"]
            service.files().update(fileId=file_id, media_body=media).execute()
            st.sidebar.success("✅ Banco de dados atualizado no Google Drive!")
        else:
            service.files().create(body=file_metadata, media_body=media).execute()
            st.sidebar.success("✅ Banco de dados salvo no Google Drive pela primeira vez!")
    except Exception as e:
        st.sidebar.error("❌ Erro ao enviar o banco de dados: " + str(e))

##########################################
# FIM DAS FUNÇÕES DE INTEGRAÇÃO COM O DRIVE #
##########################################

# IMPORTAÇÃO DAS TELAS DO SISTEMA
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

# Configuração inicial do Streamlit com tema azul claro
st.set_page_config(page_title="Gestão de Frotas", layout="wide")

# Estilização personalizada para um tema azul claro
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

# Chamada para baixar o banco de dados do Google Drive na inicialização
download_database()

# Inicializa as variáveis de estado
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_type" not in st.session_state:
    st.session_state["user_type"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None

############################################
# Verificação do Banco de Dados
############################################
if not os.path.exists(DB_PATH):
    st.sidebar.warning("❌ Banco de dados não reconhecido! Faça o upload de um novo banco de dados para prosseguir.")
    uploaded_file = st.sidebar.file_uploader("Escolha um arquivo (.db)", type=["db"])
    if uploaded_file is not None:
        new_db_path = os.path.join(os.path.dirname(DB_PATH), "fleet_management_uploaded.db")
        with open(new_db_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        os.replace(new_db_path, DB_PATH)
        st.sidebar.success("✅ Banco de dados atualizado com sucesso! Reinicie o sistema.")
        st.stop()
    else:
        st.info("Por favor, faça o upload do banco de dados para prosseguir.")
        st.stop()

############################################
# Fluxo do Sistema
############################################

# Tela de Login (com o banco de dados já atualizado a partir do Google Drive)
if not st.session_state["authenticated"]:
    user_info = login_screen()
    if user_info:
        st.session_state["authenticated"] = True
        st.session_state["user_name"] = user_info["user_name"]
        st.session_state["user_type"] = user_info["user_type"]
        st.experimental_rerun()
else:
    # Após cada interação, atualiza automaticamente o backup no Google Drive.
    upload_database()
    
    st.sidebar.title("⚙️ Configuração do Banco de Dados")
    
    st.sidebar.subheader("📤 Enviar um novo banco de dados")
    uploaded_file = st.sidebar.file_uploader("Escolha um arquivo (.db)", type=["db"])
    if uploaded_file is not None:
        new_db_path = os.path.join(os.path.dirname(DB_PATH), "fleet_management_uploaded.db")
        with open(new_db_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        os.replace(new_db_path, DB_PATH)
        st.sidebar.success("✅ Banco de dados atualizado com sucesso! Reinicie o sistema.")
        st.stop()

    st.sidebar.subheader("☁️ Backup no Google Drive")
    if st.sidebar.button("Salvar banco de dados na nuvem"):
        upload_database()

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

    if st.session_state.get("user_type") == "OPE":
        menu_options = ["Gerenciar Perfil", "Novo Checklist", "Novo Abastecimento", "Logout"]
    else:  # ADMIN
        menu_options = [
            "Gerenciar Perfil", "Cadastrar Usuário", "Gerenciar Usuários", "Cadastrar Veículo",
            "Gerenciar Veículos", "Novo Checklist", "Gerenciar Checklists", "Novo Abastecimento",
            "Gerenciar Abastecimentos", "Dashboards", "Chatbot IA 🤖", "Logout"
        ]
    menu_option = st.sidebar.radio("🚗 **Menu Principal**", menu_options)

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
