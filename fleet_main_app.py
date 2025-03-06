import Imports_fleet  # 🔹 Garante que todos os caminhos do projeto sejam adicionados corretamente
import streamlit as st
import os
import time
import subprocess
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

# Caminho correto do banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "backend", "database", "fleet_management.db")

# Variáveis de ambiente para acesso ao GitHub
GITHUB_REPO = os.getenv("GITHUB_REPO")  # Exemplo: "seu-usuario/FleetManagement"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# 🔹 Criar banco de dados se não existir
if not os.path.exists(DB_PATH):
    st.warning("⚠️ Banco de dados não encontrado! Criando um novo banco...")
    create_database()

# 🔹 Função para enviar o banco para o GitHub
def push_to_github():
    """Atualiza o banco de dados no GitHub automaticamente"""
    if not os.path.exists(DB_PATH):
        st.error("❌ Banco de dados não encontrado para upload!")
        return False

    try:
        # Configurar repositório remoto usando o token
        repo_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"

        # Debug: Verificar se o banco realmente existe antes do upload
        st.write(f"📂 Banco de dados localizado em: {DB_PATH}")

        # Executa os comandos Git para commit e push
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

        # 🔹 Verificar se o banco realmente existe antes de exibir o botão de upload
        if os.path.exists(DB_PATH):
            if st.sidebar.button("📤 Atualizar Banco no GitHub"):
                push_to_github()
        else:
            st.sidebar.error("❌ Banco de dados não encontrado para upload!")

    # 🔹 Menu lateral para navegação
    st.sidebar.title("Gestão de Frotas 🚛")
    menu_option = st.sidebar.radio(
        "Navegação",
        [
            "Gerenciar Perfil", "Cadastrar Usuário", "Gerenciar Usuários", "Cadastrar Veículo", "Gerenciar Veículos",
            "Novo Checklist", "Gerenciar Checklists", "Novo Abastecimento", "Gerenciar Abastecimentos", "Dashboards", 
            "Chatbot IA 🤖", "Logout"
        ]
    )

    if menu_option == "Gerenciar Perfil":
        user_control_screen()
    elif menu_option == "Cadastrar Usuário" and st.session_state["user_type"] == "ADMIN":
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
        screen_ia()  # Chama a tela do chatbot IA
    elif menu_option == "Logout":
        # 🔹 Botão de logout: Reseta sessão e recarrega a página
        st.session_state["authenticated"] = False
        st.session_state["user_id"] = None
        st.session_state["user_type"] = None
        st.session_state["user_name"] = None
        st.session_state["show_welcome"] = True
        st.success("Você saiu do sistema. Redirecionando para a tela de login... 🔄")
        st.rerun()
    else:
        st.warning("Você não tem permissão para acessar esta página.")
