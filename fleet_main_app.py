import Imports_fleet  # 🔹 Garante que todos os caminhos do projeto sejam adicionados corretamente
import streamlit as st
import os
import time
import subprocess
import sqlite3
from backend.database.db_fleet import create_database

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

# Configuração da página e ocultação do menu padrão do Streamlit
st.set_page_config(page_title="Gestão de Frotas", layout="wide")

hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

# 🔹 Caminho do banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "backend", "database", "fleet_management.db")

# 🔹 Debug: Mostrar caminho do banco
st.write(f"📂 Tentando localizar o banco de dados em: `{DB_PATH}`")

# 🔹 Criar banco de dados se não existir
if not os.path.exists(DB_PATH):
    st.warning("⚠️ Banco de dados não encontrado! Criando um novo banco...")
    create_database()

# 🔹 Verificar se conseguimos abrir o banco
try:
    with open(DB_PATH, "rb") as file:
        st.success("✅ Banco de dados encontrado e pronto para download.")
except FileNotFoundError:
    st.error("❌ Banco de dados não encontrado! Ele pode estar rodando em memória.")
    # Tentar salvar do SQLite para um arquivo
    try:
        conn = sqlite3.connect(":memory:")
        backup_conn = sqlite3.connect(DB_PATH)
        conn.backup(backup_conn)
        backup_conn.close()
        conn.close()
        st.success("✅ Banco de dados exportado para um arquivo antes do backup!")
    except Exception as e:
        st.error(f"⚠️ Falha ao exportar o banco de dados: {e}")

# 🔹 Carregar credenciais do GitHub do secrets.toml
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", None)
GITHUB_REPO = st.secrets.get("GITHUB_REPO", None)

if not GITHUB_TOKEN or not GITHUB_REPO:
    st.error("⚠️ Erro: Token do GitHub ou Repositório não configurado nos Secrets do Streamlit!")

# 🔹 Função para enviar o banco para o GitHub
def push_to_github():
    """Atualiza o banco de dados no GitHub automaticamente"""
    if not os.path.exists(DB_PATH):
        st.error("❌ Banco de dados não encontrado para upload!")
        return False

    try:
        repo_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"

        subprocess.run(["git", "config", "--global", "user.email", "streamlit@fleet.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "Streamlit AutoCommit"], check=True)
        subprocess.run(["git", "add", DB_PATH], check=True)
        subprocess.run(["git", "commit", "-m", "🔄 Atualização automática do banco de dados"], check=True)
        subprocess.run(["git", "push", repo_url, "main"], check=True)

        st.success("✅ Banco de dados atualizado no GitHub com sucesso!")
        return True

    except subprocess.CalledProcessError as e:
        st.error(f"❌ Erro ao enviar para o GitHub: {e}")
        return False

# 🔹 Inicializa a sessão do usuário
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_type" not in st.session_state:
    st.session_state["user_type"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None
if "show_welcome" not in st.session_state:
    st.session_state["show_welcome"] = True

# 🔹 Se o usuário NÃO estiver autenticado, exibir tela de login
if not st.session_state["authenticated"]:
    user_name = login_screen()
    
    if user_name:
        st.session_state["user_name"] = user_name
        st.rerun()
else:
    # 🔹 Exibir usuário logado no menu lateral
    st.sidebar.write(f"👤 Usuário logado: {st.session_state.get('user_name', 'Desconhecido')}")
    st.sidebar.write(f"🔑 Permissão: {st.session_state.get('user_type', 'Desconhecido')}")

    # 🔹 Exibir botão de backup apenas para ADMINs
    if st.session_state.get("user_type") == "ADMIN":
        st.sidebar.subheader("⚙️ Configurações Avançadas")
        if os.path.exists(DB_PATH):
            if st.sidebar.button("📤 Atualizar Banco no GitHub"):
                push_to_github()
        else:
            st.sidebar.error("❌ Banco de dados não encontrado para upload!")

    # 🔹 Menu lateral para navegação
    menu_option = st.sidebar.radio(
        "Navegação",
        ["Gerenciar Perfil", "Cadastrar Usuário", "Gerenciar Usuários", "Cadastrar Veículo", 
         "Gerenciar Veículos", "Novo Checklist", "Gerenciar Checklists", "Novo Abastecimento",
         "Gerenciar Abastecimentos", "Dashboards", "Chatbot IA 🤖", "Logout"]
    )

    if menu_option == "Gerenciar Perfil":
        user_control_screen()
    elif menu_option == "Logout":
        st.session_state["authenticated"] = False
        st.session_state["user_id"] = None
        st.session_state["user_type"] = None
        st.session_state["user_name"] = None
        st.session_state["show_welcome"] = True
        st.success("Você saiu do sistema. Redirecionando para a tela de login... 🔄")
        st.rerun()
