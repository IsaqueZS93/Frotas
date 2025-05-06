# C:\Users\Novaes Engenharia\frotas\fleet_main_app.py
# ------------------------------------------------------------------------------
#  Gestão de Frotas – App principal (Streamlit)
#  • Sincronização segura com Google Drive
#  • Criação automática do banco se nenhum backup existir
#  • Upload para o Drive só quando realmente houve alteração (`db_dirty`)
# ------------------------------------------------------------------------------

import Imports_fleet  # 🔹 garante que os caminhos do projeto sejam adicionados
import streamlit as st
import os
import json
import sqlite3
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# ------------------------------------------------------------------------------
# 1. Configurações básicas
# ------------------------------------------------------------------------------
load_dotenv()
st.set_page_config(page_title="Gestão de Frotas", layout="wide")
st.set_option("client.showErrorDetails", True)          # vê erros completos

SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
]

from backend.database.db_fleet import create_database, DB_PATH      # noqa: E402
DB_FILE_NAME = "fleet_management.db"
FLEETBD_FOLDER_ID = "1dPaautky1YLzYiH1IOaxgItu_GZSaxcO"

# ------------------------------------------------------------------------------
# 2. Serviço Google Drive
# ------------------------------------------------------------------------------
def get_google_drive_service():
    """Autentica e devolve serviço Drive v3 (ou None em falha)."""
    credentials_json = None
    if "GOOGLE_CREDENTIALS" in st.secrets:
        try:
            cred = st.secrets["GOOGLE_CREDENTIALS"]
            credentials_json = {k: cred[k] for k in cred.keys()}
            credentials_json["private_key"] = credentials_json["private_key"].replace(
                "\\n", "\n"
            )
        except Exception as e:
            st.error(f"⚠️ Erro nos secrets: {e}")

    if not credentials_json:
        json_txt = st.text_area("📥 Cole o JSON de serviço do Drive:", height=250)
        if st.button("🔑 Autenticar"):
            try:
                credentials_json = json.loads(json_txt)
                credentials_json["private_key"] = credentials_json["private_key"].replace(
                    "\\n", "\n"
                )
                st.success("✅ JSON validado!")
            except Exception as e:
                st.error(f"❌ JSON inválido: {e}")
                return None

    if not credentials_json:
        return None

    try:
        creds = Credentials.from_service_account_info(credentials_json, scopes=SCOPES)
        return build("drive", "v3", credentials=creds)
    except Exception as e:
        st.error(f"❌ Autenticação Drive falhou: {e}")
        return None


