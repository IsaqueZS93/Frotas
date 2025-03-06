import Imports_fleet  # 🔹 Garante que todos os caminhos do projeto sejam adicionados corretamente
import streamlit as st
import os
import time
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

# 🔹 Função para listar todos os arquivos dentro da nuvem Streamlit
def list_all_files():
    """Lista todos os arquivos e diretórios disponíveis no ambiente da nuvem Streamlit."""
    files_found = []
    for root, dirs, files in os.walk("/"):
        for file in files:
            file_path = os.path.join(root, file)
            files_found.append(file_path)
    return files_found

# 🔹 Caminho do banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FOLDER = os.path.join(BASE_DIR, "backend", "database")
DB_PATH = os.path.join(DB_FOLDER, "fleet_management.db")

# 🔹 Criar diretório se não existir
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER, exist_ok=True)

# 🔹 Debug: Mostrar caminho do banco
st.write(f"📂 Tentando localizar o banco de dados em: `{DB_PATH}`")

# 🔹 Criar banco de dados se não existir
if not os.path.exists(DB_PATH):
    st.warning("⚠️ Banco de dados não encontrado! Criando um novo banco...")
    create_database()

# 🔹 Verificar se conseguimos abrir o banco
if os.path.exists(DB_PATH):
    st.success(f"✅ Banco de dados encontrado em: `{DB_PATH}`")
else:
    st.error("❌ Banco de dados não encontrado! Certifique-se de que o banco foi salvo corretamente.")

# 🔹 Listar todos os arquivos na nuvem para diagnóstico
st.subheader("🕵️ Arquivos encontrados no sistema:")
files_list = list_all_files()

# 🔹 Exibir arquivos completos
if files_list:
    for file in files_list:
        st.write(file)
else:
    st.error("❌ Nenhum arquivo encontrado no sistema!")

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

    # 🔹 Exibir botão de backup e download apenas para ADMINs
    if st.session_state.get("user_type") == "ADMIN":
        st.sidebar.subheader("⚙️ Configurações Avançadas")

        # 🔹 Download direto do banco
        if os.path.exists(DB_PATH):
            with open(DB_PATH, "rb") as file:
                st.sidebar.download_button(
                    label="📥 Baixar Banco de Dados",
                    data=file,
                    file_name="fleet_management.db",
                    mime="application/octet-stream"
                )
        else:
            st.sidebar.error("❌ Banco de dados não encontrado para download!")

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