# ------------------------------------------------------------------------------
# 3. Sincronização: download / upload
# ------------------------------------------------------------------------------
def download_database_if_exists():
    """Baixa backup se houver no Drive. Salva em arquivo temporário, move depois."""
    service = get_google_drive_service()
    if not service:
        return

    query = f"name='{DB_FILE_NAME}' and '{FLEETBD_FOLDER_ID}' in parents"
    files = service.files().list(q=query, fields="files(id,size)").execute().get("files", [])
    if not files:
        st.warning("⚠️ Backup não encontrado no Drive – criaremos DB local vazio.")
        return

    file_id = files[0]["id"]
    request = service.files().get_media(fileId=file_id)

    tmp_path = DB_PATH + ".tmp"
    with open(tmp_path, "wb") as f_tmp:
        downloader = MediaIoBaseDownload(f_tmp, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

    os.replace(tmp_path, DB_PATH)          # troca atômica
    st.info("🔄 Banco de dados baixado do Drive.")


def upload_database():
    """Faz upload/atualização do banco para o Drive."""
    if not os.path.exists(DB_PATH):
        st.error("❌ Banco local não encontrado – upload abortado.")
        return

    service = get_google_drive_service()
    if not service:
        return

    q = f"name='{DB_FILE_NAME}' and '{FLEETBD_FOLDER_ID}' in parents"
    files = service.files().list(q=q, fields="files(id)").execute().get("files", [])

    media = MediaFileUpload(DB_PATH, resumable=True)
    try:
        if files:
            service.files().update(fileId=files[0]["id"], media_body=media).execute()
            st.sidebar.success("☁️ Backup atualizado no Drive!")
        else:
            meta = {"name": DB_FILE_NAME, "parents": [FLEETBD_FOLDER_ID]}
            service.files().create(body=meta, media_body=media).execute()
            st.sidebar.success("☁️ Backup criado no Drive!")
    except Exception as e:
        st.sidebar.error(f"❌ Falha no upload: {e}")


# ------------------------------------------------------------------------------
# 4. Garantia de existência do banco local
# ------------------------------------------------------------------------------
download_database_if_exists()
if not os.path.exists(DB_PATH):
    create_database()                       # cria vazio (todas as tabelas)

# ------------------------------------------------------------------------------
# 5. Estado da sessão
# ------------------------------------------------------------------------------
st.session_state.setdefault("authenticated", False)
st.session_state.setdefault("user_type", None)
st.session_state.setdefault("user_name", None)
st.session_state.setdefault("db_dirty", False)   # ← marca se houve escrita

# ------------------------------------------------------------------------------
# 6. Estilo
# ------------------------------------------------------------------------------
st.markdown(
    """
    <style>
      body {background:#E3F2FD;color:#0D47A1;font-family:Arial;}
      .stButton>button {background:#42A5F5;color:white;border-radius:10px;padding:10px;width:100%;}
      .stButton>button:hover {background:#1976D2;}
      input,textarea,select {background:#FFF;border-radius:8px;padding:8px;border:1px solid #90CAF9;}
      label,h1,h2,h3,h4,h5,h6 {font-weight:bold;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------------------
# 7. Upload manual se DB ainda não existe (caso raro)
# ------------------------------------------------------------------------------
if not os.path.exists(DB_PATH):
    st.sidebar.error("❌ Banco não reconhecido! Faça upload do .db e reinicie.")
    up = st.sidebar.file_uploader("Escolha um .db", type=["db"])
    if up:
        path_tmp = DB_PATH + ".uploaded"
        with open(path_tmp, "wb") as f:
            f.write(up.getbuffer())
        os.replace(path_tmp, DB_PATH)
        st.sidebar.success("✅ Banco substituído – reinicie o app.")
    st.stop()

# ------------------------------------------------------------------------------
# 8. Importação das telas (depois do DB existir)
# ------------------------------------------------------------------------------
from frontend.screens.Screen_Login import login_screen         # noqa: E402
from frontend.screens.Screen_User_Create import user_create_screen      # noqa: E402
from frontend.screens.Screen_User_List_Edit import user_list_edit_screen  # noqa: E402
from frontend.screens.Screen_User_Control import user_control_screen    # noqa: E402
from frontend.screens.Screen_Veiculo_Create import veiculo_create_screen  # noqa: E402
from frontend.screens.Screen_Veiculo_List_Edit import veiculo_list_edit_screen  # noqa: E402
from frontend.screens.Screen_Checklists_Create import checklist_create_screen    # noqa: E402
from frontend.screens.Screen_Checklist_lists import checklist_list_screen        # noqa: E402
from frontend.screens.Screen_Abastecimento_Create import abastecimento_create_screen  # noqa: E402
from frontend.screens.Screen_Abastecimento_List_Edit import abastecimento_list_edit_screen  # noqa: E402
from frontend.screens.Screen_Dash import screen_dash            # noqa: E402
from frontend.screens.Screen_IA import screen_ia                # noqa: E402

# ------------------------------------------------------------------------------
# 9. Tela de Login
# ------------------------------------------------------------------------------
if not st.session_state["authenticated"]:
    info = login_screen()
    if info:
        st.session_state.update(
            authenticated=True,
            user_name=info["user_name"],
            user_type=info["user_type"],
        )
        st.experimental_rerun()

# ------------------------------------------------------------------------------
# 10. Menu lateral (usuário autenticado)
# ------------------------------------------------------------------------------
st.sidebar.title("☰ Menu")

if st.session_state["authenticated"]:
    st.sidebar.write(f"👤 **Usuário:** {st.session_state['user_name']}")
    st.sidebar.write(f"🔑 **Permissão:** {st.session_state['user_type']}")

    if st.session_state["user_type"] == "OPE":
        options = ["Gerenciar Perfil", "Novo Checklist", "Novo Abastecimento", "Logout"]
    else:
        options = [
            "Gerenciar Perfil", "Cadastrar Usuário", "Gerenciar Usuários",
            "Cadastrar Veículo", "Gerenciar Veículos", "Novo Checklist",
            "Gerenciar Checklists", "Novo Abastecimento", "Gerenciar Abastecimentos",
            "Dashboards", "Chatbot IA 🤖", "Logout",
        ]
        # backup manual para ADMIN
        st.sidebar.subheader("☁️ Backup Drive")
        if st.sidebar.button("Enviar backup agora"):
            upload_database()

        # download automático do .db
        with open(DB_PATH, "rb") as f_db:
            st.sidebar.download_button(
                label="📥 Baixar backup .db",
                data=f_db,
                file_name=DB_FILE_NAME,
                mime="application/octet-stream",
            )

    # navegação
    choice = st.sidebar.radio("Escolha:", options, key="menu_option")

    # ----------------------------------------------------------------------------
    # 10a. Roteamento de telas
    # ----------------------------------------------------------------------------
    if choice == "Gerenciar Perfil":
        user_control_screen()
    elif choice == "Cadastrar Usuário":
        user_create_screen(); st.session_state["db_dirty"] = True
    elif choice == "Gerenciar Usuários":
        user_list_edit_screen()
    elif choice == "Cadastrar Veículo":
        veiculo_create_screen(); st.session_state["db_dirty"] = True
    elif choice == "Gerenciar Veículos":
        veiculo_list_edit_screen()
    elif choice == "Novo Checklist":
        checklist_create_screen(); st.session_state["db_dirty"] = True
    elif choice == "Gerenciar Checklists":
        checklist_list_screen()
    elif choice == "Novo Abastecimento":
        abastecimento_create_screen(); st.session_state["db_dirty"] = True
    elif choice == "Gerenciar Abastecimentos":
        abastecimento_list_edit_screen()
    elif choice == "Dashboards":
        screen_dash()
    elif choice == "Chatbot IA 🤖":
        screen_ia()
    elif choice == "Logout":
        st.session_state.clear()
        st.success("✅ Saiu do sistema!")
        st.experimental_rerun()

    # ----------------------------------------------------------------------------
    # 10b. Upload manual de arquivo .db (qualquer usuário autenticado)
    # ----------------------------------------------------------------------------
    st.sidebar.subheader("📤 Substituir banco local (.db)")
    up_file = st.sidebar.file_uploader("Escolha um .db", type=["db"])
    if up_file:
        tmp = DB_PATH + ".user_up"
        with open(tmp, "wb") as f:
            f.write(up_file.getbuffer())
        os.replace(tmp, DB_PATH)
        st.sidebar.success("✅ Banco substituído – reinicie o app.")
        st.stop()

    # ----------------------------------------------------------------------------
    # 10c. Sincronização automática se houve alterações
    # ----------------------------------------------------------------------------
    if st.session_state["db_dirty"]:
        upload_database()
        st.session_state["db_dirty"] = False
